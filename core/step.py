class MaestroStep:
    def __init__(self, step_type: str, params=None, raw=None):
        self.step_type = step_type
        self.params = params or {}
        self.raw = raw  # оригинальный YAML, если шаг не поддержан

    def to_dict(self):
        if self.raw is not None:
            return self.raw
        if not self.params:  # нет параметров
            return self.step_type  # возвращаем просто строку

        return {self.step_type: self.params}

    def display_name(self):
        if self.step_type == "runFlow":
            return f"runFlow ({self.params.get('file', '')})"

        if not self.params:
            return self.step_type

        parts = []
        if "id" in self.params:
            parts.append(f"id={self.params['id']}")
        if "text" in self.params:
            parts.append(f"text={self.params['text']}")

        return f"{self.step_type} ({', '.join(parts)})"

    @staticmethod
    def from_dict(data: dict):
        step_type = list(data.keys())[0]
        params = data[step_type]

        # поддерживаемые шаги
        supported = step_type in (
            "tapOn",
            "inputText",
            "launchApp",
            "assertVisible",
            "back",
        )

        if supported:
            return MaestroStep(
                step_type, params=params if isinstance(params, dict) else {}
            )
        else:
            return MaestroStep(
                step_type, raw=data, params=params if isinstance(params, dict) else {}
            )
