from PyQt5.QtWidgets import QListWidget

from core.step import MaestroStep


class StepListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.steps = []
        self.setDragDropMode(QListWidget.InternalMove)

    def add_step(self, step_type):
        step = MaestroStep(step_type)
        self.steps.append(step)
        self.addItem(step_type)
