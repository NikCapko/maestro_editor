from PyQt5.QtWidgets import QTextEdit


class YamlPreview(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setPlaceholderText("YAML preview will appear here")
