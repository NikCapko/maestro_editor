import os

from PyQt5.QtWidgets import QFileDialog, QFormLayout, QLineEdit, QPushButton, QWidget


class RunFlowEditor(QWidget):
    def __init__(self, step, project_dir):
        super().__init__()
        self.step = step
        self.project_dir = project_dir

        self.file_input = QLineEdit()
        self.file_input.setText(step.params.get("file", ""))

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse)

        self.file_input.textChanged.connect(self.on_change)

        layout = QFormLayout()
        layout.addRow("Flow file:", self.file_input)
        layout.addRow("", browse_btn)
        self.setLayout(layout)

    def browse(self):
        tests_dir = os.path.join(self.project_dir, "tests")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select flow", tests_dir, "YAML Files (*.yaml *.yml)"
        )
        if path:
            rel = os.path.relpath(path, tests_dir)
            self.file_input.setText(rel)

    def on_change(self):
        self.step.params.clear()
        if self.file_input.text():
            self.step.params["file"] = self.file_input.text()
