# roadmap-estudos/backend/services/dsl/engine/execute/executor.py
from typing import Any
from ..state.context import DSLState

class DSLExecutor:
    """Handles the execution of DSL steps."""

    def execute(self, dsl: dict[str, Any], state: DSLState, engine: Any) -> dict[str, Any]:
        """Execute a DSL flow.

        Args:
            dsl: Dictionary representing the DSL to execute
            state: The state object containing context
            engine: The engine instance for handler delegation

        Returns:
            Dictionary with execution status and results
        """
        executed_steps: list[dict[str, Any]] = []
        failed_steps = []

        for step in dsl.get("steps", []):
            result = self._execute_step(step, executed_steps, state, engine)
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
            "context": state.context,
        }

    def _execute_step(
        self, step: dict[str, Any], executed_steps: list[dict[str, Any]], state: DSLState, engine: Any
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

        # Try to use the engine's handler first to support patching in tests
        handler = getattr(engine, f"_execute_{step_type}", None)
        
        if not handler:
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
            state.context[f"{step_id}_result"] = result
            state.context["last_topic"] = params.get("topic", "")
            return {
                "id": step_id,
                "type": step_type,
                "status": "success",
                "result": result,
            }
        except (KeyError, ValueError, TypeError) as e:
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

    def _execute_diagnosis(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
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
