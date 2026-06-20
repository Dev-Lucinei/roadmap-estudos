# roadmap-estudos/backend/services/dsl/engine/validate/params.py
from typing import Any

_VALID_DEPTHS = frozenset({"beginner", "intermediate", "advanced"})

def validate_params(step_type: str, params: dict[str, Any], step_id: str, path: str) -> list[dict[str, str]]:
    """Validate parameters for a specific step type."""
    errors: list[dict[str, str]] = []

    if step_type == "lesson":
        if "topic" not in params:
            errors.append(
                {
                    "path": f"{path}.topic",
                    "message": f"Campo obrigatório 'topic' ausente em step '{step_id}'",
                    "severity": "error",
                }
            )
        elif not isinstance(params["topic"], str) or not params["topic"].strip():
            errors.append(
                {
                    "path": f"{path}.topic",
                    "message": f"'topic' em step '{step_id}' deve ser uma string não vazia",
                    "severity": "error",
                }
            )

    elif step_type == "quiz":
        if "topic" not in params:
            errors.append(
                {
                    "path": f"{path}.topic",
                    "message": f"Campo obrigatório 'topic' ausente em step '{step_id}'",
                    "severity": "error",
                }
            )
        elif not isinstance(params["topic"], str) or not params["topic"].strip():
            errors.append(
                {
                    "path": f"{path}.topic",
                    "message": f"'topic' em step '{step_id}' deve ser uma string não vazia",
                    "severity": "error",
                }
            )

        if "question_count" not in params:
            errors.append(
                {
                    "path": f"{path}.question_count",
                    "message": (
                        f"Campo obrigatório 'question_count' ausente em step '{step_id}'"
                    ),
                    "severity": "error",
                }
            )
        else:
            qc = params["question_count"]
            if isinstance(qc, bool) or not isinstance(qc, int):
                errors.append(
                    {
                        "path": f"{path}.question_count",
                        "message": (
                            f"'question_count' em step '{step_id}' deve ser um inteiro"
                        ),
                        "severity": "error",
                    }
                )
            elif qc < 1 or qc > 20:
                errors.append(
                    {
                        "path": f"{path}.question_count",
                        "message": (
                            f"'question_count' em step '{step_id}' deve estar entre 1 e 20"
                        ),
                        "severity": "error",
                    }
                )

        if "pass_score" in params:
            ps = params["pass_score"]
            if isinstance(ps, bool) or not isinstance(ps, int):
                errors.append(
                    {
                        "path": f"{path}.pass_score",
                        "message": f"'pass_score' em step '{step_id}' deve ser um inteiro",
                        "severity": "error",
                    }
                )
            elif ps < 0 or ps > 100:
                errors.append(
                    {
                        "path": f"{path}.pass_score",
                        "message": f"'pass_score' em step '{step_id}' deve estar entre 0 e 100",
                        "severity": "error",
                    }
                )

    elif step_type == "diagnosis":
        if "topic" not in params:
            errors.append(
                {
                    "path": f"{path}.topic",
                    "message": f"Campo obrigatório 'topic' ausente em step '{step_id}'",
                    "severity": "error",
                }
            )
        elif not isinstance(params["topic"], str) or not params["topic"].strip():
            errors.append(
                {
                    "path": f"{path}.topic",
                    "message": f"'topic' em step '{step_id}' deve ser uma string não vazia",
                    "severity": "error",
                }
            )

    elif step_type == "roadmap":
        if "theme" not in params:
            errors.append(
                {
                    "path": f"{path}.theme",
                    "message": f"Campo obrigatório 'theme' ausente em step '{step_id}'",
                    "severity": "error",
                }
            )
        elif not isinstance(params["theme"], str) or not params["theme"].strip():
            errors.append(
                {
                    "path": f"{path}.theme",
                    "message": f"'theme' em step '{step_id}' deve ser uma string não vazia",
                    "severity": "error",
                }
            )

        if "depth" not in params:
            errors.append(
                {
                    "path": f"{path}.depth",
                    "message": f"Campo obrigatório 'depth' ausente em step '{step_id}'",
                    "severity": "error",
                }
            )
        elif not isinstance(params["depth"], str):
            errors.append(
                {
                    "path": f"{path}.depth",
                    "message": f"'depth' em step '{step_id}' deve ser uma string",
                    "severity": "error",
                }
            )
        elif params["depth"] not in _VALID_DEPTHS:
            errors.append(
                {
                    "path": f"{path}.depth",
                    "message": (
                        f"Profundidade inválida '{params['depth']}'"
                        f" em step '{step_id}'. "
                        f"Valores válidos: {', '.join(sorted(_VALID_DEPTHS))}"
                    ),
                    "severity": "error",
                }
            )

    elif step_type == "review":
        if "topic" not in params:
            errors.append(
                {
                    "path": f"{path}.topic",
                    "message": f"Campo obrigatório 'topic' ausente em step '{step_id}'",
                    "severity": "error",
                }
            )
        elif not isinstance(params["topic"], str) or not params["topic"].strip():
            errors.append(
                {
                    "path": f"{path}.topic",
                    "message": f"'topic' em step '{step_id}' deve ser uma string não vazia",
                    "severity": "error",
                }
            )

    elif step_type == "project":
        if "title" not in params:
            errors.append(
                {
                    "path": f"{path}.title",
                    "message": f"Campo obrigatório 'title' ausente em step '{step_id}'",
                    "severity": "error",
                }
            )
        elif not isinstance(params["title"], str) or not params["title"].strip():
            errors.append(
                {
                    "path": f"{path}.title",
                    "message": f"'title' em step '{step_id}' deve ser uma string não vazia",
                    "severity": "error",
                }
            )

        if "description" in params and not isinstance(params["description"], str):
            errors.append(
                {
                    "path": f"{path}.description",
                    "message": f"'description' em step '{step_id}' deve ser uma string",
                    "severity": "error",
                }
            )

    return errors
