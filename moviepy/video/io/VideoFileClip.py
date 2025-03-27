# moviepy/video/io/VideoFileClip.py

import cv2
import numpy as np
from moviepy.video.VideoClip import VideoClip

class VideoFileClip(VideoClip):
    def __init__(self, filename, *args, **kwargs):
        super().__init__()

        self.filename = filename
        self.reader = cv2.VideoCapture(filename)

        if not self.reader.isOpened():
            raise IOError(f"Konnte Video nicht öffnen: {filename}")

        self.fps = self.reader.get(cv2.CAP_PROP_FPS)
        self.duration = self.reader.get(cv2.CAP_PROP_FRAME_COUNT) / self.fps
        self.size = (
            int(self.reader.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.reader.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

        self.frame_function = self.get_frame  # wichtig für moviepy-internes Verhalten

    def get_frame(self, t):
        frame_number = int(t * self.fps)
        self.reader.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.reader.read()
        if not ret:
            raise ValueError(f"Kein Frame bei t={t:.2f}s (Frame {frame_number})")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def close(self):
        if self.reader:
            self.reader.release()
