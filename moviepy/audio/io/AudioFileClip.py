# AudioFileClip.py
from moviepy.audio.AudioClip import AudioClip
class AudioFileClip(AudioClip):
    def __init__(self, filename):
        self.filename = filename
