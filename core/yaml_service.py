import tempfile

import yaml

from core.step import MaestroStep


def steps_to_yaml(steps):
    return yaml.dump(
        [step.to_dict() for step in steps], sort_keys=False, allow_unicode=True
    )


def yaml_to_steps(text):
    steps = []
    docs = list(yaml.safe_load_all(text))

    if not docs:
        return None, steps

    # Первый документ — appId
    first_doc = docs[0]
    app_id = first_doc.get("appId") if isinstance(first_doc, dict) else None

    # Остальные документы — список шагов
    for doc in docs[1:]:
        if isinstance(doc, list):
            for item in doc:
                if isinstance(item, dict):
                    steps.append(MaestroStep.from_dict(item))
                elif isinstance(item, str):
                    # простой шаг без параметров
                    steps.append(MaestroStep(item, params={}))
        elif isinstance(doc, dict):
            steps.append(MaestroStep.from_dict(doc))
        elif isinstance(doc, str):
            steps.append(MaestroStep(doc, params={}))

    return app_id, steps


def steps_to_temp_yaml(steps, app_id=None):
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    )

    if app_id:
        yaml.dump({"appId": app_id}, tmp, sort_keys=False)
        tmp.write("---\n")

    step_list = [step.to_dict() for step in steps]
    yaml.dump(step_list, tmp, sort_keys=False, allow_unicode=True)

    tmp.close()
    return tmp.name
