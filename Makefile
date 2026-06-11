# roadmap-estudos/Makefile
.DEFAULT_GOAL := help
SHELL         := /usr/bin/env bash -euo pipefail

.PHONY: help setup dev api front lint format typecheck test harness clean all

help:  ## Mostra esta mensagem de ajuda com todos os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Configuração ────────────────────────────────────────────────────────────────
setup:  ## Instala as dependências backend (uv sync)
	uv sync --dev

# ── Desenvolvimento ─────────────────────────────────────────────────────────────
dev:  ## Inicia backend
	@echo "Iniciando api..."
	@uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Backend iniciado. Frontend é estático (abra frontend/index.html)."
	@wait

api:  ## Inicia apenas a API FastAPI (uvicorn)
	uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

front:  ## O frontend é HTML vanilla, sem dev server necessário
	@echo "Abra o arquivo frontend/index.html no navegador."

# ── Qualidade ───────────────────────────────────────────────────────────────────
lint:  ## Verifica qualidade do código (ruff check + format --check)
	uv run ruff check backend/ tests/
	uv run ruff format --check backend/ tests/

format:  ## Formata o código (ruff format)
	uv run ruff format backend/ tests/
	uv run ruff check --fix backend/ tests/

typecheck:  ## Verifica tipagem estática (mypy)
	uv run mypy backend/ tests/ --no-error-summary

# ── Testes ──────────────────────────────────────────────────────────────────────
test:  ## Executa os testes (pytest)
	uv run pytest -v

# ── Validação ───────────────────────────────────────────────────────────────────
harness:  ## Validação completa do projeto
	uv run python harness.py

# ── Limpeza ─────────────────────────────────────────────────────────────────────
clean:  ## Remove artefatos gerados
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .ruff_cache .pytest_cache

# ── Pipeline completo ───────────────────────────────────────────────────────────
all: lint typecheck test harness
