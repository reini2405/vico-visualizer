import json
import subprocess
import sys
from PySide6.QtWidgets import QWidget, QMenu, QInputDialog, QComboBox, QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPainter, QColor, QPen, QAction
from PySide6.QtCore import Qt
import numpy as np
from pydub import AudioSegment

EFFECT_COLORS = {
    "color": QColor("#ff4444"),
    "zoom": QColor("#3399ff"),
    "shake": QColor("#33cc33"),
    "ripple": QColor("#cc66ff"),
    "manual": QColor("#888888")
}

class TimelineCanvas(QWidget):
    def __init__(self, duration=180, parent=None):
        super().__init__(parent)
        self.duration = duration
        self.zoom = 0.3
        self.setMinimumHeight(150)
        self.playhead_position = 0
        self.markers = []
        self.effects = {}
        self.audio_waveform_left = []
        self.audio_waveform_right = []
        self.audio_file = None

    def resizeEvent(self, event):
        if self.duration > 0:
            self.zoom = self.width() / (self.duration * 100)
        self.update()
        super().resizeEvent(event)

    def load_audio(self, filepath):
        self.audio_file = filepath
        try:
            audio = AudioSegment.from_file(filepath)
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                left = samples[:, 0]
                right = samples[:, 1]
            else:
                left = samples
                right = samples

            num_points = 1000
            factor = len(left) // num_points
            self.audio_waveform_left = left[:num_points * factor].reshape(-1, factor).mean(axis=1)
            self.audio_waveform_right = right[:num_points * factor].reshape(-1, factor).mean(axis=1)

            max_val = max(np.max(np.abs(self.audio_waveform_left)), np.max(np.abs(self.audio_waveform_right)))
            if max_val > 0:
                self.audio_waveform_left = self.audio_waveform_left / max_val
                self.audio_waveform_right = self.audio_waveform_right / max_val
        except Exception as e:
            print(f"Waveform konnte nicht geladen werden: {e}")

    def set_playhead(self, seconds):
        self.playhead_position = seconds
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1e1e1e"))

        width = self.width()
        height = self.height()
        pixels_per_second = self.zoom * 100
        ruler_height = 20

        pen = QPen(QColor("#aaaaaa"))
        painter.setPen(pen)
        range_end = int((self.duration + 9) // 10 * 10)
        for sec in range(0, range_end + 1, 10):
            x = int(sec * pixels_per_second)
            if x > width:
                break
            painter.drawLine(x, 0, x, ruler_height)
            painter.drawText(x + 2, 10, f"{sec}s")

        if len(self.audio_waveform_left) > 0:
            w_len = len(self.audio_waveform_left)
            spacing = width / w_len
            audio_color = QColor("#00aaff")
            painter.setPen(audio_color)

            left_top = ruler_height + 10
            right_top = ruler_height + 60
            waveform_height = 30

            for i in range(w_len):
                x = int(i * spacing)
                l_val = self.audio_waveform_left[i]
                r_val = self.audio_waveform_right[i]
                painter.drawLine(x, left_top + waveform_height, x, int(left_top + waveform_height - l_val * waveform_height))
                painter.drawLine(x, right_top, x, int(right_top - r_val * waveform_height))

            painter.setPen(QPen(QColor("#444444"), 1, Qt.DashLine))
            painter.drawLine(0, ruler_height + 50, width, ruler_height + 50)

        # Effekt-Marker zeichnen
        track_height = 8
        base_y = height - 30

        for marker_time, info in self.effects.items():
            effect = info.get("effect")
            color = EFFECT_COLORS.get(effect, QColor("#ffffff"))
            x = int(float(marker_time) * pixels_per_second)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(x, base_y, 6, track_height)

        playhead_x = int(self.playhead_position * pixels_per_second)
        playhead_pen = QPen(QColor("#ff0000"), 2)
        painter.setPen(playhead_pen)
        painter.drawLine(playhead_x, 0, playhead_x, height)

    def mousePressEvent(self, event):
        pixels_per_second = self.zoom * 100
        clicked_second = event.pos().x() / pixels_per_second
        print("[DEBUG] Mouse clicked at", clicked_second)

        if event.button() == Qt.LeftButton:
            self.markers.append(clicked_second)
            self.effects[str(clicked_second)] = {"effect": "manual", "action": "start"}
            self.update()

    def mousePressEvent(self, event):
        pixels_per_second = self.zoom * 100
        clicked_second = event.pos().x() / pixels_per_second
        print("[DEBUG] Mouse clicked at", clicked_second)

        if event.button() == Qt.LeftButton:
            self.markers.append(clicked_second)
            self.effects[str(clicked_second)] = {"effect": "manual", "action": "start"}
            self.update()

        elif event.button() == Qt.RightButton:
            closest = None
            for m in self.markers:
                if abs(m - clicked_second) <= 0.5:
                    closest = m
                    break
            if closest is not None:
                from PySide6.QtWidgets import QMenu, QInputDialog
                menu = QMenu(self)
                delete_action = menu.addAction("Marker löschen")
                effect_action = menu.addAction("Effekt zuweisen")
                action = menu.exec(event.globalPosition().toPoint())

                if action == delete_action:
                    self.markers.remove(closest)
                    self.effects.pop(str(closest), None)
                    self.update()

                elif action == effect_action:
                    name, ok = QInputDialog.getText(self, "Effekt zuweisen", "Effektname:")
                    if ok and name:
                        action_type, ok = QInputDialog.getItem(self, "Aktion", "Start oder Ende?", ["start", "end"], 0, False)
                        if ok:
                            self.effects[str(closest)] = {"effect": name, "action": action_type}
                            self.update()


    def run_auto_analysis(self):
        if not self.audio_file:
            print("Keine Audiodatei geladen für Analyse.")
            return

        try:
            result = subprocess.run([
                sys.executable, "vico_modules/vico_auto", "-i", self.audio_file
            ], capture_output=True, text=True)
            if result.returncode != 0:
                print("Fehler bei vico_auto:", result.stderr)
                return

            output = result.stdout
            self.parse_auto_output(output)

        except Exception as e:
            print(f"Fehler beim Ausführen von vico_auto: {e}")

    def parse_auto_output(self, output):
        section = None
        for line in output.splitlines():
            line = line.strip()
            if "Pegel-Zeiten" in line:
                section = "auto:pegel"
            elif "Höhen-Zeiten" in line:
                section = "auto:höhen"
            elif "Tiefen-Zeiten" in line:
                section = "auto:tiefen"
            elif line and section and "-" in line:
                try:
                    time_range = line.split()[0]
                    start = time_range.split("-")[0]
                    mins, secs = map(int, start.split(":"))
                    seconds = mins * 60 + secs
                    self.markers.append(seconds)
                    self.effects[str(seconds)] = {"effect": section, "action": "start"}
                except Exception as e:
                    print(f"Fehler beim Parsen der Zeile '{line}': {e}")
        self.update()
