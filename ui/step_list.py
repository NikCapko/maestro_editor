from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from core.step import MaestroStep


class StepListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.steps = []
        self.setDragDropMode(QListWidget.InternalMove)

    def add_step(self, step_type):
        step = MaestroStep(step_type)
        self.steps.append(step)

        item = QListWidgetItem(f"{len(self.steps)}. {step_type}")
        item.setData(1, step)  # Qt.UserRole = 1
        self.addItem(item)

        self.setCurrentRow(len(self.steps) - 1)

    # def mark_invalid_steps(self, errors):
    # for i in range(self.count()):
    #    self.item(i).setBackground(None)

    # for err in errors:
    #    self.item(err.step_index).setBackground(QColor.red)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.sync_steps_with_ui()

    def sync_steps_with_ui(self):
        self.steps = [self.item(i).data(1) for i in range(self.count())]
