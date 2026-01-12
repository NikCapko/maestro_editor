from PyQt5.QtWidgets import QFormLayout, QLineEdit, QWidget


class InputTextEditor(QWidget):
    def __init__(self, step):
        super().__init__()
        self.step = step

        self.target_id = QLineEdit()
        self.input_text = QLineEdit()

        self.target_id.setText(step.params.get("id", ""))
        self.input_text.setText(step.params.get("text", ""))

        self.target_id.textChanged.connect(self.on_change)
        self.input_text.textChanged.connect(self.on_change)

        layout = QFormLayout()
        layout.addRow("Target ID:", self.target_id)
        layout.addRow("Text:", self.input_text)
        self.setLayout(layout)

    def on_change(self):
        self.step.params.clear()

        if self.target_id.text():
            self.step.params["id"] = self.target_id.text()

        if self.input_text.text():
            self.step.params["text"] = self.input_text.text()
