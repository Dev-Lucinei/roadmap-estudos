# roadmap-estudos/backend/services/dsl/engine/parse/parser.py
from typing import Any

class DSLParser:
    """Handles parsing and initial structure verification of DSL input."""

    def parse(self, dsl: Any) -> dict[str, Any]:
        """Ensure the input is a dictionary, which is the expected format for this engine.

        Args:
            dsl: The raw DSL input

        Returns:
            The input as a dictionary

        Raises:
            TypeError: If the input is not a dictionary
        """
        if not isinstance(dsl, dict):
            raise TypeError("DSL must be a dictionary")
        return dsl
