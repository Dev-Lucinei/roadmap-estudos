# roadmap-estudos/backend/services/dsl/engine/__init__.py
from typing import Any
from .state.context import DSLState
from .validate.validator import DSLValidator
from .execute.executor import DSLExecutor
from .parse.parser import DSLParser

class DSLExecutionEngine:
    """Motor de execução declarativa da DSL.
    
    This class acts as a facade for the underlying parsing, validation, 
    execution, and state management modules.
    """

    def __init__(self) -> None:
        """Initialize the engine with its components."""
        self.state = DSLState()
        self.validator = DSLValidator()
        self.executor = DSLExecutor()
        self.parser = DSLParser()

    @property
    def context(self) -> dict[str, Any]:
        """Maintain backward compatibility for accessing the context."""
        return self.state.context

    def execute(self, dsl: dict[str, Any]) -> dict[str, Any]:
        """Execute a DSL flow after validation.

        Args:
            dsl: Dictionary representing the DSL to execute

        Returns:
            Dictionary with execution status and results
        """
        try:
            parsed_dsl = self.parser.parse(dsl)
        except TypeError as e:
            return {
                "status": "validation_error",
                "errors": [{"path": "", "message": str(e), "severity": "error"}],
            }

        validation = self.validate(parsed_dsl)
        if not validation["valid"]:
            return {
                "status": "validation_error",
                "errors": validation["errors"],
            }

        return self.executor.execute(parsed_dsl, self.state, self)

    def validate(self, dsl: Any) -> dict[str, Any]:
        """Validate a complete DSL definition.

        Args:
            dsl: Dictionary representing the DSL to validate

        Returns:
            Dictionary with keys: valid (bool), errors (list), warnings (list)
        """
        return self.validator.validate(dsl)

    @staticmethod
    def _validate_id_format(id_str: str) -> bool:
        """Backward compatibility for tests.
        
        Note: This requires a DSLValidator instance. 
        Since it's a static method, we'll instantiate a temporary validator.
        """
        return DSLValidator()._validate_id_format(id_str)

    def _execute_step(self, step: dict[str, Any], executed_steps: list[dict[str, Any]], state: DSLState = None) -> dict[str, Any]:
        """Backward compatibility for tests."""
        if state is None:
            state = self.state
        return self.executor._execute_step(step, executed_steps, state, self)

    def _execute_lesson(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Backward compatibility for tests."""
        return self.executor._execute_lesson(step_id, params)

    def _execute_quiz(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Backward compatibility for tests."""
        return self.executor._execute_quiz(step_id, params)

    def _execute_diagnosis(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Backward compatibility for tests."""
        return self.executor._execute_diagnosis(step_id, params)

    def _execute_roadmap(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Backward compatibility for tests."""
        return self.executor._execute_roadmap(step_id, params)

    def _execute_review(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Backward compatibility for tests."""
        return self.executor._execute_review(step_id, params)

    def _execute_project(self, step_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Backward compatibility for tests."""
        return self.executor._execute_project(step_id, params)
