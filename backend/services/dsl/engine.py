"""DSL Execution Engine for Roadmap Estudos."""

import re
from typing import Any

_VALID_TYPES = frozenset(
    {"lesson", "quiz", "diagnosis", "roadmap", "review", "project"}
)
_VALID_DEPTHS = frozenset({"beginner", "intermediate", "advanced"})


class DSLExecutionEngine:
    """Motor de execução declarativa da DSL."""

    def __init__(self) -> None:
        """Initialize the engine with an empty context."""
        self.context: dict[str, Any] = {}

    def execute(self, dsl: dict[str, Any]) -> dict[str, Any]:
        """Execute a DSL flow after validation.

        Args:
            dsl: Dictionary representing the DSL to execute

        Returns:
            Dictionary with execution status and results
        """
        validation = self.validate(dsl)
        if not validation["valid"]:
            return {
                "status": "validation_error",
                "errors": validation["errors"],
            }

        executed_steps: list[dict[str, Any]] = []
        failed_steps = []

        for step in dsl.get("steps", []):
            result = self._execute_step(step, executed_steps)
            if result["status"] == "success":
                executed_steps.append(result)
            else:
                failed_steps.append(result)
                break

        return {
            "status": "completed" if not failed_steps else "partial",
            "steps_count": len(dsl.get("steps", [])),
            "executed_steps": executed_steps,
            "failed_steps": failed_steps,
            "context": self.context,
        }

    def _execute_step(
        self, step: dict[str, Any], executed_steps: list[dict[str, Any]]
    ) -> dict[str, Any]:
        step_type = step["type"]
        step_id = step["id"]
        params = step.get("params", {})

        for dep_id in step.get("depends_on", []):
            if not any(s["id"] == dep_id for s in executed_steps):
                return {
                    "id": step_id,
                    "type": step_type,
                    "status": "skipped",
                    "reason": f"Dependência '{dep_id}' não foi executada",
                }

        handlers = {
            "lesson": self._execute_lesson,
            "quiz": self._execute_quiz,
            "diagnosis": self._execute_diagnosis,
            "roadmap": self._execute_roadmap,
            "review": self._execute_review,
            "project": self._execute_project,
        }

        handler = handlers.get(step_type)
        if not handler:
            return {
                "id": step_id,
                "type": step_type,
                "status": "failed",
                "error": f"Unknown type: {step_type}",
            }

        try:
            result = handler(step_id, params)
            self.context[f"{step_id}_result"] = result
            self.context["last_topic"] = params.get("topic", "")
            return {
                "id": step_id,
                "type": step_type,
                "status": "success",
                "result": result,
            }
        except Exception as e:
            return {
                "id": step_id,
                "type": step_type,
                "status": "failed",
                "error": str(e),
            }

    def _execute_lesson(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "topic": params.get("topic", ""),
            "difficulty": params.get("difficulty", "medium"),
            "duration_minutes": params.get("duration_minutes", 30),
            "content_generated": False,
            "note": "Implementação real requer OPENROUTER_API_KEY",
        }

    def _execute_quiz(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "topic": params.get("topic", ""),
            "question_count": params.get("question_count", 5),
            "pass_score": params.get("pass_score", 70),
            "questions_generated": False,
        }

    def _execute_diagnosis(
        self, step_id: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "topic": params.get("topic", ""),
            "prerequisites_checked": params.get("prerequisites", []),
        }

    def _execute_roadmap(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "theme": params.get("theme", ""),
            "depth": params.get("depth", "intermediate"),
        }

    def _execute_review(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "topic": params.get("topic", ""),
        }

    def _execute_project(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": params.get("title", ""),
            "description": params.get("description", ""),
        }

    def validate(self, dsl: Any) -> dict[str, Any]:
        """Validate a complete DSL definition.

        Args:
            dsl: Dictionary representing the DSL to validate

        Returns:
            Dictionary with keys: valid (bool), errors (list), warnings (list)
        """
        if not isinstance(dsl, dict):
            return {
                "valid": False,
                "errors": [
                    {
                        "path": "",
                        "message": "DSL deve ser um dicionário",
                        "severity": "error",
                    }
                ],
                "warnings": [],
            }

        errors: list[dict] = []
        warnings: list[dict] = []

        errors.extend(self._validate_structure(dsl))

        if "steps" in dsl and isinstance(dsl["steps"], list) and dsl["steps"]:
            errors.extend(self._validate_steps(dsl["steps"]))
            errors.extend(self._check_cycles(dsl["steps"]))

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def _validate_structure(self, dsl: dict) -> list[dict]:
        """Validate the root structure of a DSL definition.

        Args:
            dsl: Dictionary representing the DSL

        Returns:
            List of validation errors found
        """
        errors: list[dict] = []

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
                    "message": f"Formato de 'version' inválido: '{dsl['version']}'. Deve ser 'X.Y' (major.minor)",
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

    def _validate_steps(self, steps: list) -> list[dict]:
        """Validate each step in a DSL definition.

        Args:
            steps: List of step dictionaries

        Returns:
            List of validation errors found
        """
        errors: list[dict] = []
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
                if not self._validate_id_format(sid):
                    errors.append(
                        {
                            "path": f"{prefix}.id",
                            "message": f"ID '{sid}' não está em kebab-case (apenas letras minúsculas, números e hífens)",
                            "severity": "error",
                        }
                    )
                if sid in seen_ids:
                    errors.append(
                        {
                            "path": f"{prefix}.id",
                            "message": f"ID duplicado '{sid}' encontrado nos steps {seen_ids[sid]} e {i}",
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
                        "message": f"Tipo inválido '{step['type']}' no step '{step_id}'. Tipos válidos: {', '.join(sorted(_VALID_TYPES))}",
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
                        self._validate_params(
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
                                    "message": f"Item de 'depends_on' no step '{step_id}' deve ser uma string",
                                    "severity": "error",
                                }
                            )
                        elif dep not in seen_ids:
                            errors.append(
                                {
                                    "path": f"{prefix}.depends_on",
                                    "message": f"Dependência '{dep}' no step '{step_id}' referencia id inexistente",
                                    "severity": "error",
                                }
                            )
                        elif seen_ids[dep] >= i:
                            errors.append(
                                {
                                    "path": f"{prefix}.depends_on",
                                    "message": f"Dependência futura: step '{step_id}' depende de '{dep}' que está em posição posterior",
                                    "severity": "error",
                                }
                            )

        return errors

    def _validate_params(
        self, step_type: str, params: dict, step_id: str, path: str
    ) -> list[dict]:
        """Validate parameters for a specific step type.

        Args:
            step_type: Type of the step
            params: Parameters dictionary
            step_id: ID of the step
            path: JSON path prefix for error reporting

        Returns:
            List of validation errors found
        """
        errors: list[dict] = []

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
                        "message": f"Campo obrigatório 'question_count' ausente em step '{step_id}'",
                        "severity": "error",
                    }
                )
            else:
                qc = params["question_count"]
                if isinstance(qc, bool) or not isinstance(qc, int):
                    errors.append(
                        {
                            "path": f"{path}.question_count",
                            "message": f"'question_count' em step '{step_id}' deve ser um inteiro",
                            "severity": "error",
                        }
                    )
                elif qc < 1 or qc > 20:
                    errors.append(
                        {
                            "path": f"{path}.question_count",
                            "message": f"'question_count' em step '{step_id}' deve estar entre 1 e 20",
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
                        "message": f"Profundidade inválida '{params['depth']}' em step '{step_id}'. Valores válidos: {', '.join(sorted(_VALID_DEPTHS))}",
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

    def _check_cycles(self, steps: list) -> list[dict]:
        """Detect cycles in step dependency graph using DFS.

        Args:
            steps: List of step dictionaries

        Returns:
            List of validation errors for cycles found
        """
        errors: list[dict] = []

        id_to_idx: dict[str, int] = {}
        for i, step in enumerate(steps):
            if isinstance(step, dict) and isinstance(step.get("id"), str):
                id_to_idx[step["id"]] = i

        n = len(steps)
        WHITE, GRAY, BLACK = 0, 1, 2
        color: list[int] = [WHITE] * n
        parent: dict[int, int] = {}

        adj: list[list[int]] = [[] for _ in range(n)]
        for i, step in enumerate(steps):
            if (
                isinstance(step, dict)
                and "depends_on" in step
                and isinstance(step["depends_on"], list)
            ):
                for dep in step["depends_on"]:
                    if isinstance(dep, str) and dep in id_to_idx:
                        adj[i].append(id_to_idx[dep])

        cycles: list[list[str]] = []

        def dfs(u: int) -> None:
            """Execute a depth-first search to detect cycles in the dependency graph."""
            color[u] = GRAY
            for v in adj[u]:
                if color[v] == GRAY:
                    path: list[str] = []
                    cur: int | None = u
                    while cur is not None and cur != v:
                        path.append(
                            steps[cur]["id"]
                            if isinstance(steps[cur], dict)
                            else str(cur)
                        )
                        cur = parent.get(cur)
                    path.append(
                        steps[v]["id"] if isinstance(steps[v], dict) else str(v)
                    )
                    path.append(
                        steps[u]["id"] if isinstance(steps[u], dict) else str(u)
                    )
                    path.reverse()
                    cycles.append(path)
                elif color[v] == WHITE:
                    parent[v] = u
                    dfs(v)
            color[u] = BLACK

        for i in range(n):
            if color[i] == WHITE:
                parent.clear()
                parent[i] = -1
                dfs(i)

        for path in cycles:
            errors.append(
                {
                    "path": "steps",
                    "message": f"Ciclo de dependência detectado: {' -> '.join(path)}",
                    "severity": "error",
                }
            )

        return errors

    @staticmethod
    def _validate_id_format(id_str: str) -> bool:
        """Check if an ID string follows kebab-case format.

        Args:
            id_str: The ID string to validate

        Returns:
            True if the ID is valid kebab-case, False otherwise
        """
        if not isinstance(id_str, str) or not id_str:
            return False
        return bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", id_str))
