from PyQt5.QtWidgets import QTextEdit


class LogView(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def append_line(self, text):
        self.append(text)
