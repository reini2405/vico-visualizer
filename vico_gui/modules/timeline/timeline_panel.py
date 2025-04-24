# modules/timeline/timeline_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os

class TimelinePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.audio_file = None
        self.signal = None
        self.sr = None

        layout = QVBoxLayout()

        self.label = QLabel("Keine Audiodatei geladen")
        self.load_button = QPushButton("Audio laden und anzeigen")
        self.load_button.clicked.connect(self.load_audio)

        self.canvas = FigureCanvas(Figure(figsize=(10, 2)))
        self.ax = self.canvas.figure.subplots()

        layout.addWidget(self.label)
        layout.addWidget(self.load_button)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def load_audio(self):
        file, _ = QFileDialog.getOpenFileName(self, "WAV-Datei laden", "", "Audio (*.wav)")
        if file:
            self.audio_file = file
            self.label.setText(os.path.basename(file))
            self.signal, self.sr = librosa.load(file, sr=None)
            self.plot_waveform()

    def plot_waveform(self):
        self.ax.clear()
        librosa.display.waveshow(self.signal, sr=self.sr, ax=self.ax, color='b')
        self.ax.set(title='Wellenform', xlabel='Zeit (s)', ylabel='Amplitude')
        self.canvas.draw()
