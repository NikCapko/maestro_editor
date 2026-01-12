class ValidationError:
    def __init__(self, step_index, message):
        self.step_index = step_index
        self.message = message

    def __str__(self):
        return f"Step {self.step_index + 1}: {self.message}"


class StepValidator:
    @staticmethod
    def validate(steps):
        errors = []

        for i, step in enumerate(steps):
            if step.step_type == "tapOn":
                if not step.params:
                    errors.append(ValidationError(i, "tapOn требует id или text"))

            if step.step_type == "inputText":
                if "text" not in step.params:
                    errors.append(ValidationError(i, "inputText требует text"))
                if not any(k in step.params for k in ("id", "text")):
                    errors.append(ValidationError(i, "inputText требует цель (id)"))

            if step.step_type == "assertVisible":
                if "id" not in step.params or not step.params["id"]:
                    errors.append(
                        ValidationError(i, "assertVisible требует указать id элемента")
                    )

        return errors
