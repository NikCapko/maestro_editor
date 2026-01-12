from ui.step_editors.input_text import InputTextEditor
from ui.step_editors.tap_on import TapOnEditor


class StepEditorFactory:
    @staticmethod
    def create(step):
        if step.step_type == "tapOn":
            return TapOnEditor(step)
        if step.step_type == "inputText":
            return InputTextEditor(step)
        return None
