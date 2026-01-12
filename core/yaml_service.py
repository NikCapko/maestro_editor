import tempfile

import yaml

from core.step import MaestroStep


def steps_to_yaml(steps):
    return yaml.dump(
        [step.to_dict() for step in steps], sort_keys=False, allow_unicode=True
    )


def yaml_to_steps(text: str):
    data = yaml.safe_load(text)

    if not isinstance(data, list):
        raise ValueError("Maestro YAML должен быть списком шагов")

    steps = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Некорректный шаг в YAML")
        steps.append(MaestroStep.from_dict(item))

    return steps


def steps_to_temp_yaml(steps):
    data = [step.to_dict() for step in steps]

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    )

    yaml.dump(data, tmp, sort_keys=False, allow_unicode=True)
    tmp.close()
    return tmp.name
