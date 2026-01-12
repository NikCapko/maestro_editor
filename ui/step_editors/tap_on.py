from PyQt5.QtWidgets import QFormLayout, QLineEdit, QWidget


class TapOnEditor(QWidget):
    def __init__(self, step):
        super().__init__()
        self.step = step

        self.id_input = QLineEdit()
        self.text_input = QLineEdit()

        # заполнение из модели
        self.id_input.setText(step.params.get("id", ""))
        self.text_input.setText(step.params.get("text", ""))

        self.id_input.textChanged.connect(self.on_change)
        self.text_input.textChanged.connect(self.on_change)

        layout = QFormLayout()
        layout.addRow("ID:", self.id_input)
        layout.addRow("Text:", self.text_input)
        self.setLayout(layout)

    def on_change(self):
        self.step.params.clear()

        if self.id_input.text():
            self.step.params["id"] = self.id_input.text()

        if self.text_input.text():
            self.step.params["text"] = self.text_input.text()
