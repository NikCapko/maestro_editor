from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.step_list import StepListWidget
from ui.widgets.log_view import LogView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maestro GUI")
        self.resize(1000, 600)

        self.step_list = StepListWidget()
        self.editor_panel = QTextEdit()
        self.log_view = LogView()

        self.run_btn = QPushButton("Run")

        splitter = QSplitter()
        splitter.addWidget(self.step_list)
        splitter.addWidget(self.editor_panel)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.log_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
