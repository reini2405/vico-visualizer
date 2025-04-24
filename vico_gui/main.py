# main.py (Letzter stabiler Stand vor Auto-Marker)
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from modules.merge.merge_panel import MergePanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("vico GUI")
        self.setMinimumSize(1000, 700)

        layout = QVBoxLayout()
        self.merge_panel = MergePanel()
        layout.addWidget(self.merge_panel)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
