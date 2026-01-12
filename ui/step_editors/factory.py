from ui.step_editors.assert_visible import AssertVisibleEditor
from ui.step_editors.input_text import InputTextEditor
from ui.step_editors.launch_app import LaunchAppEditor
from ui.step_editors.run_flow import RunFlowEditor
from ui.step_editors.tap_on import TapOnEditor


class StepEditorFactory:
    @staticmethod
    def create(step, project_dir=None):
        if step.step_type == "tapOn":
            return TapOnEditor(step)
        if step.step_type == "inputText":
            return InputTextEditor(step)
        if step.step_type == "launchApp":
            return LaunchAppEditor(step)
        if step.step_type == "assertVisible":
            return AssertVisibleEditor(step)
        if step.step_type == "runFlow":
            return RunFlowEditor(step, project_dir)
        return None
