"""Tests for Agent Skills generation and drift verification (AGENT-SKILLS.md, E050)."""

from pathlib import Path

import yaml

from trashheap.skills import check_agent_skills, generate_agent_skills_content, write_agent_skills


def test_agent_skills_frontmatter_and_commands():
    """AGENT-SKILLS.md §2, §3: Frontmatter schema and standard slash commands."""
    content = generate_agent_skills_content()
    parts = content.split("---", 2)
    assert len(parts) >= 3, "Missing frontmatter fences in generated SKILL.md"

    fm = yaml.safe_load(parts[1])
    assert fm["name"] == "trashheap"
    assert fm["version"] == "3.8.10"
    assert fm["license"] == "Apache-2.0"
    assert fm["compatibility"]["python"] == ">=3.11"
    assert fm["compatibility"]["pydantic"] == ">=2.0"
    assert fm["metadata"]["specification"] == "LLM-WIKI-AGENT-SKILLS-001"

    # Verify 6 standard slash commands are documented
    body = parts[2]
    expected_commands = [
        "/lint",
        "/validate",
        "/stage-lint",
        "/ingest",
        "/query",
        "/rebuild",
    ]
    for cmd in expected_commands:
        assert cmd in body, f"Command {cmd} missing from generated SKILL.md"


def test_agent_skills_drift_detection(tmp_path: Path):
    """E050: Generated skill drift detection."""
    # Initially missing
    assert not check_agent_skills(tmp_path)

    # After writing
    skill_file = write_agent_skills(tmp_path)
    assert skill_file.exists()
    assert check_agent_skills(tmp_path)

    # After tampering
    skill_file.write_text("Tampered content", encoding="utf-8")
    assert not check_agent_skills(tmp_path)
