#!/usr/bin/env python3
"""Gera lições faltantes para todos os roadmaps."""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.core.config import LICOES_DIR  # noqa: E402
from backend.services.ai_content.lesson_generator import processar_node  # noqa: E402


def find_missing_lessons():
    """Encontra todos os node_ids sem lição correspondente."""
    data_dir = BASE_DIR / "data"
    existing = {f.stem for f in LICOES_DIR.glob("*.md")}
    all_nodes = {}

    for rf in data_dir.glob("roadmap_*.json"):
        with open(rf) as f:
            data = json.load(f)

        roadmap_title = data.get("title", "")

        def walk(node, parent_group: str = "", roadmap_titulo: str = ""):
            nid = node.get("id", "")
            title = node.get("title", "")
            node_type = node.get("type", "subtopic")
            group = node.get("group", parent_group)
            difficulty = node.get("difficulty")
            content = node.get("content")
            subtopics_titles = [sub.get("title", "") for sub in node.get("subtopics", [])]

            if nid:
                all_nodes[nid] = {
                    "title": title,
                    "type": node_type,
                    "content": content,
                    "group": group,
                    "difficulty": difficulty,
                    "roadmap_title": roadmap_titulo,
                    "subtopics": subtopics_titles if subtopics_titles else None,
                }
            for sub in node.get("subtopics", []):
                walk(sub, parent_group=group, roadmap_titulo=roadmap_titulo)

        for node in data.get("nodes", []):
            walk(node, roadmap_titulo=roadmap_title)

    missing = {nid: info for nid, info in all_nodes.items() if nid not in existing}
    return missing


def generate_missing(missing, limit=0, dry_run=False):
    """Gera lições para nós faltantes."""
    results = {"success": 0, "failed": 0, "skipped": 0, "errors": []}

    for i, (node_id, info) in enumerate(sorted(missing.items())):
        if limit and i >= limit:
            break

        if dry_run:
            print(f"  [DRY] {node_id}: {info['title']} ({info['type']})")
            results["skipped"] += 1
            continue

        try:
            processar_node(
                node_id,
                info["title"],
                info["type"],
                content=info.get("content"),
                group=info.get("group"),
                difficulty=info.get("difficulty"),
                roadmap_title=info.get("roadmap_title"),
                subtopics=info.get("subtopics"),
            )
            print(f"  [{i + 1}/{len(missing)}] GERADO {node_id}: {info['title']}")
            results["success"] += 1
        except Exception as e:
            print(f"  [{i + 1}/{len(missing)}] FALHA {node_id}: {e}")
            results["failed"] += 1
            results["errors"].append({"node_id": node_id, "error": str(e)})

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    print("🔍 Escaneando lições faltantes...")
    missing = find_missing_lessons()
    print(f"📊 Total: {len(missing)} lições faltantes")

    if not missing:
        print("✅ Todas as lições já foram geradas!")
        sys.exit(0)

    if args.dry_run:
        generate_missing(missing, limit=args.limit, dry_run=True)
        sys.exit(0)

    print("🚀 Gerando lições...")
    results = generate_missing(missing, limit=args.limit)

    print(
        f"\n✅ Concluído: {results['success']} geradas, "
        f"{results['failed']} falhas, {results['skipped']} puladas"
    )
    if results["errors"]:
        for err in results["errors"][:5]:
            print(f"  Erro: {err['node_id']} — {err['error']}")
