from PySide6.QtWidgets import QApplication, QWidget

app = QApplication([])
window = QWidget()
window.setWindowTitle("Test")
window.resize(400, 300)
window.show()
app.exec()
