#!/usr/bin/env python3
"""
Script para corrigir roadmaps com estrutura antiga (children + side)
e converter para estrutura nova (subtopics aninhados)
"""

import json
import sys


def convert_to_new_structure(old_data):
    """Converte estrutura antiga para nova"""

    # Criar índice de todos os nós
    all_nodes = {node["id"]: node for node in old_data["nodes"]}

    # Identificar nós centrais
    central_nodes = [n for n in old_data["nodes"] if n.get("type") == "central"]

    print(f"   Encontrados {len(central_nodes)} nós centrais")

    new_nodes = []

    for central in central_nodes:
        print(f"   Processando: {central['id']}")

        new_central = {
            "id": central["id"],
            "title": central["title"],
            "type": "central",
            "group": central.get("group", ""),
            "difficulty": central.get("difficulty", "medium"),
        }

        if "content" in central:
            new_central["content"] = central["content"]

        # Converter children para subtopics
        if "children" in central and central["children"]:
            print(f"      Children: {central['children']}")
            subtopics = []
            for child_id in central["children"]:
                if child_id in all_nodes:
                    child = all_nodes[child_id]
                    print(f"         Adicionando subtópico: {child_id}")
                    subtopic = {
                        "id": child_id,
                        "title": child["title"],
                        "difficulty": child.get("difficulty", "medium"),
                    }

                    if "content" in child:
                        subtopic["content"] = child["content"]

                    subtopics.append(subtopic)
                else:
                    print(f"         ⚠️  Child {child_id} não encontrado!")

            if subtopics:
                new_central["subtopics"] = subtopics
                print(f"      Total de subtópicos adicionados: {len(subtopics)}")

        new_nodes.append(new_central)

    return {"title": old_data["title"], "nodes": new_nodes}


def main():
    if len(sys.argv) < 2:
        print("Uso: python fix_roadmap_structure.py <arquivo.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"📖 Lendo {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    print("🔄 Convertendo estrutura...")
    new_data = convert_to_new_structure(old_data)

    print(f"💾 Salvando {input_file}...")
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

    print("✅ Conversão concluída!")
    print(f"   Nós centrais: {len(new_data['nodes'])}")
    total_subtopics = sum(len(n.get("subtopics", [])) for n in new_data["nodes"])
    print(f"   Total de subtópicos: {total_subtopics}")


if __name__ == "__main__":
    main()
