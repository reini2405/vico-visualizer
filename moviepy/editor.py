# editor.py – Bau dir dein "moviepy.editor" wie früher

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.all import fadein, fadeout, resize
from moviepy.audio.fx.all import volumex
# Verschiebe diesen Import nachträglich
import moviepy.editor

