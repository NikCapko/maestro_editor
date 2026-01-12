from PyQt5.QtWidgets import QWidget


class BaseStepEditor(QWidget):
    def __init__(self, step):
        super().__init__()
        self.step = step
