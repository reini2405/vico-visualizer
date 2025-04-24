# modules/merge/merge_panel.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QSizePolicy, QMessageBox, QDialog, QListView,
    QDialogButtonBox, QAbstractItemView, QSlider, QSplitter
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QLocale, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from core.vico_executor import run_vico_merge
from modules.timeline.timeline_canvas import TimelineCanvas
import os

class VideoSortDialog(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Videoreihenfolge bearbeiten")
        self.setMinimumWidth(400)

        self.model = model
        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setDragDropMode(QAbstractItemView.InternalMove)
        self.view.setDefaultDropAction(Qt.MoveAction)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(buttons)
        self.setLayout(layout)

class MergePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.audio_file = None
        self.video_model = QStandardItemModel()

        main_layout = QVBoxLayout()

        # Fortschritt
        self.status_label = QLabel("Bereit")
        main_layout.addWidget(self.status_label)

        # --- Audio Auswahl ---
        audio_row = QHBoxLayout()
        self.audio_path_display = QLineEdit()
        self.audio_path_display.setPlaceholderText("Audiodatei wählen...")
        self.audio_path_display.setReadOnly(True)
        audio_button = QPushButton("Laden")
        audio_button.clicked.connect(self.select_audio)
        audio_row.addWidget(QLabel("🎵 Audio:"))
        audio_row.addWidget(self.audio_path_display)
        audio_row.addWidget(audio_button)
        main_layout.addLayout(audio_row)

        # --- Video Auswahl mit Sortierbutton ---
        video_row = QHBoxLayout()
        self.video_info_display = QLineEdit()
        self.video_info_display.setReadOnly(True)
        self.update_video_display()
        video_button = QPushButton("Sortieren")
        video_button.clicked.connect(self.sort_videos)
        add_button = QPushButton("Videos hinzufügen")
        add_button.clicked.connect(self.select_videos)
        video_row.addWidget(QLabel("🎞️ Videos:"))
        video_row.addWidget(self.video_info_display)
        video_row.addWidget(video_button)
        video_row.addWidget(add_button)
        main_layout.addLayout(video_row)

        # --- Optionen in einer Zeile ---
        options_row = QHBoxLayout()
        self.reverse_cb = QCheckBox("Rev")
        self.crossfade_clips_cb = QCheckBox("Cf")
        self.rc_cb = QCheckBox("Cf P-P")

        self.crossfade_input = QDoubleSpinBox()
        self.crossfade_input.setRange(0, 10)
        self.crossfade_input.setSingleStep(0.1)
        self.crossfade_input.setDecimals(1)
        self.crossfade_input.setSuffix(" s")
        self.crossfade_input.setValue(0.0)
        self.crossfade_input.setLocale(QLocale.c())

        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 240)
        self.fps_input.setValue(30)
        self.fps_input.setSuffix(" fps")

        options_row.addWidget(self.reverse_cb)
        options_row.addWidget(self.crossfade_clips_cb)
        options_row.addWidget(self.rc_cb)
        options_row.addWidget(self.crossfade_input)
        options_row.addWidget(QLabel("CF-TIME"))
        options_row.addWidget(self.fps_input)
        options_row.addWidget(QLabel("FPS"))
        main_layout.addLayout(options_row)

        # --- Action Button ---
        self.run_btn = QPushButton("🚀 Merge starten")
        self.run_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.run_btn.clicked.connect(self.run_merge)
        main_layout.addWidget(self.run_btn)

        # --- Vorschau + Steuerung + Timeline ---
        splitter = QSplitter(Qt.Vertical)

        self.video_widget = QVideoWidget()
        splitter.addWidget(self.video_widget)

        controls = QHBoxLayout()
        self.play_btn = QPushButton("▶")
        self.play_btn.clicked.connect(lambda: self.video_player.play())
        self.pause_btn = QPushButton("⏸")
        self.pause_btn.clicked.connect(lambda: self.video_player.pause())
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.clicked.connect(lambda: self.video_player.stop())
        self.backward_btn = QPushButton("⏪")
        self.backward_btn.clicked.connect(lambda: self.video_player.setPosition(self.video_player.position() - 5000))
        self.forward_btn = QPushButton("⏩")
        self.forward_btn.clicked.connect(lambda: self.video_player.setPosition(self.video_player.position() + 5000))

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(lambda v: self.audio_output.setVolume(v / 100.0))

        controls.addWidget(self.backward_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.forward_btn)
        controls.addWidget(QLabel("🔊"))
        controls.addWidget(self.volume_slider)
        main_layout.addLayout(controls)

        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 100)
        self.timeline_slider.sliderMoved.connect(self.seek_video)
        splitter.addWidget(self.timeline_slider)

        self.timeline_canvas = TimelineCanvas(duration=180)
        splitter.addWidget(self.timeline_canvas)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 0)
        splitter.setStretchFactor(2, 1)

        main_layout.addWidget(splitter)

        self.video_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.video_player.setAudioOutput(self.audio_output)
        self.video_player.setVideoOutput(self.video_widget)

        self.video_player.durationChanged.connect(self.update_slider_range)
        self.video_player.positionChanged.connect(self.update_slider_position)

        self.setLayout(main_layout)

    def update_video_display(self):
        count = self.video_model.rowCount()
        if count == 0:
            self.video_info_display.setText("Keine Videos ausgewählt")
        else:
            self.video_info_display.setText(f"{count} Video(s)")

    def sort_videos(self):
        dialog = VideoSortDialog(self.video_model, self)
        dialog.exec()
        self.update_video_display()

    def select_audio(self):
        file, _ = QFileDialog.getOpenFileName(self, "Audio auswählen", "", "Audio (*.wav *.mp3)")
        if file:
            self.audio_file = file
            self.audio_path_display.setText(file)
            self.timeline_canvas.load_audio(file)

    def select_videos(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Videos auswählen", "", "Videos (*.mp4 *.mov *.avi)")
        if files:
            for f in files:
                item = QStandardItem(os.path.basename(f))
                item.setData(f, Qt.UserRole)
                item.setEditable(False)
                self.video_model.appendRow(item)
            self.update_video_display()

    def run_merge(self):
        if not self.audio_file:
            QMessageBox.warning(self, "Fehlende Eingabe", "Bitte eine Audiodatei auswählen.")
            return

        if self.video_model.rowCount() == 0:
            QMessageBox.warning(self, "Fehlende Eingabe", "Bitte mindestens ein Video hinzufügen.")
            return

        self.video_player.stop()
        self.video_player.setSource(QUrl())

        self.status_label.setText("⏳ Merge läuft...")

        videos = [self.video_model.item(i).data(Qt.UserRole) for i in range(self.video_model.rowCount())]
        crossfade = self.crossfade_input.value()
        fps = self.fps_input.value()

        result = run_vico_merge(
            self.audio_file,
            videos,
            crossfade=crossfade if self.crossfade_clips_cb.isChecked() else None,
            reverse=self.reverse_cb.isChecked(),
            rc=self.rc_cb.isChecked(),
            fps=fps
        )

        if result.returncode == 0:
            self.status_label.setText("✅ Merge erfolgreich abgeschlossen.")
            self.load_video_preview()
        else:
            self.status_label.setText("❌ Fehler beim Merge.")

        print("Ausgabe:", result.stdout)
        if result.stderr:
            print("Fehler:", result.stderr)

    def load_video_preview(self):
        video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "vico_modules", "output.mp4"))
        if os.path.exists(video_path):
            self.video_player.setSource(QUrl.fromLocalFile(video_path))
            self.video_player.play()

    def update_slider_range(self, duration):
        self.timeline_slider.setRange(0, duration)
        self.timeline_canvas.duration = duration // 1000
        self.timeline_canvas.resizeEvent(None)
        self.timeline_canvas.set_playhead(self.video_player.position() / 1000)

    def update_slider_position(self, position):
        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(position)
        self.timeline_slider.blockSignals(False)
        self.timeline_canvas.set_playhead(position / 1000)

    def seek_video(self, position):
        self.video_player.setPosition(position)
