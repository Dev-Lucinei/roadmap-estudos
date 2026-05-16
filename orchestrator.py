#!/usr/bin/env python3
"""CLI do Orchestrator Agent para gerenciar task_board.json.

Uso:
  python orchestrator.py update <task_id> <status> "<output_log>" "[result_path]"
  python orchestrator.py ready
  python orchestrator.py status
"""

import json
import sys
import os
from datetime import datetime, timezone

def update_task_status(
    board_path: str,
    task_id: str,
    status: str,
    output_log: str | None = None,
    result_path: str | None = None,
    retry_count: int | None = None,
    clear_output_log: bool = False,
) -> dict:  # type: ignore
    """Atualiza o status de uma tarefa no task_board.json."""
    if not os.path.exists(board_path):
        raise FileNotFoundError(f"Task board not found at {board_path}")
    with open(board_path) as f:
        board = json.load(f)
    task_found = False
    for task in board["tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            task["last_update"] = datetime.now(timezone.utc).isoformat()
            if clear_output_log:
                task["output_log"] = ""
            elif output_log:
                task["output_log"] = output_log
            if result_path:
                task["result_path"] = result_path
            if retry_count is not None:
                task["retry_count"] = retry_count
            task_found = True
            break
    if not task_found:
        raise ValueError(f"Task ID {task_id} not found in task board")
    board["last_update"] = datetime.now(timezone.utc).isoformat()
    with open(board_path, "w") as f:
        json.dump(board, f, indent=2)
    return board


def get_ready_tasks(task_board: dict) -> list[str]:  # type: ignore
    """Retorna IDs de tarefas pendentes com todas as dependências concluídas."""
    completed = {t["id"] for t in task_board["tasks"] if t.get("status") == "completed"}
    return [
        t["id"]
        for t in task_board["tasks"]
        if t.get("status") == "pending"
        and all(d in completed for d in t.get("dependencies", []))
    ]


BOARD_PATH = "task_board.json"


def cmd_update(args: list[str]) -> None:
    """Executa o comando update: altera status de uma tarefa."""
    if len(args) < 2:
        print(
            "Uso: python orchestrator.py update <task_id> <status> [output_log] [result_path]"
        )
        sys.exit(1)
    task_id = args[0]
    status = args[1]
    output_log = args[2] if len(args) > 2 else ""
    result_path = args[3] if len(args) > 3 else ""
    try:
        board = update_task_status(BOARD_PATH, task_id, status, output_log, result_path)
        print(f"✅ {task_id} → {status}")
        print(f"   last_update: {board['last_update']}")
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


def cmd_ready() -> None:
    """Lista tarefas prontas para delegar (pending com dependências completed)."""
    try:
        with open(BOARD_PATH) as f:
            board = json.load(f)
        ready = get_ready_tasks(board)
        if ready:
            print("📋 Tarefas prontas para delegar:")
            for tid in ready:
                task = next(t for t in board["tasks"] if t["id"] == tid)
                print(
                    f"   {tid} | agente={task.get('assigned_agent', 'TBD')} | input={task.get('input_data', '')}"
                )
        else:
            print("📋 Nenhuma tarefa pronta. Verifique dependências.")
    except FileNotFoundError:
        print(f"❌ task_board.json não encontrado em {BOARD_PATH}")
        sys.exit(1)


def cmd_status() -> None:
    """Exibe o resumo do task_board: contagem por status."""
    try:
        with open(BOARD_PATH) as f:
            board = json.load(f)
    except FileNotFoundError:
        print(f"❌ task_board.json não encontrado em {BOARD_PATH}")
        sys.exit(1)

    counts = {"pending": 0, "in_progress": 0, "completed": 0, "failed": 0}
    for t in board["tasks"]:
        s = t.get("status", "pending")
        counts[s] = counts.get(s, 0) + 1

    print(f"📊 Projeto: {board.get('project_id', 'N/A')}")
    print(f"   Última atualização: {board.get('last_update', 'N/A')}")
    print(f"   ✅ completed: {counts['completed']}")
    print(f"   🔄 in_progress: {counts['in_progress']}")
    print(f"   ⏳ pending: {counts['pending']}")
    print(f"   ❌ failed: {counts['failed']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command == "update":
        cmd_update(sys.argv[2:])
    elif command == "ready":
        cmd_ready()
    elif command == "status":
        cmd_status()
    else:
        print(f"❌ Comando desconhecido: {command}")
        print(__doc__)
        sys.exit(1)
