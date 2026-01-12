class MaestroStep:
    def __init__(self, step_type: str, params=None):
        self.step_type = step_type
        self.params = params or {}

    def to_dict(self):
        return {self.step_type: self.params}

    @staticmethod
    def from_dict(data: dict):
        step_type = list(data.keys())[0]
        return MaestroStep(step_type, data[step_type])
