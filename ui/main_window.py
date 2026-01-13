import os

import yaml
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
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
    QShortcut,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.runner import MaestroRunner
from core.step import MaestroStep
from core.validator import StepValidator
from core.yaml_service import save_maestro_yaml
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

        # ==== Buttons ====
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        self.open_project_btn = QPushButton(" Open Project")
        self.open_project_btn.setIcon(self.icon("folder-open.svg"))
        self.open_project_btn.clicked.connect(self.open_project)
        btn_layout.addWidget(self.open_project_btn)

        self.new_test_btn = QPushButton(" New Test")
        self.new_test_btn.setIcon(self.icon("file.svg"))
        self.new_test_btn.clicked.connect(self.new_test)
        tooltip = self.add_shortcut(QKeySequence.New, self.new_test, "New test")
        self.new_test_btn.setToolTip(tooltip)
        btn_layout.addWidget(self.new_test_btn)

        self.delete_test_btn = QPushButton("\uf1f8  Delete Test")
        self.delete_test_btn.clicked.connect(self.delete_test)
        tooltip = self.add_shortcut(
            key=QKeySequence.Delete,
            callback=self.delete_test,
            tooltip_text="Delete test",
            parent=self.test_list_widget,
        )
        self.delete_test_btn.setToolTip(tooltip)
        btn_layout.addWidget(self.delete_test_btn)

        self.save_btn = QPushButton(" Save YAML")
        self.save_btn.setIcon(self.icon("floppy-disk.svg"))
        self.save_btn.clicked.connect(self.save_current_test)
        tooltip = self.add_shortcut(
            QKeySequence.Save, self.save_current_test, "Save test"
        )
        self.save_btn.setToolTip(tooltip)
        btn_layout.addWidget(self.save_btn)

        # ==== Список шагов ====
        self.step_list = QListWidget()
        self.step_list.itemClicked.connect(self.on_step_selected)
        layout.addWidget(QLabel("Steps:"))
        layout.addWidget(self.step_list)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        self.add_launch_btn = QPushButton("Add launchApp")
        self.add_launch_btn.clicked.connect(lambda: self.add_step("launchApp"))
        btn_layout.addWidget(self.add_launch_btn)

        self.add_runflow_btn = QPushButton("Add runFlow")
        self.add_runflow_btn.clicked.connect(lambda: self.add_step("runFlow"))
        btn_layout.addWidget(self.add_runflow_btn)

        self.add_tap_btn = QPushButton(" Add TapOn")
        self.add_tap_btn.setIcon(self.icon("hand-pointer.svg"))
        self.add_tap_btn.clicked.connect(lambda: self.add_step("tapOn"))
        btn_layout.addWidget(self.add_tap_btn)

        self.add_input_btn = QPushButton(" Add InputText")
        self.add_input_btn.setIcon(self.icon("keyboard.svg"))
        self.add_input_btn.clicked.connect(lambda: self.add_step("inputText"))
        btn_layout.addWidget(self.add_input_btn)

        self.add_assert_btn = QPushButton(" Add assertVisible")
        self.add_assert_btn.setIcon(self.icon("eye.svg"))
        self.add_assert_btn.clicked.connect(lambda: self.add_step("assertVisible"))
        btn_layout.addWidget(self.add_assert_btn)

        self.add_back_btn = QPushButton(" Add back")
        self.add_back_btn.setIcon(self.icon("arrow-left.svg"))
        self.add_back_btn.clicked.connect(lambda: self.add_step("back"))
        btn_layout.addWidget(self.add_back_btn)

        self.delete_step_btn = QPushButton("\uf1f8  Delete step")
        self.delete_step_btn.setEnabled(False)
        self.delete_step_btn.clicked.connect(self.delete_selected_step)
        tooltip = self.add_shortcut(
            QKeySequence.Delete,
            self.delete_selected_step,
            "Delete step",
            parent=self.step_list,
        )
        self.delete_step_btn.setToolTip(tooltip)
        btn_layout.addWidget(self.delete_step_btn)

        # ==== Editor panel ====
        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout()
        self.editor_widget.setLayout(self.editor_layout)
        layout.addWidget(QLabel("Step Editor:"))
        layout.addWidget(self.editor_widget)

        self.run_btn = QPushButton(" Run Maestro")
        self.run_btn.setIcon(self.icon("circle-play.svg"))
        self.run_btn.clicked.connect(self.run_maestro)
        tooltip = self.add_shortcut("Ctrl+R", self.run_maestro, "Run test")
        self.run_btn.setToolTip(tooltip)
        layout.addWidget(self.run_btn)

        # ==== Live YAML preview ====

        self.yaml_preview = QTextEdit()
        self.yaml_preview.setReadOnly(True)
        # self.yaml_preview.setReadOnly(False)
        # self.yaml_preview.textChanged.connect(self.on_yaml_edited)
        layout.addWidget(QLabel("Live YAML Preview:"))
        layout.addWidget(self.yaml_preview)

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

        # если расширения нет — добавляем .yaml
        if not file_name.lower().endswith((".yaml", ".yml")):
            file_name += ".yaml"

        self.current_test_name = os.path.basename(file_name)
        save_maestro_yaml(file_name, self.app_id_input.text(), [])
        self.load_test_list()
        items = self.test_list_widget.findItems(self.current_test_name, Qt.MatchExactly)
        if items:
            self.test_list_widget.setCurrentItem(items[0])
            self.on_test_selected(items[0])

    def delete_test(self):
        if not self.confirm(
            "Delete test", f"Удалить тест:\n\n{self.current_test_name} ?"
        ):
            return
        path = os.path.join(self.tests_dir, self.current_test_name)
        os.remove(path)
        self.load_test_list()
        self.step_list.clear()
        pass

    def confirm(self, title, text):
        reply = QMessageBox.question(
            self, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    # ==== Steps methods ====
    def add_step(self, step_type):
        step = MaestroStep(step_type, params={})
        item = QListWidgetItem(step.display_name())
        item.setData(1, step)
        self.step_list.addItem(item)
        self.step_list.setCurrentItem(item)
        self.on_step_selected(item)
        self.update_yaml()

    def on_step_selected(self, item):
        self.clear_editor()
        step = item.data(1)
        editor = StepEditorFactory.create(step, self.project_dir)
        if editor:
            self.wrap_editor_with_update(editor)
            self.editor_layout.addWidget(editor)
        self.delete_step_btn.setEnabled(True)
        self.update_yaml()

    def clear_editor(self):
        for i in reversed(range(self.editor_layout.count())):
            widget = self.editor_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.delete_step_btn.setEnabled(False)

    def delete_selected_step(self):
        row = self.step_list.currentRow()
        if row < 0:
            return

        step = self.step_list.currentItem().data(1)

        if not self.confirm("Delete step", f"Удалить шаг:\n\n{step.display_name()} ?"):
            return

        self.step_list.takeItem(row)

        count = self.step_list.count()

        if count == 0:
            # шагов больше нет
            self.clear_editor()
            self.delete_step_btn.setEnabled(False)
            self.update_yaml()
            return

        # выбираем новый активный шаг
        if row < count:
            new_row = row
        else:
            new_row = count - 1

        self.step_list.setCurrentRow(new_row)
        item = self.step_list.currentItem()
        if item:
            self.on_step_selected(item)

        self.update_yaml()

    def wrap_editor_with_update(self, editor):
        try:
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
        except Exception as e:
            pass

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

    def save_current_test(self, show_message: bool = True):
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
        if show_message:
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
        self.save_current_test(False)

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

    def icon(self, name):
        return QIcon(os.path.join(os.path.dirname(__file__), "icons", name))

    def add_shortcut(self, key, callback, tooltip_text=None, parent=None):
        if isinstance(key, QKeySequence):
            sequence = key
        else:
            sequence = QKeySequence(key)

        shortcut = QShortcut(sequence, parent or self)
        shortcut.activated.connect(callback)

        if tooltip_text:
            native = sequence.toString(QKeySequence.NativeText)
            return f"{tooltip_text} ({native})"

        return None
