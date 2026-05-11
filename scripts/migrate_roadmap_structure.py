#!/usr/bin/env python3
"""
Script de Migração: Estrutura Antiga -> Estrutura Nova (v2.0)

Converte roadmaps do formato antigo (children + side) para o novo formato (subtopics).

Uso:
    python scripts/migrate_roadmap_structure.py data/python_fundamentos.json
    python scripts/migrate_roadmap_structure.py data/python_fundamentos.json --output data/python_fundamentos_v2.json
"""

import json
import sys
import os
from typing import Dict, Any


def migrate_node(node: Dict[str, Any], all_nodes: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Converte um nó do formato antigo para o novo formato.

    Args:
        node: Nó no formato antigo
        all_nodes: Dicionário com todos os nós indexados por ID

    Returns:
        Nó no formato novo
    """
    new_node = {
        "id": node["id"],
        "title": node["title"],
        "type": node["type"],
        "group": node.get("group", ""),
        "difficulty": node.get("difficulty", "medium"),
    }

    # Adicionar content se existir
    if "content" in node:
        new_node["content"] = node["content"]

    # Converter children para subtopics
    if "children" in node and node["children"]:
        subtopics = []
        for child_id in node["children"]:
            if child_id in all_nodes:
                child_node = all_nodes[child_id]
                subtopic = {"id": child_id, "title": child_node["title"]}

                # Adicionar campos opcionais
                if "difficulty" in child_node:
                    subtopic["difficulty"] = child_node["difficulty"]
                if "content" in child_node:
                    subtopic["content"] = child_node["content"]

                # Recursivamente processar filhos do filho (se houver)
                if "children" in child_node and child_node["children"]:
                    subtopic["subtopics"] = []
                    for grandchild_id in child_node["children"]:
                        if grandchild_id in all_nodes:
                            grandchild = all_nodes[grandchild_id]
                            subtopic["subtopics"].append(
                                {
                                    "id": grandchild_id,
                                    "title": grandchild["title"],
                                    "difficulty": grandchild.get(
                                        "difficulty", "medium"
                                    ),
                                }
                            )

                subtopics.append(subtopic)

        if subtopics:
            new_node["subtopics"] = subtopics

    return new_node


def migrate_roadmap(old_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte um roadmap completo do formato antigo para o novo.

    Args:
        old_data: Roadmap no formato antigo

    Returns:
        Roadmap no formato novo
    """
    # Criar índice de todos os nós por ID
    all_nodes = {node["id"]: node for node in old_data["nodes"]}

    # Identificar nós centrais (que não são subtópicos de ninguém)
    central_ids = set(all_nodes.keys())
    for node in old_data["nodes"]:
        if "children" in node:
            central_ids -= set(node["children"])

    # Converter apenas nós centrais (subtópicos serão processados recursivamente)
    new_nodes = []
    for node_id in central_ids:
        if node_id in all_nodes:
            node = all_nodes[node_id]
            if node.get("type") == "central":
                new_nodes.append(migrate_node(node, all_nodes))

    # Criar nova estrutura
    new_data = {"title": old_data["title"], "nodes": new_nodes}

    # Adicionar description se existir
    if "description" in old_data:
        new_data["description"] = old_data["description"]

    return new_data


def main():
    if len(sys.argv) < 2:
        print(
            "Uso: python migrate_roadmap_structure.py <arquivo_entrada> [--output <arquivo_saida>]"
        )
        sys.exit(1)

    input_file = sys.argv[1]

    # Determinar arquivo de saída
    if "--output" in sys.argv:
        output_index = sys.argv.index("--output")
        if output_index + 1 < len(sys.argv):
            output_file = sys.argv[output_index + 1]
        else:
            print("Erro: --output requer um caminho de arquivo")
            sys.exit(1)
    else:
        # Criar nome de saída baseado no input
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_v2{ext}"

    # Verificar se arquivo existe
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo '{input_file}' não encontrado")
        sys.exit(1)

    # Carregar arquivo antigo
    print(f"📖 Lendo {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    # Migrar estrutura
    print("🔄 Migrando estrutura...")
    new_data = migrate_roadmap(old_data)

    # Salvar novo arquivo
    print(f"💾 Salvando em {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print("✅ Migração concluída!")
    print(f"   Nós centrais: {len(new_data['nodes'])}")
    print(f"   Arquivo gerado: {output_file}")


if __name__ == "__main__":
    main()
