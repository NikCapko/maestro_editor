from PyQt5.QtWidgets import QMainWindow, QPushButton, QSplitter, QVBoxLayout, QWidget

from core.runner import MaestroRunner
from core.validator import StepValidator
from core.yaml_service import steps_to_temp_yaml, steps_to_yaml
from ui.step_editors.factory import StepEditorFactory
from ui.step_list import StepListWidget
from ui.widgets.log_view import LogView
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

        self.add_input_btn = QPushButton("Add inputText")
        self.add_input_btn.clicked.connect(lambda: self.add_step("inputText"))

        self.step_list.currentRowChanged.connect(self.on_step_selected)
        self.step_list.model().rowsMoved.connect(lambda *_: self.update_yaml())

        splitter = QSplitter()
        splitter.addWidget(self.step_list)
        splitter.addWidget(self.editor_container)
        splitter.addWidget(self.yaml_preview)
        splitter.setSizes([200, 400, 400])

        layout = QVBoxLayout()
        layout.addWidget(self.add_tap_btn)
        layout.addWidget(self.add_input_btn)
        layout.addWidget(splitter)

        self.run_btn = QPushButton("Run Maestro")
        self.run_btn.clicked.connect(self.run_maestro)

        self.log_view = LogView()
        layout.addWidget(self.run_btn)
        layout.addWidget(self.log_view)

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

    def run_maestro(self):
        errors = StepValidator.validate(self.step_list.steps)

        if errors:
            self.log_view.clear()
            self.log_view.append_line("❌ Validation errors:")

            for err in errors:
                self.log_view.append_line(str(err))

            # self.step_list.mark_invalid_steps(errors)

            return

        yaml_path = steps_to_temp_yaml(self.step_list.steps)

        self.log_view.clear()
        self.log_view.append_line(f"Running: {yaml_path}")

        self.runner = MaestroRunner(yaml_path)
        self.runner.log.connect(self.log_view.append_line)
        self.runner.finished.connect(self.on_run_finished)
        self.runner.start()

    def on_run_finished(self, code):
        if code == 0:
            self.log_view.append_line("✅ Finished successfully")
        else:
            self.log_view.append_line(f"❌ Finished with code {code}")
