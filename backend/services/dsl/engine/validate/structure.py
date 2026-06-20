# roadmap-estudos/backend/services/dsl/engine/validate/structure.py
import re
from typing import Any

def validate_structure(dsl: dict[str, Any]) -> list[dict[str, str]]:
    """Validate the root structure of a DSL definition."""
    errors: list[dict[str, str]] = []

    if "version" not in dsl:
        errors.append(
            {
                "path": "version",
                "message": "Campo obrigatório 'version' ausente",
                "severity": "error",
            }
        )
    elif not isinstance(dsl["version"], str):
        errors.append(
            {
                "path": "version",
                "message": "'version' deve ser uma string",
                "severity": "error",
            }
        )
    elif not re.match(r"^\d+\.\d+$", dsl["version"]):
        errors.append(
            {
                "path": "version",
                "message": (
                    f"Formato de 'version' inválido: '{dsl['version']}'."
                    " Deve ser 'X.Y' (major.minor)"
                ),
                "severity": "error",
            }
        )

    if "name" not in dsl:
        errors.append(
            {
                "path": "name",
                "message": "Campo obrigatório 'name' ausente",
                "severity": "error",
            }
        )
    elif not isinstance(dsl["name"], str) or not dsl["name"].strip():
        errors.append(
            {
                "path": "name",
                "message": "'name' deve ser uma string não vazia",
                "severity": "error",
            }
        )

    if "description" in dsl and not isinstance(dsl["description"], str):
        errors.append(
            {
                "path": "description",
                "message": "'description' deve ser uma string",
                "severity": "error",
            }
        )

    if "steps" not in dsl:
        errors.append(
            {
                "path": "steps",
                "message": "Campo obrigatório 'steps' ausente",
                "severity": "error",
            }
        )
    elif not isinstance(dsl["steps"], list):
        errors.append(
            {
                "path": "steps",
                "message": "'steps' deve ser uma lista",
                "severity": "error",
            }
        )
    elif not dsl["steps"]:
        errors.append(
            {
                "path": "steps",
                "message": "'steps' deve conter pelo menos um step",
                "severity": "error",
            }
        )

    return errors
