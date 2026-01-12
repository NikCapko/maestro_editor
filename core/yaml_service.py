import yaml


def steps_to_yaml(steps):
    return yaml.dump(
        [step.to_dict() for step in steps], sort_keys=False, allow_unicode=True
    )


def yaml_to_steps(text):
    data = yaml.safe_load(text) or []
    return [MaestroStep.from_dict(item) for item in data]
