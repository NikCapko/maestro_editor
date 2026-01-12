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

    @staticmethod
    def from_dict(data: dict):
        step_type = list(data.keys())[0]
        params = data[step_type]

        # поддерживаемые шаги
        supported = step_type in ("tapOn", "inputText", "launchApp", "assertVisible")

        if supported:
            return MaestroStep(
                step_type, params=params if isinstance(params, dict) else {}
            )
        else:
            return MaestroStep(
                step_type, raw=data, params=params if isinstance(params, dict) else {}
            )
