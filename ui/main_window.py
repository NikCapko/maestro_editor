import io

import yaml
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.runner import MaestroRunner
from core.step import MaestroStep
from core.validator import StepValidator
from core.yaml_service import steps_to_temp_yaml, steps_to_yaml, yaml_to_steps
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

        # Панель для appId
        self.app_id_input = QLineEdit()
        self.app_id_input.setPlaceholderText("App ID (package)")
        self.app_id_input.textChanged.connect(self.update_yaml)

        self.app_id_layout = QHBoxLayout()
        self.app_id_layout.addWidget(QLabel("App ID:"))
        self.app_id_layout.addWidget(self.app_id_input)

        self.app_id = None

        self.add_launch_btn = QPushButton("Add launchApp")
        self.add_launch_btn.clicked.connect(lambda: self.add_step("launchApp"))

        self.add_tap_btn = QPushButton("Add tapOn")
        self.add_tap_btn.clicked.connect(lambda: self.add_step("tapOn"))

        self.open_btn = QPushButton("Open YAML")
        self.open_btn.clicked.connect(self.open_yaml)

        self.add_input_btn = QPushButton("Add inputText")
        self.add_input_btn.clicked.connect(lambda: self.add_step("inputText"))

        self.add_assert_btn = QPushButton("Add assertVisible")
        self.add_assert_btn.clicked.connect(lambda: self.add_step("assertVisible"))

        self.step_list.currentRowChanged.connect(self.on_step_selected)
        self.step_list.model().rowsMoved.connect(lambda *_: self.update_yaml())

        splitter = QSplitter()
        splitter.addWidget(self.step_list)
        splitter.addWidget(self.editor_container)
        splitter.addWidget(self.yaml_preview)
        splitter.setSizes([200, 400, 400])

        layout = QVBoxLayout()
        layout.addLayout(self.app_id_layout)
        layout.addWidget(self.open_btn)
        layout.addWidget(self.add_launch_btn)
        layout.addWidget(self.add_tap_btn)
        layout.addWidget(self.add_input_btn)
        layout.addWidget(self.add_assert_btn)
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
        self.clear_editor()  # теперь безопасно

        if index < 0:
            return

        step = self.step_list.steps[index]

        if step.raw is not None:
            # неподдерживаемый шаг
            from PyQt5.QtWidgets import QLabel

            self.editor_layout.addWidget(QLabel("Этот шаг пока не поддерживается"))
            return

        editor = StepEditorFactory.create(step)
        if editor:
            self.wrap_editor_with_update(editor)
            self.editor_layout.addWidget(editor)

        self.update_yaml()

    def wrap_editor_with_update(self, editor):
        """
        Перехватываем изменения параметров шага
        """
        if hasattr(editor, "on_change"):
            original_change = editor.on_change

            def wrapped():
                original_change()
                self.update_yaml()

            editor.on_change = wrapped

    def update_yaml(self):
        # берём текущее appId
        self.app_id = self.app_id_input.text()

        # генерируем YAML в памяти для Live preview
        output = io.StringIO()

        if self.app_id:
            yaml.dump(
                {"appId": self.app_id}, output, sort_keys=False, allow_unicode=True
            )
            output.write("---\n")

        step_dicts = [step.to_dict() for step in self.step_list.steps]
        yaml.dump(step_dicts, output, sort_keys=False, allow_unicode=True)

        self.yaml_preview.setPlainText(output.getvalue())

    def run_maestro(self):
        errors = StepValidator.validate(self.step_list.steps)

        if errors:
            self.log_view.clear()
            self.log_view.append_line("❌ Validation errors:")

            for err in errors:
                self.log_view.append_line(str(err))

            # self.step_list.mark_invalid_steps(errors)

            return

        yaml_path = steps_to_temp_yaml(self.step_list.steps, self.app_id)

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

    def open_yaml(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Maestro YAML", "", "YAML Files (*.yaml *.yml)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            self.app_id, steps = yaml_to_steps(text)
            self.app_id_input.setText(self.app_id or "")
            self.load_steps(steps)

        except Exception as e:
            QMessageBox.critical(self, "YAML Import Error", str(e))

    def load_steps(self, steps):
        self.step_list.clear()
        self.step_list.steps = []

        for step in steps:
            self.step_list.steps.append(step)

            label = step.step_type
            if step.raw is not None:
                label += " (unsupported)"

            item = QListWidgetItem(label)
            item.setData(1, step)
            self.step_list.addItem(item)

        self.update_yaml()

    def clear_editor(self):
        """
        Очищает правую панель редактора шагов
        """
        for i in reversed(range(self.editor_layout.count())):
            widget = self.editor_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
