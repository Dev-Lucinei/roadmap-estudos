# roadmap-estudos/backend/services/dsl/engine/validate/cycles.py
from typing import Any

def check_cycles(steps: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Detect cycles in step dependency graph using DFS."""
    errors: list[dict[str, str]] = []

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
                    path.append(steps[cur]["id"] if isinstance(steps[cur], dict) else str(cur))
                    cur = parent.get(cur)
                path.append(steps[v]["id"] if isinstance(steps[v], dict) else str(v))
                path.append(steps[u]["id"] if isinstance(steps[u], dict) else str(u))
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
