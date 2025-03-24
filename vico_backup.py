#!/root/venv_librosa/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import argparse
import librosa
import cv2
import tempfile
import shutil
import multiprocessing
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from tqdm import tqdm


# ====== Audioanalyse: Frequenzbereiche extrahieren ======
def analyze_audio_timevarying(audio_file, hop_length=2048, sr_desired=None):
    y, sr = librosa.load(audio_file, sr=sr_desired, mono=True)
    S = np.abs(librosa.stft(y, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=S.shape[0] * 2 - 2)

    low_mask = freqs < 200
    mid_mask = (freqs >= 200) & (freqs < 2000)
    high_mask = freqs >= 2000

    n_frames = S.shape[1]
    frame_duration = hop_length / sr
    data = []
    for i in range(n_frames):
        spectrum = S[:, i]
        low_energy = np.sum(spectrum[low_mask])
        mid_energy = np.sum(spectrum[mid_mask])
        high_energy = np.sum(spectrum[high_mask])
        total = low_energy + mid_energy + high_energy
        if total == 0:
            lr, mr, hr = 0.0, 0.0, 0.0
        else:
            lr = low_energy / total
            mr = mid_energy / total
            hr = high_energy / total
        time_for_frame = i * frame_duration
        data.append((time_for_frame, lr, mr, hr))
    return data


# ====== Zeitpunkt-basierte Frequenzverteilung abrufen ======
def get_freq_ratios_at_time(t, freq_data):
    if t <= freq_data[0][0]:
        return freq_data[0][1:]
    if t >= freq_data[-1][0]:
        return freq_data[-1][1:]
    for i in range(len(freq_data) - 1):
        t0 = freq_data[i][0]
        t1 = freq_data[i + 1][0]
        if t0 <= t < t1:
            return freq_data[i][1:]
    return freq_data[-1][1:]


# ====== Hauptframe-Manipulationsfunktion mit Effekten ======
def dynamic_color_frame_from_array(args):
    (frame, t, freq_data, factor, zoom_factor, shake, shake_intensity, shake_range,
     glitch, glitch_intensity, glitch_range, zoom_range, debug) = args

    lr, mr, hr = get_freq_ratios_at_time(t, freq_data)

    # Farbe
    frame = frame.astype(np.float32)
    frame[..., 2] *= (1.0 + lr * factor)
    frame[..., 1] *= (1.0 + mr * factor)
    frame[..., 0] *= (1.0 + hr * factor)
    np.clip(frame, 0, 255, out=frame)

    # Zoom
    if zoom_factor > 0 and any(start <= t <= (end if end else t + 1) for (start, end) in zoom_range):
        volume_factor = lr + mr + hr
        pulsation = 0.98 + 0.04 * np.sin(2 * np.pi * t)
        zoom = 1 + volume_factor * zoom_factor * pulsation
        h, w = frame.shape[:2]
        resized = cv2.resize(frame, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_LINEAR)
        cx, cy = resized.shape[1] // 2, resized.shape[0] // 2
        frame = resized[cy - h // 2:cy + h // 2, cx - w // 2:cx + w // 2]

    # Shake
    if shake and any(start <= t <= (end if end else t + 1) for (start, end) in shake_range):
        offset_x = int(np.sin(t * 25) * shake_intensity)
        offset_y = int(np.cos(t * 33) * shake_intensity)
        M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        frame = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))

    # Glitch
    if glitch and any(start <= t <= (end if end else t + 1) for (start, end) in glitch_range):
        for _ in range(3):
            h, w = frame.shape[:2]
            band_height = np.random.randint(1, 10)
            y = np.random.randint(0, h - band_height)
            dx = np.random.randint(-glitch_intensity, glitch_intensity)
            frame[y:y + band_height] = np.roll(frame[y:y + band_height], dx, axis=1)

    # Debug Overlay
    if debug:
        overlay = frame.copy()
        alpha = 0.4
        overlay[:] = (0, 0, 255)
        frame = cv2.addWeighted(frame.astype(np.uint8), 1 - alpha, overlay, alpha, 0)

    return frame.astype(np.uint8)


# ====== Loop- und PingPong Builder ======
def build_loop_sequence(video_files, target_duration, reverse):
    loop_sequence = []
    for v in video_files:
        clip = VideoFileClip(v)
        if reverse:
            loop_sequence.append(clip)
            loop_sequence.append(clip.fx(vfx.time_mirror))
        else:
            loop_sequence.append(clip)
    clips = []
    total = 0
    while total < target_duration:
        for c in loop_sequence:
            clips.append(c)
            total += c.duration
            if total >= target_duration:
                break
    return concatenate_videoclips(clips, method="compose")


# ====== Hauptprozess ======
def process_clips_with_dynamic_audiofreq(video_files, audio_file, output_file, fps, factor, reverse, fast, debug,
                                         zoom_factor, zoom_ranges, shake, shake_intensity, shake_ranges,
                                         glitch, glitch_intensity, glitch_ranges, crossfade, crossfade_mode):
    freq_data = analyze_audio_timevarying(audio_file)
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration

    combined_clip = build_loop_sequence(video_files, audio_duration, reverse)

    with tempfile.TemporaryDirectory() as tmpdir:
        times = np.arange(0, audio_duration, 1.0 / fps)
        args = [(combined_clip.get_frame(t), t, freq_data, factor, zoom_factor,
                 shake, shake_intensity, shake_ranges,
                 glitch, glitch_intensity, glitch_ranges,
                 zoom_ranges, debug) for t in times]

        with multiprocessing.Pool() as pool:
            frames = list(tqdm(pool.imap(dynamic_color_frame_from_array, args), total=len(args), desc="Rendering frames"))

        print("📦 Speichern...")
        frame_paths = []
        for i, f in enumerate(frames):
            path = os.path.join(tmpdir, f"frame_{i:05d}.png")
            cv2.imwrite(path, f)
            frame_paths.append(path)

        ffmpeg_cmd = f"ffmpeg -y -framerate {fps} -i {tmpdir}/frame_%05d.png -i {audio_file} -c:v libx264 -preset fast -crf 18 -c:a aac -shortest {output_file}"
        os.system(ffmpeg_cmd)


# ====== CLI-Parser und Ausführung ======
if __name__ == "__main__":
    def parse_timerange(s):
        if not s:
            return []
        start_str, end_str = s.split("-")
        def to_sec(t):
            if t in ("0", "0.0", "0:00", ""):
                return 0.0
            parts = list(map(float, t.split(":")))
            return sum(p * 60 ** (len(parts) - i - 1) for i, p in enumerate(parts))
        return [(to_sec(start_str), to_sec(end_str) if end_str != "0" else None)]

    parser = argparse.ArgumentParser()
    parser.add_argument("output_file")
    parser.add_argument("audio_file")
    parser.add_argument("video_files", nargs="+")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--factor", type=float, default=3.0)
    parser.add_argument("--zoom-factor", type=float, default=0.0)
    parser.add_argument("--zoom-range", type=parse_timerange, default=[])
    parser.add_argument("--shake", action="store_true")
    parser.add_argument("--shake-intensity", type=int, default=0)
    parser.add_argument("--shake-range", type=parse_timerange, default=[])
    parser.add_argument("--glitch", action="store_true")
    parser.add_argument("--glitch-intensity", type=int, default=0)
    parser.add_argument("--glitch-range", type=parse_timerange, default=[])
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--crossfade", type=float, default=0)
    parser.add_argument("--crossfade-mode", choices=["ffmpeg", "moviepy"], default="ffmpeg")
    args = parser.parse_args()

    process_clips_with_dynamic_audiofreq(
        args.video_files, args.audio_file, args.output_file,
        fps=args.fps,
        factor=args.factor,
        reverse=args.reverse,
        fast=args.fast,
        debug=args.debug,
        zoom_factor=args.zoom_factor,
        zoom_ranges=args.zoom_range,
        shake=args.shake,
        shake_intensity=args.shake_intensity,
        shake_ranges=args.shake_range,
        glitch=args.glitch,
        glitch_intensity=args.glitch_intensity,
        glitch_ranges=args.glitch_range,
        crossfade=args.crossfade,
        crossfade_mode=args.crossfade_mode
    )

