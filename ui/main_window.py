import os

import yaml
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.runner import MaestroRunner
from core.step import MaestroStep
from core.validator import StepValidator
from core.yaml_service import save_maestro_yaml, steps_to_temp_yaml
from ui.step_editors.factory import StepEditorFactory
from ui.widgets.log_view import LogView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maestro Test Editor")
        self.resize(900, 600)

        self.project_dir = None
        self.tests_dir = None
        self.current_test_name = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # ==== appId ====
        self.app_id_input = QLineEdit()
        self.app_id_input.setPlaceholderText("App ID (package)")
        self.app_id_input.textChanged.connect(self.update_yaml)
        app_id_layout = QHBoxLayout()
        app_id_layout.addWidget(QLabel("App ID:"))
        app_id_layout.addWidget(self.app_id_input)
        layout.addLayout(app_id_layout)

        # ==== Список тестов ====
        self.test_list_widget = QListWidget()
        self.test_list_widget.itemClicked.connect(self.on_test_selected)
        layout.addWidget(QLabel("Tests:"))
        layout.addWidget(self.test_list_widget)

        # ==== Список шагов ====
        self.step_list = QListWidget()
        self.step_list.itemClicked.connect(self.on_step_selected)
        layout.addWidget(QLabel("Steps:"))
        layout.addWidget(self.step_list)

        btn_layout = QHBoxLayout()

        self.add_launch_btn = QPushButton("Add launchApp")
        self.add_launch_btn.clicked.connect(lambda: self.add_step("launchApp"))
        btn_layout.addWidget(self.add_launch_btn)

        self.add_runflow_btn = QPushButton("Add runFlow")
        self.add_runflow_btn.clicked.connect(lambda: self.add_step("runFlow"))
        btn_layout.addWidget(self.add_runflow_btn)

        self.add_tap_btn = QPushButton("Add TapOn")
        self.add_tap_btn.clicked.connect(lambda: self.add_step("tapOn"))
        btn_layout.addWidget(self.add_tap_btn)

        self.add_input_btn = QPushButton("Add InputText")
        self.add_input_btn.clicked.connect(lambda: self.add_step("inputText"))
        btn_layout.addWidget(self.add_input_btn)

        self.add_assert_btn = QPushButton("Add assertVisible")
        self.add_assert_btn.clicked.connect(lambda: self.add_step("assertVisible"))
        btn_layout.addWidget(self.add_assert_btn)

        layout.addLayout(btn_layout)

        # ==== Editor panel ====
        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout()
        self.editor_widget.setLayout(self.editor_layout)
        layout.addWidget(QLabel("Step Editor:"))
        layout.addWidget(self.editor_widget)

        self.run_btn = QPushButton("Run Maestro")
        self.run_btn.clicked.connect(self.run_maestro)
        layout.addWidget(self.run_btn)

        # ==== Live YAML preview ====

        self.yaml_preview = QTextEdit()
        self.yaml_preview.setReadOnly(False)
        self.yaml_preview.textChanged.connect(self.on_yaml_edited)
        layout.addWidget(QLabel("Live YAML Preview:"))
        layout.addWidget(self.yaml_preview)

        # ==== Buttons ====
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        self.open_project_btn = QPushButton("Open Project")
        self.open_project_btn.clicked.connect(self.open_project)
        btn_layout.addWidget(self.open_project_btn)

        self.new_test_btn = QPushButton("New Test")
        self.new_test_btn.clicked.connect(self.new_test)
        btn_layout.addWidget(self.new_test_btn)

        self.save_btn = QPushButton("Save YAML")
        self.save_btn.clicked.connect(self.save_current_test)
        btn_layout.addWidget(self.save_btn)

        self.log_view = LogView()
        layout.addWidget(QLabel("Maestro output:"))
        layout.addWidget(self.log_view)

    # ==== Project methods ====
    def open_project(self):
        project_dir = QFileDialog.getExistingDirectory(self, "Open Maestro Project")
        if not project_dir:
            return

        config_path = os.path.join(project_dir, "config.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self.app_id_input.setText(config.get("appId", ""))
        else:
            self.app_id_input.setText("")

        self.project_dir = project_dir
        self.tests_dir = os.path.join(project_dir, "tests")
        os.makedirs(self.tests_dir, exist_ok=True)
        self.load_test_list()

    def load_test_list(self):
        self.test_list_widget.clear()
        for root, _, files in os.walk(self.tests_dir):
            for file in files:
                if file.endswith((".yaml", ".yml")):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.tests_dir)
                    self.test_list_widget.addItem(rel_path)

    def on_test_selected(self, item: QListWidgetItem):
        self.current_test_name = item.text()
        path = os.path.join(self.tests_dir, self.current_test_name)
        self.open_yaml(path)

    def new_test(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "New Test", self.tests_dir, "YAML Files (*.yaml *.yml)"
        )
        if not file_name:
            return
        self.current_test_name = os.path.basename(file_name)
        self.step_list.clear()
        self.update_yaml()

    # ==== Steps methods ====
    def add_step(self, step_type):
        step = MaestroStep(step_type, params={})
        item = QListWidgetItem(step.display_name())
        item.setData(1, step)
        self.step_list.addItem(item)
        self.step_list.setCurrentItem(item)
        self.update_yaml()

    def on_step_selected(self, item):
        self.clear_editor()
        step = item.data(1)
        editor = StepEditorFactory.create(step, self.project_dir)
        if editor:
            self.wrap_editor_with_update(editor)
            self.editor_layout.addWidget(editor)
        self.update_yaml()

    def clear_editor(self):
        for i in reversed(range(self.editor_layout.count())):
            widget = self.editor_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def wrap_editor_with_update(self, editor):
        if hasattr(editor, "on_change"):
            original_change = editor.on_change

            def wrapped():
                original_change()
                # обновляем отображение шага в списке
                current_item = self.step_list.currentItem()
                if current_item:
                    step = current_item.data(1)
                    current_item.setText(step.display_name())
                self.update_yaml()

            editor.on_change = wrapped

    # ==== YAML methods ====
    def update_yaml(self):
        import io

        output = io.StringIO()
        app_id = self.app_id_input.text()
        if app_id:
            yaml.dump({"appId": app_id}, output, sort_keys=False, allow_unicode=True)
            output.write("---\n")
        step_list = [
            self.step_list.item(i).data(1).to_dict()
            for i in range(self.step_list.count())
        ]
        yaml.dump(step_list, output, sort_keys=False, allow_unicode=True)
        self.yaml_preview.setPlainText(output.getvalue())

    def save_current_test(self):
        if not self.current_test_name:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Test", self.tests_dir, "YAML Files (*.yaml *.yml)"
            )
            if not file_name:
                return
            self.current_test_name = os.path.basename(file_name)
        else:
            file_name = os.path.join(self.tests_dir, self.current_test_name)

        steps = [self.step_list.item(i).data(1) for i in range(self.step_list.count())]
        save_maestro_yaml(file_name, self.app_id_input.text(), steps)
        QMessageBox.information(self, "Saved", f"YAML сохранён: {file_name}")

    def open_yaml(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                docs = list(yaml.safe_load_all(f))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        # Первый документ — appId
        first_doc = docs[0] if docs else {}
        if isinstance(first_doc, dict) and "appId" in first_doc:
            self.app_id_input.setText(first_doc["appId"])
        else:
            self.app_id_input.setText("")

        # Остальные документы — шаги
        self.step_list.clear()
        for doc in docs[1:]:
            if isinstance(doc, list):
                for item in doc:
                    if isinstance(item, dict):
                        step = MaestroStep.from_dict(item)
                    elif isinstance(item, str):
                        step = MaestroStep(item, params={})
                    else:
                        continue
                    item_widget = QListWidgetItem(step.display_name())
                    item_widget.setData(1, step)
                    self.step_list.addItem(item_widget)
        self.update_yaml()

    def on_yaml_edited(self):
        """
        При редактировании YAML вручную синхронизируем список шагов и appId.
        """
        text = self.yaml_preview.toPlainText()
        try:
            docs = list(yaml.safe_load_all(text))
            if not docs:
                return

            # Первый документ — appId
            first_doc = docs[0]
            if isinstance(first_doc, dict) and "appId" in first_doc:
                self.app_id_input.blockSignals(True)
                self.app_id_input.setText(first_doc["appId"])
                self.app_id_input.blockSignals(False)

            # Остальные документы — шаги
            self.step_list.clear()
            for doc in docs[1:]:
                if isinstance(doc, list):
                    for item in doc:
                        if isinstance(item, dict):
                            step = MaestroStep.from_dict(item)
                        elif isinstance(item, str):
                            step = MaestroStep(item, params={})
                        else:
                            continue
                        item_widget = QListWidgetItem(step.display_name())
                        item_widget.setData(1, step)
                        self.step_list.addItem(item_widget)
                elif isinstance(doc, dict):
                    step = MaestroStep.from_dict(doc)
                    item_widget = QListWidgetItem(step.display_name())
                    item_widget.setData(1, step)
                    self.step_list.addItem(item_widget)
        except Exception:
            # Ошибки синтаксиса YAML игнорируем временно
            pass

    def get_steps(self):
        steps = []
        for i in range(self.step_list.count()):
            steps.append(self.step_list.item(i).data(1))
        return steps

    def run_maestro(self):
        if not self.current_test_name:
            QMessageBox.warning(self, "Run", "Test file is not selected")
            return

        steps = self.get_steps()

        # 1️⃣ Валидация шагов
        errors = StepValidator.validate(steps)

        self.log_view.clear()

        if errors:
            self.log_view.append_line("❌ Validation errors:")
            for err in errors:
                self.log_view.append_line(str(err))
            return

        # 2️⃣ Сохраняем текущий тест перед запуском
        self.save_current_test()

        # 3️⃣ Запускаем АКТИВНЫЙ файл
        yaml_path = os.path.join(self.tests_dir, self.current_test_name)

        self.log_view.append_line("▶ Running Maestro")
        self.log_view.append_line(f"File: {self.current_test_name}")

        self.runner = MaestroRunner(yaml_path=yaml_path)

        self.runner.log.connect(self.log_view.append_line)
        self.runner.finished.connect(self.on_run_finished)
        self.runner.start()

    def on_run_finished(self, code):
        if code == 0:
            self.log_view.append_line("✅ Finished successfully")
        else:
            self.log_view.append_line(f"❌ Finished with code {code}")
