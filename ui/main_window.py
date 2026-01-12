from PyQt5.QtWidgets import QMainWindow, QPushButton, QSplitter, QVBoxLayout, QWidget

from core.yaml_service import steps_to_yaml
from ui.step_editors.factory import StepEditorFactory
from ui.step_list import StepListWidget
from ui.widgets.yaml_preview import YamlPreview


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maestro GUI")
        self.resize(1200, 700)

        self.step_list = StepListWidget()

        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_container)

        self.yaml_preview = YamlPreview()

        self.add_tap_btn = QPushButton("Add tapOn")
        self.add_tap_btn.clicked.connect(lambda: self.add_step("tapOn"))

        self.step_list.currentRowChanged.connect(self.on_step_selected)
        self.step_list.model().rowsMoved.connect(lambda *_: self.update_yaml())

        splitter = QSplitter()
        splitter.addWidget(self.step_list)
        splitter.addWidget(self.editor_container)
        splitter.addWidget(self.yaml_preview)
        splitter.setSizes([200, 400, 400])

        layout = QVBoxLayout()
        layout.addWidget(self.add_tap_btn)
        layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_step(self, step_type):
        self.step_list.add_step(step_type)
        self.update_yaml()

    def on_step_selected(self, index):
        # очистка редактора
        for i in reversed(range(self.editor_layout.count())):
            widget = self.editor_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if index < 0:
            return

        step = self.step_list.steps[index]
        editor = StepEditorFactory.create(step)

        if editor:
            # 🔹 КЛЮЧЕВОЙ МОМЕНТ
            self.wrap_editor_with_update(editor)

            self.editor_layout.addWidget(editor)

        self.update_yaml()

    def wrap_editor_with_update(self, editor):
        """
        Перехватываем изменения параметров шага
        """
        original_change = editor.on_change

        def wrapped():
            original_change()
            self.update_yaml()

        editor.on_change = wrapped

    def update_yaml(self):
        yaml_text = steps_to_yaml(self.step_list.steps)
        self.yaml_preview.setPlainText(yaml_text)
