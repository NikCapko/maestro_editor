import tempfile

import yaml


def steps_to_yaml(steps):
    return yaml.dump(
        [step.to_dict() for step in steps], sort_keys=False, allow_unicode=True
    )


def yaml_to_steps(text):
    data = yaml.safe_load(text) or []
    return [MaestroStep.from_dict(item) for item in data]


def steps_to_temp_yaml(steps):
    data = [step.to_dict() for step in steps]

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    )

    yaml.dump(data, tmp, sort_keys=False, allow_unicode=True)
    tmp.close()
    return tmp.name
