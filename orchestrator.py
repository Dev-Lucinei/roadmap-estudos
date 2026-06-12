#!/usr/bin/env python3
"""CLI do Orchestrator Agent para gerenciar task_board.json.

Uso:
  python orchestrator.py update <task_id> <status> "<output_log>" "[result_path]"
  python orchestrator.py ready
  python orchestrator.py status
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any
import logging
logger = logging.getLogger(__name__)


def update_task_status(
    board_path: str,
    task_id: str,
    status: str,
    output_log: str | None = None,
    result_path: str | None = None,
    retry_count: int | None = None,
    clear_output_log: bool = False,
) -> dict[str, Any]:
    """Atualiza o status de uma tarefa no task_board.json."""
    if not os.path.exists(board_path):
        raise FileNotFoundError(f"Task board not found at {board_path}")
    with open(board_path) as f:
        board: dict[str, Any] = json.load(f)
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
        if t.get("status") == "pending" and all(d in completed for d in t.get("dependencies", []))
    ]


BOARD_PATH = "task_board.json"


def cmd_update(args: list[str]) -> None:
    """Executa o comando update: altera status de uma tarefa."""
    if len(args) < 2:
        logger.info("Uso: python orchestrator.py update <task_id> <status> [output_log] [result_path]")
        sys.exit(1)
    task_id = args[0]
    status = args[1]
    output_log = args[2] if len(args) > 2 else ""
    result_path = args[3] if len(args) > 3 else ""
    try:
        board = update_task_status(BOARD_PATH, task_id, status, output_log, result_path)
        logger.info(f"✅ {task_id} → {status}")
        logger.info(f"   last_update: {board['last_update']}")
    except (FileNotFoundError, ValueError, KeyError) as e:
        logger.error(f"❌ Erro: {e}")
        sys.exit(1)


def cmd_ready() -> None:
    """Lista tarefas prontas para delegar (pending com dependências completed)."""
    try:
        with open(BOARD_PATH) as f:
            board = json.load(f)
        ready = get_ready_tasks(board)
        if ready:
            logger.info("📋 Tarefas prontas para delegar:")
            for tid in ready:
                task = next(t for t in board["tasks"] if t["id"] == tid)
                logger.info(
                    f"   {tid} | agente={task.get('assigned_agent', 'TBD')}"
                    f" | input={task.get('input_data', '')}"
                )
        else:
            logger.info("📋 Nenhuma tarefa pronta. Verifique dependências.")
    except FileNotFoundError:
        logger.error(f"❌ task_board.json não encontrado em {BOARD_PATH}")
        sys.exit(1)


def cmd_status() -> None:
    """Exibe o resumo do task_board: contagem por status."""
    try:
        with open(BOARD_PATH) as f:
            board = json.load(f)
    except FileNotFoundError:
        logger.error(f"❌ task_board.json não encontrado em {BOARD_PATH}")
        sys.exit(1)

    counts = {"pending": 0, "in_progress": 0, "completed": 0, "failed": 0}
    for t in board["tasks"]:
        s = t.get("status", "pending")
        counts[s] = counts.get(s, 0) + 1

    logger.info(f"📊 Projeto: {board.get('project_id', 'N/A')}")
    logger.info(f"   Última atualização: {board.get('last_update', 'N/A')}")
    logger.info(f"   ✅ completed: {counts['completed']}")
    logger.info(f"   🔄 in_progress: {counts['in_progress']}")
    logger.info(f"   ⏳ pending: {counts['pending']}")
    logger.error(f"   ❌ failed: {counts['failed']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.info(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command == "update":
        cmd_update(sys.argv[2:])
    elif command == "ready":
        cmd_ready()
    elif command == "status":
        cmd_status()
    else:
        logger.error(f"❌ Comando desconhecido: {command}")
        logger.info(__doc__)
        sys.exit(1)
