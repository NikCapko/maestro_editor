from PyQt5.QtWidgets import QFormLayout, QLineEdit, QWidget


class InputTextEditor(QWidget):
    def __init__(self, step):
        super().__init__()
        self.step = step

        self.target_input = QLineEdit()
        self.text_input = QLineEdit()

        self.target_input.setText(step.params.get("id", ""))
        self.text_input.setText(step.params.get("text", ""))

        self.target_input.textChanged.connect(self.on_change)
        self.text_input.textChanged.connect(self.on_change)

        layout = QFormLayout()
        layout.addRow("Target ID:", self.target_input)
        layout.addRow("Text:", self.text_input)
        self.setLayout(layout)

    def on_change(self):
        self.step.params.clear()

        if self.target_input.text():
            self.step.params["id"] = self.target_input.text()

        if self.text_input.text():
            self.step.params["text"] = self.text_input.text()
