# moviepy/audio/AudioClip.py

import numpy as np

class AudioClip:
    def __init__(self, make_frame=None, duration=None, fps=44100):
        self.make_frame = make_frame
        self.duration = duration
        self.fps = fps
        self.start = 0  # default value, used in composite

    def get_frame(self, t):
        if self.make_frame is not None:
            return self.make_frame(t)
        else:
            return np.zeros(1)

    def __add__(self, other):
        return CompositeAudioClip([self, other])


class CompositeAudioClip(AudioClip):
    def __init__(self, clips):
        super().__init__()
        self.clips = clips
        self.duration = max([clip.duration for clip in clips if clip.duration is not None])
        self.fps = max([getattr(clip, "fps", 44100) for clip in clips])
        self.start = 0

    def get_frame(self, t):
        return sum(
            clip.get_frame(t - getattr(clip, "start", 0))
            for clip in self.clips
            if getattr(clip, "start", 0) <= t < getattr(clip, "start", 0) + clip.duration
        )
def concatenate_audioclips(clips):
    """
    Kombiniert mehrere AudioClip-Objekte zu einem einzigen AudioClip.
    """
    durations = [clip.duration for clip in clips]
    result = AudioClip()
    result.duration = sum(durations)
    result.fps = clips[0].fps  # Setze die FPS des ersten Clips für den neuen Clip
    result.audio = [clip.audio for clip in clips]
    return result

