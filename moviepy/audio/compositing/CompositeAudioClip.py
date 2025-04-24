# moviepy/audio/compositing/CompositeAudioClip.py

from moviepy.audio.AudioClip import AudioClip

class CompositeAudioClip(AudioClip):
    def __init__(self, clips):
        super().__init__()
        self.clips = clips
        self.duration = max([clip.duration for clip in clips if clip.duration is not None])
        self.fps = max([clip.fps for clip in clips if hasattr(clip, "fps") and clip.fps is not None])

    def get_frame(self, t):
        return sum(clip.get_frame(t) for clip in self.clips if clip.start <= t < clip.end)

