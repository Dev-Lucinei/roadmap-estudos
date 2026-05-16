#!/usr/bin/env python3
"""
Roadmap-Estudos Validation Harness — Agent-Ready Edition.

Executa todas as validações do projeto e gera um relatório completo
com plano de ação detalhado para agentes de IA corrigirem erros
sem intervenção humana adicional.

Uso:
    python harness.py            → todas as validações (saída humana)
    python harness.py json       → todas as validações (saída JSON para agentes)
    python harness.py lint       → apenas lint + format
    python harness.py type       → apenas type check
    python harness.py test       → apenas testes
    python harness.py audit      → apenas auditoria de arquitetura
    python harness.py security   → apenas verificações de segurança
    python harness.py structure  → apenas estrutura de arquivos
    python harness.py content    → apenas validação de formato de conteúdo (roadmaps/lições)
"""

import ast
import hashlib
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# =============================================================================
# CONSTANTES E CONFIGURAÇÃO
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent
# Para este projeto, o código fonte está em backend/
SRC_DIR = BASE_DIR / "backend"
TESTS_DIR = BASE_DIR / "tests"

# Arquivos protegidos contra modificação por agentes
HASH_FILE = BASE_DIR / ".harness.hash"
PROTECTED_FILES: list[str] = [
    "harness.py",
    "scripts/guard_harness.py",
]

# Estrutura obrigatória do projeto (ajustado para Roadmap-Estudos)
REQUIRED_FILES = [
    "pyproject.toml",
    "README.md",
    "backend/main.py",
    "backend/core/config.py",
    "backend/api/routes.py",
]

REQUIRED_DIRS = [
    "tests",
    "scripts",
    "docs",
    "skill",
    "data",
    "licoes",
    "backend",
    "frontend",
]

# Padrões proibidos por segurança
FORBIDDEN_PATTERNS: list[tuple[str, str, str]] = [
    # (padrão_regex, descrição, sugestão)
    (
        r"\beval\s*\(",
        "Uso de eval() detectado — risco de injeção de código",
        "Substituir eval() por ast.literal_eval() ou lógica explícita",
    ),
    (
        r"\bexec\s*\(",
        "Uso de exec() detectado — risco de execução arbitrária",
        "Refatorar para não usar exec(); use funções explícitas",
    ),
    (
        r"__import__\s*\(",
        "Uso de __import__() detectado — carregamento dinâmico inseguro",
        "Usar importlib.import_module() com validação de nome",
    ),
    (
        r"subprocess\.call\s*\(.*shell\s*=\s*True",
        "subprocess com shell=True — risco de injeção de shell",
        "Usar lista de argumentos e shell=False (padrão)",
    ),
    (
        r"os\.system\s*\(",
        "Uso de os.system() detectado — preferir subprocess",
        "Substituir por subprocess.run() com lista de argumentos",
    ),
    (
        r"pickle\.loads?\s*\(",
        "Deserialização com pickle — risco de execução de código",
        "Usar json.loads() ou outro formato seguro de serialização",
    ),
    (
        r"yaml\.load\s*\([^,)]+\)",
        "yaml.load() sem Loader — risco de execução de código",
        "Usar yaml.safe_load() ou yaml.load(data, Loader=yaml.SafeLoader)",
    ),
    (
        r"(password|secret|token|api_key)\s*=\s*['\"][^'\"]{4,}['\"]",
        "Credencial hardcoded detectada",
        "Mover para variável de ambiente: os.getenv('SECRET_NAME')",
    ),
]

# Mapa completo de sugestões para códigos Ruff
RUFF_SUGGESTIONS: dict[str, dict[str, str]] = {
    # Pyflakes (F)
    "F401": {
        "fix": "Remover o import não utilizado ou adicionar ao __all__ se for re-exportação",
        "example": "# Remover: import os  →  (deletar linha)",
        "auto_fixable": "true",
    },
    "F811": {
        "fix": "Remover definição duplicada; manter apenas a última ou renomear",
        "auto_fixable": "false",
    },
    "F841": {
        "fix": "Remover a variável local não utilizada ou usar _ como nome",
        "example": "result = calc()  →  _ = calc()  ou remover linha",
        "auto_fixable": "false",
    },
    "F821": {
        "fix": "Definir o nome antes do uso ou importar o módulo correto",
        "auto_fixable": "false",
    },
    # pycodestyle (E/W)
    "E501": {
        "fix": "Quebrar linha para máximo 88 caracteres usando parênteses ou barra invertida",
        "example": "long_call(arg1, arg2)  →  long_call(\n    arg1,\n    arg2,\n)",
        "auto_fixable": "false",
    },
    "E302": {
        "fix": "Adicionar 2 linhas em branco antes de definição de função/classe de nível superior",
        "auto_fixable": "true",
    },
    "E303": {
        "fix": "Reduzir para no máximo 2 linhas em branco consecutivas",
        "auto_fixable": "true",
    },
    "E711": {
        "fix": "Usar 'is None' ou 'is not None' em vez de == None",
        "example": "if x == None  →  if x is None",
        "auto_fixable": "true",
    },
    "E712": {
        "fix": "Usar 'is True/False' ou comparação booleana direta",
        "example": "if x == True  →  if x",
        "auto_fixable": "true",
    },
    "W291": {
        "fix": "Remover espaços em branco no final da linha",
        "auto_fixable": "true",
    },
    "W293": {
        "fix": "Remover espaços em branco em linha em branco",
        "auto_fixable": "true",
    },
    # isort (I)
    "I001": {
        "fix": (
            "Reordenar imports: stdlib → third-party → local, cada "
            "grupo separado por\\n               linha em branco"
        ),
        "auto_fixable": "true",
    },
    # pep8-naming (N)
    "N801": {
        "fix": "Renomear classe para CapWords (PascalCase): class minha_classe → class MinhaClasse",
        "auto_fixable": "false",
    },
    "N802": {
        "fix": "Renomear função para snake_case: def MinhaFuncao → def minha_funcao",
        "auto_fixable": "false",
    },
    "N803": {
        "fix": "Renomear argumento para snake_case",
        "auto_fixable": "false",
    },
    "N806": {
        "fix": "Renomear variável local para snake_case (não SCREAMING_SNAKE dentro de funções)",
        "auto_fixable": "false",
    },
    # flake8-bugbear (B)
    "B006": {
        "fix": "Não usar objeto mutável (lista/dict) como valor padrão de argumento",
        "example": "def f(x=[])  →  def f(x=None):\n    if x is None: x = []",
        "auto_fixable": "false",
    },
    "B007": {
        "fix": "Variável de loop não usada no corpo; renomear para _ se intencional",
        "auto_fixable": "false",
    },
    "B008": {
        "fix": "Não chamar função como valor padrão de argumento",
        "example": "def f(x=datetime.now())  →  def f(x=None):\n"
        "    if x is None: x = datetime.now()",
        "auto_fixable": "false",
    },
    # flake8-simplify (SIM)
    "SIM102": {
        "fix": "Combinar ifs aninhados em um único if com 'and'",
        "example": "if a:\n  if b:  →  if a and b:",
        "auto_fixable": "false",
    },
    "SIM108": {
        "fix": "Usar operador ternário em vez de if/else de atribuição",
        "example": "if c: x=a\nelse: x=b  →  x = a if c else b",
        "auto_fixable": "false",
    },
    # Ruff-specific (RUF)
    "RUF100": {
        "fix": "Remover diretiva '# noqa' que não suprime nenhum aviso",
        "auto_fixable": "true",
    },
}

# Sugestões para erros MyPy
MYPY_PATTERNS: list[tuple[str, str, str]] = [
    (
        r"has no attribute",
        "Atributo inexistente no tipo inferido",
        "Verificar se o objeto é do tipo correto; adicionar cast() ou type guard se necessário",
    ),
    (
        r"Argument .* has incompatible type",
        "Tipo de argumento incompatível",
        "Ajustar o tipo do argumento para o tipo esperado pela função ou usar Union/Optional",
    ),
    (
        r"Incompatible return value type",
        "Tipo de retorno incompatível com anotação",
        "Corrigir o valor retornado ou atualizar a anotação de retorno da função",
    ),
    (
        r"Name .* is not defined",
        "Nome não definido no escopo",
        "Importar o símbolo faltante ou verificar erro de digitação",
    ),
    (
        r"Missing return statement",
        "Função pode retornar None implicitamente",
        "Adicionar return explícito em todos os caminhos ou anotar retorno como Optional",
    ),
    (
        r"Cannot determine type",
        "Tipo não pode ser inferido",
        "Adicionar anotação de tipo explícita à variável",
    ),
    (
        r'Item "None" of .* has no attribute',
        "Possível None não verificado antes de acesso",
        "Adicionar verificação 'if x is not None:' antes do acesso ou usar assert",
    ),
]


# =============================================================================
# ESTRUTURAS DE DADOS
# =============================================================================


@dataclass
class ValidationError:
    """Erro detectado durante validação, com contexto completo para agentes."""

    type: str  # lint | type | test | security | structure | audit | dsl
    severity: str  # error | warning
    file: str
    line: int | None
    column: int | None
    code: str | None
    message: str
    # Campos para o agente agir
    fix_instruction: str  # O que fazer (instrução precisa)
    fix_example: str | None  # Exemplo concreto de antes/depois
    auto_fixable: bool  # Pode ser corrigido automaticamente (ex: ruff --fix)
    auto_fix_command: str | None  # Comando exato para auto-correção


@dataclass
class StepResult:
    """Resultado de um passo de validação."""

    step: str
    status: str  # success | fail | skip
    exit_code: int
    duration_ms: int
    stdout: str
    stderr: str
    errors: list[ValidationError] = field(default_factory=list)
    tool_missing: bool = False


# =============================================================================
# HARNESS PRINCIPAL
# =============================================================================


class ValidationHarness:
    """
    Orquestrador de validações do SkillHub com saída acionável para agentes.

    Cada step gera erros estruturados com instruções precisas de correção,
    permitindo que um agente de IA resolva todos os problemas sem perguntar
    ao usuário como agir.
    """

    def __init__(self) -> None:
        self.results: list[StepResult] = []
        self.start_time = time.time()

    # =========================================================
    # EXECUTOR BASE
    # =========================================================

    def _run_command(
        self,
        name: str,
        command: list[str],
        cwd: Path | None = None,
    ) -> StepResult:
        """Executa um comando e retorna StepResult estruturado."""
        start = time.time()
        working_dir = cwd or BASE_DIR

        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=working_dir,
            )
            duration = int((time.time() - start) * 1000)

            result = StepResult(
                step=name,
                status="success" if proc.returncode == 0 else "fail",
                exit_code=proc.returncode,
                duration_ms=duration,
                stdout=proc.stdout,
                stderr=proc.stderr,
            )

        except FileNotFoundError:
            result = StepResult(
                step=name,
                status="skip",
                exit_code=-1,
                duration_ms=int((time.time() - start) * 1000),
                stdout="",
                stderr=f"Ferramenta não encontrada: {command[0]}",
                tool_missing=True,
            )
        except Exception as exc:
            result = StepResult(
                step=name,
                status="fail",
                exit_code=-1,
                duration_ms=int((time.time() - start) * 1000),
                stdout="",
                stderr=str(exc),
            )

        self.results.append(result)
        return result

    # =========================================================
    # PARSERS DE ERROS
    # =========================================================

    def _parse_ruff_errors(self, output: str) -> list[ValidationError]:
        """Extrai erros do ruff com sugestões de correção detalhadas."""
        errors: list[ValidationError] = []
        pattern = r"(.+\.py):(\d+):(\d+):\s+([A-Z]+\d+)\s+(.*)"

        for match in re.findall(pattern, output):
            file, line, col, code, message = match
            suggestion = RUFF_SUGGESTIONS.get(code, {})

            fix_instruction = suggestion.get(
                "fix", f"Corrigir violação {code}: {message}"
            )
            fix_example = suggestion.get("example")
            auto_fixable_str = suggestion.get("auto_fixable", "false")
            auto_fixable = auto_fixable_str == "true"

            errors.append(
                ValidationError(
                    type="lint",
                    severity="error",
                    file=file,
                    line=int(line),
                    column=int(col),
                    code=code,
                    message=message,
                    fix_instruction=fix_instruction,
                    fix_example=fix_example,
                    auto_fixable=auto_fixable,
                    auto_fix_command="ruff check --fix ." if auto_fixable else None,
                )
            )

        return errors

    def _parse_ruff_format_errors(self, output: str) -> list[ValidationError]:
        """Detecta arquivos que precisam de formatação."""
        errors: list[ValidationError] = []

        for line in output.splitlines():
            if "Would reformat" in line or "would reformat" in line:
                # extrai o nome do arquivo da linha
                parts = line.split()
                file = parts[-1] if parts else "arquivo desconhecido"
                errors.append(
                    ValidationError(
                        type="format",
                        severity="error",
                        file=file,
                        line=None,
                        column=None,
                        code="FORMAT",
                        message=f"Arquivo precisa de formatação: {file}",
                        fix_instruction="Executar 'ruff format .' para formatar todos os arquivos\n"
                        " automaticamente",
                        fix_example=None,
                        auto_fixable=True,
                        auto_fix_command="ruff format .",
                    )
                )

        if (
            not errors
            and "reformatted" not in output
            and "would reformat" in output.lower()
        ):
            errors.append(
                ValidationError(
                    type="format",
                    severity="error",
                    file=".",
                    line=None,
                    column=None,
                    code="FORMAT",
                    message="Arquivos precisam de formatação",
                    fix_instruction="Executar 'ruff format .' para reformatar o projeto",
                    fix_example=None,
                    auto_fixable=True,
                    auto_fix_command="ruff format .",
                )
            )

        return errors

    def _parse_mypy_errors(self, output: str) -> list[ValidationError]:
        """Extrai erros do mypy com sugestões contextuais."""
        errors: list[ValidationError] = []
        pattern = r"(.+\.py):(\d+):(?:\d+:)?\s+(error|warning|note):\s+(.*)"

        for match in re.findall(pattern, output):
            file, line, level, message = match

            # encontrar sugestão contextual
            fix_instruction = "Corrigir o erro de tipagem indicado pelo mypy"
            for pattern_str, _desc, suggestion in MYPY_PATTERNS:
                if re.search(pattern_str, message, re.IGNORECASE):
                    fix_instruction = suggestion
                    break

            severity = "error" if level == "error" else "warning"

            errors.append(
                ValidationError(
                    type="type",
                    severity=severity,
                    file=file,
                    line=int(line),
                    column=None,
                    code="MYPY",
                    message=message,
                    fix_instruction=fix_instruction,
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )

        return errors

    def _parse_pytest_errors(self, output: str) -> list[ValidationError]:
        """Extrai falhas de testes com contexto de correção."""
        errors: list[ValidationError] = []

        # Captura linhas FAILED com nome do teste
        failed_pattern = r"FAILED\s+([\w/\.]+\.py)::(\w+(?:::\w+)?)"
        for match in re.findall(failed_pattern, output):
            file, test_name = match
            errors.append(
                ValidationError(
                    type="test",
                    severity="error",
                    file=file,
                    line=None,
                    column=None,
                    code="PYTEST_FAIL",
                    message=f"Teste falhou: {test_name}",
                    fix_instruction=(
                        f"1. Executar 'pytest {file}::{test_name} -v' para ver o traceback. "
                        f"2. Identificar a assertion que falhou. "
                        f"3. Corrigir o código em src/ ou atualizar o teste se o "
                        "comportamento esperado mudou."
                    ),
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=f"pytest {file}::{test_name} -v --tb=long",
                )
            )

        # Captura erros de coleta (import errors, etc.)
        error_pattern = r"ERROR\s+([\w/\.]+\.py)"
        for match in re.findall(error_pattern, output):
            file = match
            errors.append(
                ValidationError(
                    type="test",
                    severity="error",
                    file=file,
                    line=None,
                    column=None,
                    code="PYTEST_ERROR",
                    message=f"Erro ao coletar/importar: {file}",
                    fix_instruction=(
                        "1. Verificar erros de importação no arquivo. "
                        "2. Executar 'python -c \"import <módulo>\"' para checar imports. "
                        "3. Corrigir dependências faltantes ou erros de sintaxe."
                    ),
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=f"pytest {file} -v --tb=short",
                )
            )

        # Se falhou mas sem matches específicos
        if not errors and ("FAILED" in output or "error" in output.lower()):
            errors.append(
                ValidationError(
                    type="test",
                    severity="error",
                    file="tests/",
                    line=None,
                    column=None,
                    code="PYTEST_FAIL",
                    message="Falha na suíte de testes",
                    fix_instruction=(
                        "Executar 'pytest -v --tb=long' para ver detalhes completos das falhas "
                        "e corrigir cada teste individualmente."
                    ),
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command="pytest -v --tb=long",
                )
            )

        return errors

    # =========================================================
    # VALIDAÇÃO DE ESTRUTURA (sem subprocess)
    # =========================================================

    def _check_project_structure(self) -> StepResult:
        """Verifica estrutura obrigatória de arquivos e diretórios."""
        start = time.time()
        errors: list[ValidationError] = []

        for required_file in REQUIRED_FILES:
            path = BASE_DIR / required_file
            if not path.exists():
                errors.append(
                    ValidationError(
                        type="structure",
                        severity="error",
                        file=str(path.relative_to(BASE_DIR)),
                        line=None,
                        column=None,
                        code="MISSING_FILE",
                        message=f"Arquivo obrigatório não encontrado: {required_file}",
                        fix_instruction=(
                            f"Criar o arquivo '{required_file}' com o conteúdo "
                            "adequado ao seu papel no projeto"
                        ),
                        fix_example=self._structure_fix_example(required_file),
                        auto_fixable=False,
                        auto_fix_command=None,
                    )
                )

        for required_dir in REQUIRED_DIRS:
            path = BASE_DIR / required_dir
            if not path.exists():
                errors.append(
                    ValidationError(
                        type="structure",
                        severity="error",
                        file=str(path.relative_to(BASE_DIR)),
                        line=None,
                        column=None,
                        code="MISSING_DIR",
                        message=f"Diretório obrigatório não encontrado: {required_dir}",
                        fix_instruction=(
                            f"Criar o diretório '{required_dir}/' com a estrutura necessária"
                        ),
                        fix_example=f"mkdir -p {required_dir}",
                        auto_fixable=False,
                        auto_fix_command=f"mkdir -p {required_dir}",
                    )
                )

        duration = int((time.time() - start) * 1000)
        result = StepResult(
            step="structure",
            status="success" if not errors else "fail",
            exit_code=0 if not errors else 1,
            duration_ms=duration,
            stdout="",
            stderr="",
            errors=errors,
        )
        self.results.append(result)
        return result

    def _structure_fix_example(self, file: str) -> str | None:
        """Exemplos de conteúdo mínimo para arquivos obrigatórios."""
        examples = {
            "src/__init__.py": '"""SkillHub source package."""\n',
            "pyproject.toml": '[project]\nname = "skillhub"\nversion = "0.1.0"\n',
        }
        return examples.get(file)

    # =========================================================
    # VALIDAÇÃO DE SEGURANÇA (sem subprocess)
    # =========================================================

    def _check_security(self) -> StepResult:
        """Verifica padrões proibidos em todos os arquivos Python do projeto (raiz + src/)."""
        start = time.time()
        errors: list[ValidationError] = []

        # Varre arquivos na raiz (server.py, generate_*.py) e em src/
        py_files = list(BASE_DIR.glob("*.py")) + list(SRC_DIR.rglob("*.py"))

        if not py_files:
            result = StepResult(
                step="security",
                status="skip",
                exit_code=0,
                duration_ms=int((time.time() - start) * 1000),
                stdout="",
                stderr="Nenhum arquivo Python encontrado para verificação",
            )
            self.results.append(result)
            return result

        for py_file in py_files:
            # Ignora o próprio harness.py (contém padrões proibidos como strings)
            if py_file.name == "harness.py":
                continue
            # Ignora arquivos de cache e venv
            if any(
                part in str(py_file)
                for part in (
                    "__pycache__",
                    ".venv",
                    ".pytest_cache",
                    ".mypy_cache",
                    ".ruff_cache",
                )
            ):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
            except Exception as exc:
                # Registra falha de leitura em vez de ignorar silenciosamente
                errors.append(
                    ValidationError(
                        type="security",
                        severity="error",
                        file=str(py_file.relative_to(BASE_DIR)),
                        line=None,
                        column=None,
                        code="FILE_READ_ERROR",
                        message=f"Não foi possível ler o arquivo: {exc}",
                        fix_instruction="Verificar permissões do arquivo ou encoding inválido",
                        fix_example=None,
                        auto_fixable=False,
                        auto_fix_command=None,
                    )
                )
                continue

            for pattern, description, fix in FORBIDDEN_PATTERNS:
                for line_num, line_content in enumerate(content.splitlines(), 1):
                    if re.search(pattern, line_content):
                        errors.append(
                            ValidationError(
                                type="security",
                                severity="error",
                                file=str(py_file.relative_to(BASE_DIR)),
                                line=line_num,
                                column=None,
                                code="SEC_FORBIDDEN",
                                message=description,
                                fix_instruction=fix,
                                fix_example=None,
                                auto_fixable=False,
                                auto_fix_command=None,
                            )
                        )

        duration = int((time.time() - start) * 1000)
        result = StepResult(
            step="security",
            status="success" if not errors else "fail",
            exit_code=0 if not errors else 1,
            duration_ms=duration,
            stdout=f"Verificados {len(py_files)} arquivos Python",
            stderr="",
            errors=errors,
        )
        self.results.append(result)
        return result

    # =========================================================
    # AUDITORIA DE QUALIDADE (sem subprocess)
    # =========================================================

    def _audit_file(self, py_file: Path, errors: list[ValidationError]):
        """Audita um arquivo individual via AST."""
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except SyntaxError as exc:
            errors.append(
                ValidationError(
                    type="audit",
                    severity="error",
                    file=str(py_file.relative_to(BASE_DIR)),
                    line=exc.lineno,
                    column=exc.offset,
                    code="SYNTAX_ERROR",
                    message=f"Erro de sintaxe: {exc.msg}",
                    fix_instruction="Corrigir a sintaxe Python no local indicado",
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )
            return
        except Exception as exc:
            # Registra falha de leitura em vez de ignorar silenciosamente
            errors.append(
                ValidationError(
                    type="audit",
                    severity="error",
                    file=str(py_file.relative_to(BASE_DIR)),
                    line=None,
                    column=None,
                    code="FILE_READ_ERROR",
                    message=f"Não foi possível ler/parsear o arquivo: {exc}",
                    fix_instruction="Verificar permissões do arquivo ou encoding inválido",
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )
            return

        rel_path = str(py_file.relative_to(BASE_DIR))
        if not ast.get_docstring(tree):
            errors.append(
                ValidationError(
                    type="audit",
                    severity="warning",
                    file=rel_path,
                    line=1,
                    column=None,
                    code="MISSING_MODULE_DOCSTRING",
                    message="Módulo sem docstring",
                    fix_instruction='Adicionar docstring: """Descrição."""',
                    fix_example='"""Módulo responsável por X.\n"""',
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._audit_func(node, rel_path, errors)
            elif isinstance(node, ast.ClassDef):
                self._audit_class(node, rel_path, errors)

    def _audit_func(self, node: Any, rel_path: str, errors: list[ValidationError]):
        """Audita docstrings e tipos de uma função."""
        if not ast.get_docstring(node) and not node.name.startswith("_"):
            errors.append(
                ValidationError(
                    type="audit",
                    severity="warning",
                    file=rel_path,
                    line=node.lineno,
                    column=None,
                    code="MISSING_DOCSTRING",
                    message=f"Função pública sem docstring: {node.name}()",
                    fix_instruction=f"Adicionar docstring à função {node.name}()",
                    fix_example=f'def {node.name}(...):\n    """O que faz."""',
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )
        if node.returns is None and not node.name.startswith("__"):
            errors.append(
                ValidationError(
                    type="audit",
                    severity="warning",
                    file=rel_path,
                    line=node.lineno,
                    column=None,
                    code="MISSING_RETURN_TYPE",
                    message=f"Função sem retorno tipado: {node.name}()",
                    fix_instruction=f"Adicionar anotação de retorno a {node.name}()",
                    fix_example=f"def {node.name}(...) -> ReturnType:",
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )

    def _audit_class(
        self, node: ast.ClassDef, rel_path: str, errors: list[ValidationError]
    ):
        """Audita docstrings de uma classe."""
        if not ast.get_docstring(node):
            errors.append(
                ValidationError(
                    type="audit",
                    severity="warning",
                    file=rel_path,
                    line=node.lineno,
                    column=None,
                    code="MISSING_CLASS_DOCSTRING",
                    message=f"Classe sem docstring: {node.name}",
                    fix_instruction=f"Adicionar docstring à classe {node.name}",
                    fix_example=f'class {node.name}:\n    """Propósito."""',
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )

    def _check_code_quality(self) -> StepResult:
        """Verifica type hints e docstrings via AST (raiz + src/)."""
        start = time.time()
        errors: list[ValidationError] = []

        # Varre arquivos na raiz (server.py, generate_*.py) e em src/
        py_files = list(BASE_DIR.glob("*.py")) + list(SRC_DIR.rglob("*.py"))

        if not py_files:
            result = StepResult(
                step="audit",
                status="skip",
                exit_code=0,
                duration_ms=int((time.time() - start) * 1000),
                stdout="",
                stderr="Nenhum arquivo Python encontrado para auditoria",
            )
            self.results.append(result)
            return result

        for py_file in py_files:
            # Ignora o próprio harness.py (contém padrões proibidos como strings)
            if py_file.name == "harness.py":
                continue
            # Ignora arquivos de cache e venv
            if any(
                part in str(py_file)
                for part in (
                    "__pycache__",
                    ".venv",
                    ".pytest_cache",
                    ".mypy_cache",
                    ".ruff_cache",
                )
            ):
                continue
            self._audit_file(py_file, errors)

        duration = int((time.time() - start) * 1000)
        is_fail = any(e.severity == "error" for e in errors)
        result = StepResult(
            step="audit",
            status="success" if not is_fail else "fail",
            exit_code=0 if not is_fail else 1,
            duration_ms=duration,
            stdout="",
            stderr="",
            errors=errors,
        )
        self.results.append(result)
        return result

    # =========================================================
    # STEPS COM FERRAMENTAS EXTERNAS
    # =========================================================

    def run_lint(self) -> None:
        """Executa ruff check e ruff format --check."""
        result = self._run_command(
            "lint", ["ruff", "check", ".", "--output-format=concise"]
        )
        if result.status != "skip":
            result.errors = self._parse_ruff_errors(result.stdout + result.stderr)

        fmt_result = self._run_command(
            "format_check", ["ruff", "format", "--check", "."]
        )
        if fmt_result.status != "skip":
            fmt_result.errors = self._parse_ruff_format_errors(
                fmt_result.stdout + fmt_result.stderr
            )

    def run_typecheck(self) -> None:
        """Executa mypy nos arquivos Python do projeto (raiz + src/)."""
        # Varre arquivos na raiz (server.py, generate_*.py) e em src/
        py_files = list(BASE_DIR.glob("*.py")) + list(SRC_DIR.rglob("*.py"))
        # Ignora arquivos de cache e venv
        py_files = [
            f
            for f in py_files
            if not any(
                p in str(f)
                for p in (
                    "__pycache__",
                    ".venv",
                    ".pytest_cache",
                    ".mypy_cache",
                    ".ruff_cache",
                )
            )
        ]

        if not py_files:
            result = StepResult(
                step="typecheck",
                status="skip",
                exit_code=0,
                duration_ms=0,
                stdout="",
                stderr="Nenhum arquivo Python encontrado para type check",
            )
            self.results.append(result)
            return

        # Executa mypy em todos os arquivos Python encontrados
        result = self._run_command(
            "typecheck",
            ["mypy"]
            + [str(f.relative_to(BASE_DIR)) for f in py_files]
            + ["--show-column-numbers"],
        )
        if result.status != "skip":
            result.errors = self._parse_mypy_errors(result.stdout + result.stderr)

    def run_tests(self) -> None:
        """Executa pytest com saída verbosa."""
        result = self._run_command(
            "tests",
            ["pytest", "-v", "--tb=short", "--no-header"],
        )
        if result.status != "skip":
            result.errors = self._parse_pytest_errors(result.stdout + result.stderr)

    def run_audit(self) -> None:
        """Verifica qualidade de código via AST (sem subprocess)."""
        self._check_code_quality()

    def run_security(self) -> None:
        """Verifica padrões de segurança proibidos."""
        self._check_security()

    def run_structure(self) -> None:
        """Verifica estrutura obrigatória do projeto."""
        self._check_project_structure()

    def run_content_format(self) -> None:
        """Verifica formato de roadmaps e lições gerados."""
        start = time.time()
        errors: list[ValidationError] = []

        # Importa o validador de conteúdo
        try:
            sys.path.insert(0, str(BASE_DIR / "scripts"))
            from validate_content_format import ContentValidator  # type: ignore

            validator = ContentValidator()
            validator.validate_all()

            # Converte erros do validador para o formato do harness
            for error_msg in validator.errors:
                # Parse da mensagem de erro
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

            # Converte warnings
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
            return (
                "Adicionar bloco ```json com quiz de 3+ perguntas ao final do arquivo"
            )
        elif "quiz tem menos de 3 perguntas" in message:
            return "Adicionar mais perguntas ao quiz (mínimo 3)"
        elif "deve ter exatamente 4 opções" in message:
            return "Ajustar pergunta para ter exatamente 4 alternativas"
        elif "'answer' deve ser 0-3" in message:
            return "Corrigir campo 'answer' para índice válido (0, 1, 2 ou 3)"
        else:
            return "Corrigir formato conforme documentação em docs/PADROES_FORMATO_CONTEUDO.md"

    def _check_hash(self, rel_path: str, expected: dict, errors: list[ValidationError]):
        """Verifica o hash de um arquivo protegido."""
        abs_path = BASE_DIR / rel_path
        if not abs_path.exists():
            errors.append(
                ValidationError(
                    type="integrity",
                    severity="error",
                    file=rel_path,
                    line=None,
                    column=None,
                    code="PROTECTED_FILE_MISSING",
                    message=f"Arquivo não encontrado: {rel_path}",
                    fix_instruction=f"Restaurar: git checkout HEAD -- {rel_path}",
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=f"git checkout HEAD -- {rel_path}",
                )
            )
            return
        h = hashlib.sha256()
        with abs_path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        current, exp = h.hexdigest(), expected.get(rel_path)
        if exp is None:
            errors.append(
                ValidationError(
                    type="integrity",
                    severity="error",
                    file=rel_path,
                    line=None,
                    column=None,
                    code="HASH_NOT_REGISTERED",
                    message=f"Não registrado: {rel_path}",
                    fix_instruction="Executar: python scripts/guard_harness.py --seal",
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )
        elif current != exp:
            errors.append(
                ValidationError(
                    type="integrity",
                    severity="error",
                    file=rel_path,
                    line=None,
                    column=None,
                    code="HASH_MISMATCH",
                    message=f"VIOLAÇÃO: {rel_path} modificado",
                    fix_instruction=f"Restaurar: git checkout HEAD -- {rel_path}",
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=f"git checkout HEAD -- {rel_path}",
                )
            )

    def _check_git_integrity(self, errors: list[ValidationError]):
        """Verifica se há alterações abertas no git para arquivos protegidos."""
        try:
            git = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
            )
            if git.returncode == 0:
                p_set = set(PROTECTED_FILES + [".harness.hash"])
                for line in git.stdout.splitlines():
                    if len(line) < 4:
                        continue
                    # Formato porcelain v1: "XY filename" — colunas fixas
                    # Arquivos renomeados têm formato "R  old -> new"; extraímos
                    # apenas o nome destino (após " -> ") para evitar falsos negativos
                    raw_file = line[3:].strip().strip('"')
                    if " -> " in raw_file:
                        raw_file = raw_file.split(" -> ")[-1].strip()
                    status = line[:2].strip()
                    if raw_file in p_set and status not in ("??",):
                        # REGRA CRÍTICA: Se o arquivo está SELADO (chattr +i), significa que
                        # foi aprovado com senha. Apenas bloqueia se estiver DESBLOQUEADO.
                        file_path = BASE_DIR / raw_file
                        is_sealed = False
                        if file_path.exists():
                            try:
                                result = subprocess.run(
                                    ["lsattr", str(file_path)],
                                    capture_output=True,
                                    text=True,
                                    check=False,
                                )
                                if result.returncode == 0:
                                    attrs = result.stdout.split()[0]
                                    is_sealed = "i" in attrs
                            except Exception:
                                pass

                        # Só bloqueia se o arquivo NÃO estiver selado
                        if not is_sealed:
                            errors.append(
                                ValidationError(
                                    type="integrity",
                                    severity="error",
                                    file=raw_file,
                                    line=None,
                                    column=None,
                                    code="GIT_DIRTY_PROTECTED",
                                    message=f"Alteração aberta no git: {raw_file} (DESBLOQUEADO)",
                                    fix_instruction=(
                                        f"Arquivo protegido modificado mas não selado.\n"
                                        f"Para aprovar: python scripts/guard_harness.py --seal\n"
                                        f"Para reverter: git checkout HEAD -- {raw_file}"
                                    ),
                                    fix_example=None,
                                    auto_fixable=False,
                                    auto_fix_command=None,
                                )
                            )
        except FileNotFoundError:
            pass

    def run_integrity(self) -> StepResult:
        """Verifica integridade via SHA256 e git status."""
        start, errors = time.time(), []
        if not HASH_FILE.exists():
            errors.append(
                ValidationError(
                    type="integrity",
                    severity="error",
                    file=".harness.hash",
                    line=None,
                    column=None,
                    code="HASH_FILE_MISSING",
                    message="Arquivo .harness.hash não encontrado",
                    fix_instruction="Executar: python scripts/guard_harness.py --seal",
                    fix_example=None,
                    auto_fixable=False,
                    auto_fix_command=None,
                )
            )
        else:
            try:
                expected = json.loads(HASH_FILE.read_text(encoding="utf-8"))
            except Exception:
                expected = {}
            for rel_path in PROTECTED_FILES:
                self._check_hash(rel_path, expected, errors)
        self._check_git_integrity(errors)
        duration = int((time.time() - start) * 1000)
        result = StepResult(
            step="integrity",
            status="success" if not errors else "fail",
            exit_code=0 if not errors else 2,
            duration_ms=duration,
            stdout="",
            stderr="",
            errors=errors,
        )
        self.results.append(result)
        return result

    def run_all(self) -> None:
        """Executa todas as validações na ordem de prioridade."""
        self.run_integrity()  # sempre primeiro — fail-fast se violado
        self.run_structure()
        self.run_content_format()  # valida formato de roadmaps e lições
        self.run_security()
        self.run_lint()
        self.run_typecheck()
        self.run_tests()
        self.run_audit()

    def run_without_integrity(self) -> None:
        """Executa todas as validações exceto integridade (para hooks do git)."""
        self.run_structure()
        self.run_content_format()
        self.run_security()
        self.run_lint()
        self.run_typecheck()
        self.run_tests()
        self.run_audit()

    # =========================================================
    # RELATÓRIO E PLANO DE AÇÃO PARA AGENTES
    # =========================================================

    def _error_priority(self, error: ValidationError) -> int:
        """Retorna prioridade numérica do erro (menor = mais urgente)."""
        priority_map = {
            ("integrity", "error"): 0,  # acima de tudo — bloqueia execução
            ("security", "error"): 1,
            ("structure", "error"): 1,
            ("lint", "error"): 2,
            ("format", "error"): 2,
            ("type", "error"): 2,
            ("test", "error"): 2,
            ("audit", "error"): 3,
            ("dsl", "error"): 3,
            ("lint", "warning"): 4,
            ("type", "warning"): 4,
            ("audit", "warning"): 5,
        }
        return priority_map.get((error.type, error.severity), 5)

    def build_agent_instructions(self) -> list[dict[str, Any]]:
        """
        Gera lista ordenada de instruções para o agente.

        Cada instrução contém tudo que o agente precisa para agir:
        - O que está errado
        - Por que é um problema
        - Como corrigir (instrução precisa)
        - Exemplo concreto (quando disponível)
        - Comando para executar (quando aplicável)
        - Se pode ser corrigido automaticamente
        """
        all_errors: list[ValidationError] = []
        for result in self.results:
            all_errors.extend(result.errors)

        # Ordenar por prioridade
        all_errors.sort(key=self._error_priority)

        instructions = []
        for err in all_errors:
            instruction: dict[str, Any] = {
                "priority": self._error_priority(err),
                "priority_label": {
                    0: "BLOQUEANTE",
                    1: "CRÍTICO",
                    2: "IMPORTANTE",
                    3: "MODERADO",
                    4: "SUGESTÃO",
                    5: "INFORMATIVO",
                }.get(self._error_priority(err), "INFORMATIVO"),
                "category": err.type,
                "severity": err.severity,
                "location": {
                    "file": err.file,
                    "line": err.line,
                    "column": err.column,
                },
                "error_code": err.code,
                "problem": err.message,
                "fix_instruction": err.fix_instruction,
                "auto_fixable": err.auto_fixable,
            }

            if err.auto_fix_command:
                instruction["auto_fix_command"] = err.auto_fix_command

            if err.fix_example:
                instruction["fix_example"] = err.fix_example

            instructions.append(instruction)

        return instructions

    def build_auto_fix_sequence(self) -> list[str]:
        """
        Retorna sequência ordenada de comandos auto-aplicáveis.

        O agente pode executar estes comandos diretamente sem análise adicional.
        """
        commands: list[str] = []
        seen: set[str] = set()

        for result in self.results:
            for err in result.errors:
                if err.auto_fixable and err.auto_fix_command:
                    cmd = err.auto_fix_command
                    if cmd not in seen:
                        commands.append(cmd)
                        seen.add(cmd)

        return commands

    def report(self) -> dict[str, Any]:
        """Gera relatório completo estruturado para consumo por agentes."""
        total_duration = int((time.time() - self.start_time) * 1000)
        failed_steps = [r for r in self.results if r.status == "fail"]
        all_errors = [e for r in self.results for e in r.errors]
        critical_errors = [e for e in all_errors if e.severity == "error"]

        steps_summary = []
        for r in self.results:
            step_data: dict[str, Any] = {
                "step": r.step,
                "status": r.status,
                "exit_code": r.exit_code,
                "duration_ms": r.duration_ms,
                "error_count": len(r.errors),
                "errors": [asdict(e) for e in r.errors],
            }
            if r.tool_missing:
                step_data["tool_missing"] = True
                step_data["install_hint"] = self._install_hint(r.step)
            steps_summary.append(step_data)

        return {
            "schema_version": "2.0",
            "harness": "SkillHub Validation Harness",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "healthy" if not critical_errors else "failed",
            "total_duration_ms": total_duration,
            "summary": {
                "total_steps": len(self.results),
                "failed_steps": len(failed_steps),
                "skipped_steps": len([r for r in self.results if r.status == "skip"]),
                "total_errors": len(critical_errors),
                "total_warnings": len(
                    [e for e in all_errors if e.severity == "warning"]
                ),
                "auto_fixable_count": len([e for e in all_errors if e.auto_fixable]),
            },
            "failed_steps": [r.step for r in failed_steps],
            # Instruções completas para o agente corrigir tudo
            "agent_instructions": {
                "description": (
                    "Lista ordenada de correções a aplicar. "
                    "Aplicar em ordem de prioridade (1=mais urgente). "
                    "Executar 'auto_fix_sequence' primeiro para correções automáticas."
                ),
                "auto_fix_sequence": self.build_auto_fix_sequence(),
                "manual_fixes": self.build_agent_instructions(),
            },
            "steps": steps_summary,
        }

    def _install_hint(self, step: str) -> str:
        """Dica de instalação para ferramenta faltante."""
        hints = {
            "lint": "pip install ruff  ou  uv add --dev ruff",
            "format_check": "pip install ruff  ou  uv add --dev ruff",
            "typecheck": "pip install mypy  ou  uv add --dev mypy",
            "tests": "pip install pytest  ou  uv add --dev pytest",
        }
        return hints.get(step, f"Instalar ferramenta para o step '{step}'")

    # =========================================================
    # OUTPUT HUMANO
    # =========================================================

    def _print_step_results(self):
        """Imprime os resultados de cada step."""
        for r in self.results:
            icon = {"success": "✅", "skip": "⏭️ ", "fail": "❌"}.get(r.status, "❓")
            tag = f"[{r.status.upper()}]" if r.status != "success" else ""
            print(f"\n{icon} {r.step.upper()} {tag} ({r.duration_ms}ms)")
            if r.tool_missing:
                print(f"   ⚠️  Ferramenta não encontrada: {self._install_hint(r.step)}")
            for err in r.errors:
                sev = "🔴" if err.severity == "error" else "🟡"
                loc = f":{err.line}" if err.line else ""
                print(f"\n   {sev} [{err.code}] {err.file}{loc}")
                print(f"      Problema: {err.message}")
                print(f"      Correção: {err.fix_instruction}")
                if err.auto_fixable:
                    print(f"      ⚡ Auto-fix: {err.auto_fix_command}")

            # Fallback: Se falhou mas não temos erros parseados, mostra o output bruto
            if r.status == "fail" and not r.errors and not r.tool_missing:
                print(
                    "   ⚠️  Falha detectada, mas nenhum erro foi identificado pelo parser."
                )
                if r.stdout:
                    print("   📄 [STDOUT]:")
                    for line in r.stdout.splitlines()[:5]:
                        print(f"      {line}")
                if r.stderr:
                    print("   ❌ [STDERR]:")
                    for line in r.stderr.splitlines()[:5]:
                        print(f"      {line}")

    def _print_action_plan(self):
        """Imprime o plano de ação consolidado."""
        instructions = self.build_agent_instructions()
        auto_fixes = self.build_auto_fix_sequence()
        print("\n" + "═" * 60 + "\n  PLANO DE AÇÃO\n" + "═" * 60)
        if auto_fixes:
            print("\n⚡ CORREÇÕES AUTOMÁTICAS (executar primeiro):")
            for cmd in auto_fixes:
                print(f"   → {cmd}")
        manual = [i for i in instructions if not i["auto_fixable"]]
        if manual:
            print("\n🔧 CORREÇÕES MANUAIS (por prioridade):")
            for it in manual:
                loc = f":{it['location']['line']}" if it["location"]["line"] else ""
                print(f"\n   [{it['priority_label']}] {it['location']['file']}{loc}")
                print(
                    f"   Problema: {it['problem']}\n   Ação:     {it['fix_instruction']}"
                )

    def print_human(self) -> None:
        """Saída formatada para leitura humana no terminal."""
        print("\n" + "═" * 60)
        print("  SKILLHUB — VALIDAÇÃO COMPLETA")
        print("═" * 60)

        self._print_step_results()
        self._print_action_plan()

        report = self.report()
        status_icon = "✅" if report["status"] == "healthy" else "❌"
        print(f"\n{status_icon} STATUS FINAL: {report['status'].upper()}")
        s = report["summary"]
        print(
            f"   {s['total_errors']} erros · {s['total_warnings']} avisos · "
            f"{s['auto_fixable_count']} auto-fixáveis · "
            f"{report['total_duration_ms']}ms total"
        )

    def print_json(self) -> None:
        """Saída JSON estruturada para consumo por agentes."""
        print(json.dumps(self.report(), indent=2, ensure_ascii=False))


# =============================================================================
# CLI
# =============================================================================


def main() -> None:
    """Ponto de entrada CLI."""
    # ── Fail-fast: verificar integridade antes de qualquer coisa ──────────────
    # Reutiliza a mesma instância para evitar dupla execução de run_integrity()
    harness = ValidationHarness()
    integrity_result = harness.run_integrity()
    if integrity_result.status == "fail":
        print("\n" + "█" * 60)
        print("  🚨  VIOLAÇÃO DE INTEGRIDADE — EXECUÇÃO BLOQUEADA")
        print("█" * 60)
        for err in integrity_result.errors:
            print(f"\n  [{err.code}] {err.file}")
            print(f"  {err.message}")
            print(f"  → {err.fix_instruction}")
        print("\n  O harness não pode continuar com arquivos protegidos comprometidos.")
        print("  Apenas o mantenedor humano pode resolver violações de integridade.\n")
        sys.exit(2)
    # ─────────────────────────────────────────────────────────────────────────

    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    # run_all inclui run_integrity, mas já foi executado — define steps restantes
    def _run_remaining() -> None:
        harness.run_structure()
        harness.run_content_format()
        harness.run_security()
        harness.run_lint()
        harness.run_typecheck()
        harness.run_tests()
        harness.run_audit()

    dispatch = {
        "all": _run_remaining,
        "integrity": lambda: None,  # já executado acima
        "lint": harness.run_lint,
        "type": harness.run_typecheck,
        "test": harness.run_tests,
        "audit": harness.run_audit,
        "security": harness.run_security,
        "structure": harness.run_structure,
        "content": harness.run_content_format,
    }

    if cmd == "json":
        _run_remaining()
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
