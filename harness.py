#!/usr/bin/env python3
"""Roadmap-Estudos Validation Harness — Agent-Ready Edition."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from harness_core import HarnessConfig, StepResult, ValidationHarness

CONFIG = HarnessConfig(
    src_dir="backend",
    required_files=[
        "pyproject.toml",
        "README.md",
        "backend/main.py",
        "backend/core/config.py",
        "backend/api/routes.py",
    ],
    required_dirs=[
        "tests",
        "scripts",
        "docs",
        "skill",
        "data",
        "licoes",
        "backend",
        "frontend",
    ],
    protected_files=["harness.py", "scripts/guard_harness.py"],
    harness_name="Roadmap-Estudos Validation Harness",
    extra_steps=["content"],
)


class RoadmapHarness(ValidationHarness):
    """Harness customizado com validação de conteúdo."""

    def run_content(self) -> None:
        """Verifica formato de roadmaps e lições gerados."""
        import time

        from harness_core import ValidationError

        start = time.time()
        errors: list[ValidationError] = []

        try:
            sys.path.insert(0, str(self.base_dir / "scripts"))
            from validate_content_format import ContentValidator

            validator = ContentValidator()
            validator.validate_all()

            for error_msg in validator.errors:
                if ":" in error_msg:
                    parts = error_msg.split(":", 2)
                    file = parts[1].strip() if len(parts) > 1 else "unknown"
                    message = parts[2].strip() if len(parts) > 2 else error_msg
                else:
                    file = "unknown"
                    message = error_msg

                errors.append(
                    ValidationError(
                        type="content",
                        severity="error",
                        file=file,
                        line=None,
                        column=None,
                        code="CONTENT_FORMAT",
                        message=message,
                        fix_instruction=self._get_content_fix_instruction(message),
                        fix_example=None,
                        auto_fixable=False,
                        auto_fix_command=None,
                    )
                )

            for warning_msg in validator.warnings:
                if ":" in warning_msg:
                    parts = warning_msg.split(":", 2)
                    file = parts[1].strip() if len(parts) > 1 else "unknown"
                    message = parts[2].strip() if len(parts) > 2 else warning_msg
                else:
                    file = "unknown"
                    message = warning_msg

                errors.append(
                    ValidationError(
                        type="content",
                        severity="warning",
                        file=file,
                        line=None,
                        column=None,
                        code="CONTENT_WARNING",
                        message=message,
                        fix_instruction=self._get_content_fix_instruction(message),
                        fix_example=None,
                        auto_fixable=False,
                        auto_fix_command=None,
                    )
                )

        except ImportError as e:
            errors.append(
                ValidationError(
                    type="content",
                    severity="error",
                    file="scripts/validate_content_format.py",
                    line=None,
                    column=None,
                    code="VALIDATOR_MISSING",
                    message=f"Validador de conteúdo não encontrado: {e}",
                    fix_instruction="Verificar se scripts/validate_content_format.py existe",
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )
        except Exception as e:
            errors.append(
                ValidationError(
                    type="content",
                    severity="error",
                    file="scripts/validate_content_format.py",
                    line=None,
                    column=None,
                    code="VALIDATOR_ERROR",
                    message=f"Erro ao executar validador: {e}",
                    fix_instruction="Verificar logs do validador para detalhes",
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )

        duration = int((time.time() - start) * 1000)
        is_fail = any(e.severity == "error" for e in errors)
        result = StepResult(
            step="content",
            status="success" if not is_fail else "fail",
            exit_code=0 if not is_fail else 1,
            duration_ms=duration,
            stdout="Validados roadmaps e lições",
            stderr="",
            errors=errors,
        )
        self.results.append(result)

    def _get_content_fix_instruction(self, message: str) -> str:
        """Retorna instrução de correção baseada na mensagem de erro."""
        if "deve começar com 'roadmap_'" in message:
            return "Renomear arquivo para seguir padrão roadmap_*.json"
        elif "contém caracteres inválidos" in message:
            return "Remover acentos e caracteres especiais do nome do arquivo"
        elif "falta campo" in message:
            return "Adicionar campo obrigatório ao JSON"
        elif "ID" in message and "inválido" in message:
            return "Converter ID para kebab-case (apenas a-z, 0-9, -, _)"
        elif "não contém quiz embutido" in message:
            return "Adicionar bloco ```json com quiz de 3+ perguntas ao final do arquivo"
        elif "quiz tem menos de 3 perguntas" in message:
            return "Adicionar mais perguntas ao quiz (mínimo 3)"
        elif "deve ter exatamente 4 opções" in message:
            return "Ajustar pergunta para ter exatamente 4 alternativas"
        elif "'answer' deve ser 0-3" in message:
            return "Corrigir campo 'answer' para índice válido (0, 1, 2 ou 3)"
        else:
            return "Corrigir formato conforme documentação em docs/PADROES_FORMATO_CONTEUDO.md"

    def run_all(self) -> None:
        super().run_all()
        self.run_content()


def main() -> None:
    harness = RoadmapHarness(CONFIG, Path(__file__).resolve().parent)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    dispatch = {
        "all": harness.run_all,
        "content": harness.run_content,
        "lint": harness.run_lint,
        "type": harness.run_typecheck,
        "test": harness.run_tests,
        "audit": harness.run_audit,
        "security": harness.run_security,
        "structure": harness.run_structure,
    }

    if cmd == "json":
        harness.run_all()
        harness.print_json()
        return

    if cmd in dispatch:
        dispatch[cmd]()
    else:
        print(f"Comando desconhecido: '{cmd}'")
        print(f"Disponíveis: {', '.join(dispatch.keys())}, json")
        sys.exit(1)

    harness.print_human()
    sys.exit(0 if harness.report()["status"] == "healthy" else 1)


if __name__ == "__main__":
    main()
