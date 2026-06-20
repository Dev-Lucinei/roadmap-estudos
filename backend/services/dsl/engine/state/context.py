# roadmap-estudos/backend/services/dsl/engine/state/context.py
from typing import Any

class DSLState:
    """Manages the state and context of a DSL execution."""
    def __init__(self) -> None:
        self.context: dict[str, Any] = {}
