from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class BackEditor(QWidget):
    def __init__(self, step):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Back - go to previos screen"))
        self.setLayout(layout)
