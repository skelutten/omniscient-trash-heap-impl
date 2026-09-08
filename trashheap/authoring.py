"""Canonical authoring and section-owned regeneration (OWN-001..003, BODY-003..004, E051)."""

from typing import Dict, Optional, Tuple

from trashheap.linter import KNOWN_TEMPLATE_HEADINGS


class SectionOwnershipError(Exception):
    """Raised when compilation/regeneration encounters invalid sections (E051)."""

    def __init__(self, code: str, message: str):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


def parse_markdown_sections(body: str) -> Dict[str, str]:
    """Parse Markdown body into ordered sections keyed by heading title."""
    sections: Dict[str, str] = {}
    lines = body.splitlines()
    current_heading: Optional[str] = None
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines)
            current_heading = line[3:].strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)
        else:
            # Preamble before first H2 (e.g. H1 title)
            if "" not in sections:
                sections[""] = ""
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines)
    elif "" in sections:
        sections[""] = "\n".join(current_lines)

    return sections


def extract_notes_section(body: str) -> Tuple[Optional[str], int]:
    """Extract the first raw ## Notes section verbatim, returning (section_text, count).

    The count is the total number of ``## Notes`` headings in the body, so a
    second Notes section separated by another heading is still detected as a
    duplicate (OWN-002) rather than silently dropped.
    """
    lines = body.splitlines(keepends=True)
    in_notes = False
    notes_lines: list[str] = []
    count = 0

    for line in lines:
        if line.startswith("## Notes"):
            count += 1
            if count == 1:
                in_notes = True
                notes_lines.append(line)
        elif in_notes:
            if line.startswith("## "):
                # Reached the end of the first Notes section
                in_notes = False
            else:
                notes_lines.append(line)

    if count == 0:
        return None, 0
    return "".join(notes_lines), count


def regenerate_page(
    existing_content: str,
    updated_machine_sections: Dict[str, str],
    allow_conflict_overwrite: bool = False,
) -> str:
    """Regenerate a Knowledge Object page adhering to the Section Ownership contract.

    Invariants:
    - OWN-001: Machine-owned template headings are updated from data.
    - OWN-002: At most ONE ## Notes section is preserved byte-verbatim.
    - OWN-003: Unmodified regeneration yields byte-identical output.
    - BODY-003 / E051: Unrecognized non-Notes sections abort compilation fail-closed.
    - BODY-004: Manually modified machine sections require explicit overwrite flag.
    """
    parts = existing_content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid markdown file: missing frontmatter fences")

    fm_raw = parts[1]
    body = parts[2]

    # Check for duplicate ## Notes (OWN-002, E051)
    raw_notes, notes_count = extract_notes_section(body)
    if notes_count > 1:
        raise SectionOwnershipError(
            "E051",
            f"Multiple '## Notes' sections ({notes_count}) detected. Compilation aborted to prevent data loss.",
        )

    # Parse sections
    sections = parse_markdown_sections(body)

    # Validate all existing non-Notes sections are recognized template headings (BODY-003 / E051)
    for heading in sections.keys():
        if heading == "" or heading == "Notes":
            continue
        if heading not in KNOWN_TEMPLATE_HEADINGS:
            raise SectionOwnershipError(
                "E051",
                f"Unrecognized non-Notes section '## {heading}' detected. Compilation aborted to prevent data loss.",
            )

    # Check for manual edits to machine-owned sections (BODY-004)
    if not allow_conflict_overwrite:
        for heading, new_content in updated_machine_sections.items():
            if heading in sections:
                old_clean = sections[heading].strip()
                new_clean = new_content.strip()
                if old_clean and old_clean != new_clean:
                    raise SectionOwnershipError(
                        "E051",
                        f"Machine-owned section '## {heading}' has been modified. Overwrite requires allow_conflict_overwrite=True (BODY-004).",
                    )

    # Reassemble body
    # Preserve preamble (e.g. H1 title)
    preamble = sections.get("", "").strip()
    assembled_parts = []
    if preamble:
        assembled_parts.append(preamble)

    for heading, content in updated_machine_sections.items():
        assembled_parts.append(f"## {heading}\n{content.strip()}\n")

    # Append byte-preserved human Notes (OWN-002)
    if raw_notes:
        assembled_parts.append(raw_notes.strip() + "\n")

    new_body = "\n\n".join(assembled_parts).strip() + "\n"
    return f"---{fm_raw}---\n\n{new_body}"
