# roadmap-estudos/backend/services/dsl/engine/validate/steps.py
import re
from typing import Any, Callable
from .params import validate_params

_VALID_TYPES = frozenset({"lesson", "quiz", "diagnosis", "roadmap", "review", "project"})

def validate_id_format(id_str: str) -> bool:
    """Check if an ID string follows kebab-case format."""
    if not isinstance(id_str, str) or not id_str:
        return False
    return bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", id_str))

def validate_steps(steps: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Validate each step in a DSL definition."""
    errors: list[dict[str, str]] = []
    seen_ids: dict[str, int] = {}

    for i, step in enumerate(steps):
        prefix = f"steps[{i}]"

        if not isinstance(step, dict):
            errors.append(
                {
                    "path": prefix,
                    "message": f"Step na posição {i} deve ser um dicionário",
                    "severity": "error",
                }
            )
            continue

        step_id = step.get("id", f"posicao-{i}")

        if "id" not in step:
            errors.append(
                {
                    "path": f"{prefix}.id",
                    "message": f"Step na posição {i} não possui 'id'",
                    "severity": "error",
                }
            )
        elif not isinstance(step["id"], str):
            errors.append(
                {
                    "path": f"{prefix}.id",
                    "message": f"'id' do step na posição {i} deve ser uma string",
                    "severity": "error",
                }
            )
        else:
            sid = step["id"]
            if not validate_id_format(sid):
                errors.append(
                    {
                        "path": f"{prefix}.id",
                        "message": (
                            f"ID '{sid}' não está em kebab-case"
                            " (apenas letras minúsculas, números e hífens)"
                        ),
                        "severity": "error",
                    }
                )
            if sid in seen_ids:
                errors.append(
                    {
                        "path": f"{prefix}.id",
                        "message": (
                            f"ID duplicado '{sid}' encontrado nos steps {seen_ids[sid]} e {i}"
                        ),
                        "severity": "error",
                    }
                )
            else:
                seen_ids[sid] = i

        if "type" not in step:
            errors.append(
                {
                    "path": f"{prefix}.type",
                    "message": f"Step '{step_id}' não possui 'type'",
                    "severity": "error",
                }
            )
        elif not isinstance(step["type"], str):
            errors.append(
                {
                    "path": f"{prefix}.type",
                    "message": f"'type' do step '{step_id}' deve ser uma string",
                    "severity": "error",
                }
            )
        elif step["type"] not in _VALID_TYPES:
            errors.append(
                {
                    "path": f"{prefix}.type",
                    "message": (
                        f"Tipo inválido '{step['type']}' no step '{step_id}'. "
                        f"Tipos válidos: {', '.join(sorted(_VALID_TYPES))}"
                    ),
                    "severity": "error",
                }
            )

        if "params" not in step:
            errors.append(
                {
                    "path": f"{prefix}.params",
                    "message": f"Step '{step_id}' não possui 'params'",
                    "severity": "error",
                }
            )
        elif not isinstance(step["params"], dict):
            errors.append(
                {
                    "path": f"{prefix}.params",
                    "message": f"'params' do step '{step_id}' deve ser um dicionário",
                    "severity": "error",
                }
            )
        elif not step["params"]:
            errors.append(
                {
                    "path": f"{prefix}.params",
                    "message": f"'params' do step '{step_id}' não pode ser vazio",
                    "severity": "error",
                }
            )
        else:
            step_type = step.get("type", "")
            if step_type in _VALID_TYPES:
                errors.extend(
                    validate_params(
                        step_type, step["params"], step_id, f"{prefix}.params"
                    )
                )

        if "depends_on" in step:
            if not isinstance(step["depends_on"], list):
                errors.append(
                    {
                        "path": f"{prefix}.depends_on",
                        "message": f"'depends_on' do step '{step_id}' deve ser uma lista",
                        "severity": "error",
                    }
                )
            else:
                for dep in step["depends_on"]:
                    if not isinstance(dep, str):
                        errors.append(
                            {
                                "path": f"{prefix}.depends_on",
                                "message": (
                                    f"Item de 'depends_on' no step '{step_id}'"
                                    " deve ser uma string"
                                ),
                                "severity": "error",
                            }
                        )
                    elif dep not in seen_ids:
                        errors.append(
                            {
                                "path": f"{prefix}.depends_on",
                                "message": (
                                    f"Dependência '{dep}' no step '{step_id}'"
                                    " referencia id inexistente"
                                ),
                                "severity": "error",
                            }
                        )
                    elif seen_ids[dep] >= i:
                        errors.append(
                            {
                                "path": f"{prefix}.depends_on",
                                "message": (
                                    f"Dependência futura: step '{step_id}'"
                                    f" depende de '{dep}' que está em posição posterior"
                                ),
                                "severity": "error",
                            }
                        )

    return errors
