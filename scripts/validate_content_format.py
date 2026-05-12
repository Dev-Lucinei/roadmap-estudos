#!/usr/bin/env python3
"""
Script de Validação de Formato de Conteúdo

Valida que todos os roadmaps e lições seguem os padrões estabelecidos:
- Roadmaps: estrutura v2.0 com subtopics
- Lições: formato markdown com quiz JSON embutido
- Nomes de arquivo: sem acentos, kebab-case
"""

import json
import re
import sys
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LICOES_DIR = BASE_DIR / "licoes"


class ContentValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0

    def validate_roadmap_filename(self, filename):
        """Valida nome de arquivo de roadmap"""
        if not filename.startswith("roadmap_"):
            self.errors.append(f"❌ {filename}: deve começar com 'roadmap_'")
            return False

        if not filename.endswith(".json"):
            self.errors.append(f"❌ {filename}: deve terminar com '.json'")
            return False

        # Verifica caracteres especiais
        name_part = filename.replace("roadmap_", "").replace(".json", "")
        if not re.match(r"^[a-z0-9_]+$", name_part):
            self.errors.append(
                f"❌ {filename}: contém caracteres inválidos (use apenas a-z, 0-9, _)"
            )
            return False

        return True

    def validate_roadmap_structure(self, filepath):
        """Valida estrutura JSON do roadmap"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validações obrigatórias
            if "title" not in data:
                self.errors.append(f"❌ {filepath.name}: falta campo 'title'")
                return False

            if "nodes" not in data:
                self.errors.append(f"❌ {filepath.name}: falta campo 'nodes'")
                return False

            if not isinstance(data["nodes"], list):
                self.errors.append(f"❌ {filepath.name}: 'nodes' deve ser um array")
                return False

            # Verifica estrutura v2.0 (subtopics em vez de children)
            for i, node in enumerate(data["nodes"]):
                if "children" in node or "side" in node:
                    self.warnings.append(
                        f"⚠️ {filepath.name}: nó {i} usa estrutura antiga (children/side). "
                        "Considere migrar para estrutura v2.0 (subtopics)"
                    )

                # Valida campos obrigatórios do nó
                required_fields = ["id", "title"]
                for field in required_fields:
                    if field not in node:
                        self.errors.append(
                            f"❌ {filepath.name}: nó {i} falta campo '{field}'"
                        )
                        return False

                # Valida IDs (kebab-case)
                if not re.match(r"^[a-z0-9_-]+$", node["id"]):
                    self.errors.append(
                        f"❌ {filepath.name}: ID '{node['id']}' inválido (use kebab-case)"
                    )
                    return False

            self.success_count += 1
            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"❌ {filepath.name}: JSON inválido - {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"❌ {filepath.name}: erro ao validar - {str(e)}")
            return False

    def validate_lesson_format(self, filepath):
        """Valida formato de lição markdown"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Verifica se tem conteúdo
            if len(content.strip()) < 100:
                self.warnings.append(
                    f"⚠️ {filepath.name}: conteúdo muito curto (< 100 chars)"
                )

            # Verifica se tem título (# no início)
            if not content.strip().startswith("#"):
                self.warnings.append(
                    f"⚠️ {filepath.name}: deve começar com título markdown (#)"
                )

            # Verifica se tem quiz JSON embutido
            quiz_match = re.search(r"```json\s*(\[[\s\S]*?\])\s*```", content)
            if quiz_match:
                try:
                    quiz_data = json.loads(quiz_match.group(1))

                    if not isinstance(quiz_data, list):
                        self.errors.append(
                            f"❌ {filepath.name}: quiz deve ser um array"
                        )
                        return False

                    if len(quiz_data) < 3:
                        self.warnings.append(
                            f"⚠️ {filepath.name}: quiz tem menos de 3 perguntas"
                        )

                    # Valida estrutura de cada pergunta
                    for i, q in enumerate(quiz_data):
                        required = ["question", "options", "answer"]
                        for field in required:
                            if field not in q:
                                self.errors.append(
                                    f"❌ {filepath.name}: pergunta {i} falta campo '{field}'"
                                )
                                return False

                        if not isinstance(q["options"], list) or len(q["options"]) != 4:
                            self.errors.append(
                                f"❌ {filepath.name}: pergunta {i} deve ter exatamente 4 opções"
                            )
                            return False

                        if (
                            not isinstance(q["answer"], int)
                            or q["answer"] < 0
                            or q["answer"] > 3
                        ):
                            self.errors.append(
                                f"❌ {filepath.name}: pergunta {i} 'answer' deve ser 0-3"
                            )
                            return False

                except json.JSONDecodeError:
                    self.errors.append(f"❌ {filepath.name}: quiz JSON inválido")
                    return False
            else:
                self.warnings.append(f"⚠️ {filepath.name}: não contém quiz embutido")

            self.success_count += 1
            return True

        except Exception as e:
            self.errors.append(f"❌ {filepath.name}: erro ao validar - {str(e)}")
            return False

    def validate_all(self):
        """Executa todas as validações"""
        print("=" * 70)
        print("VALIDAÇÃO DE FORMATO DE CONTEÚDO")
        print("=" * 70)

        # Valida roadmaps
        print("\n📚 Validando Roadmaps...")
        roadmap_files = [
            f for f in DATA_DIR.glob("*.json") if f.name.startswith("roadmap_")
        ]

        for filepath in sorted(roadmap_files):
            if self.validate_roadmap_filename(filepath.name):
                self.validate_roadmap_structure(filepath)

        # Valida lições
        print("\n📝 Validando Lições...")
        lesson_files = list(LICOES_DIR.glob("*.md"))

        for filepath in sorted(lesson_files):
            self.validate_lesson_format(filepath)

        # Relatório final
        print("\n" + "=" * 70)
        print("RELATÓRIO DE VALIDAÇÃO")
        print("=" * 70)

        print(f"\n✅ Arquivos válidos: {self.success_count}")

        if self.warnings:
            print(f"\n⚠️ Avisos ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"   {warning}")
            if len(self.warnings) > 10:
                print(f"   ... e mais {len(self.warnings) - 10} avisos")

        if self.errors:
            print(f"\n❌ Erros ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"   {error}")
            if len(self.errors) > 10:
                print(f"   ... e mais {len(self.errors) - 10} erros")

        print("\n" + "=" * 70)

        if self.errors:
            print("❌ VALIDAÇÃO FALHOU - Corrija os erros acima")
            return False
        elif self.warnings:
            print("⚠️ VALIDAÇÃO PASSOU COM AVISOS")
            return True
        else:
            print("✅ VALIDAÇÃO PASSOU - Todos os arquivos estão corretos!")
            return True


def main():
    validator = ContentValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
