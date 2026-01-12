from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class LaunchAppEditor(QWidget):
    def __init__(self, step):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("LaunchApp"))
        self.setLayout(layout)
