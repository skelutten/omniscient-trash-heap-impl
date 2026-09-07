#!/usr/bin/env python3
"""Script to emit or verify .agents/skills/trashheap/SKILL.md (AGENT-SKILLS.md §4, E050)."""

import argparse
import sys
from pathlib import Path

from trashheap.skills import check_agent_skills, write_agent_skills


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or verify Agent Skills definition.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that .agents/skills/trashheap/SKILL.md is up-to-date and matches specification.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root path (default: current working directory).",
    )
    parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install skill globally to ~/.agents/skills/trashheap/SKILL.md",
    )
    args = parser.parse_args()

    if args.global_install:
        from trashheap.skills import generate_agent_skills_content

        global_path = Path.home() / ".agents" / "skills" / "trashheap" / "SKILL.md"
        global_path.parent.mkdir(parents=True, exist_ok=True)
        content = generate_agent_skills_content()
        global_path.write_text(content, encoding="utf-8")
        print(f"✓ Installed global Agent Skill to {global_path}")
        sys.exit(0)

    repo_root = args.repo_root.resolve()

    if args.check:
        if not check_agent_skills(repo_root):
            print(
                "ERROR: [E050] .agents/skills/trashheap/SKILL.md is missing or out of sync.",
                file=sys.stderr,
            )
            sys.exit(1)
        print("✓ .agents/skills/trashheap/SKILL.md is up-to-date.")
        sys.exit(0)
    else:
        out_path = write_agent_skills(repo_root)
        print(f"✓ Emitted {out_path}")
        sys.exit(0)


if __name__ == "__main__":
    main()
