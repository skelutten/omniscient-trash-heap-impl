"""Pydantic v2 frontmatter model and Knowledge Object representation.

Enforces META-001 (9 metadata categories) and META-002 (extra=forbid).
"""

from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from trashheap.constants import DEFAULT_SCHEMA_VERSION


class ValidityModel(BaseModel):
    """Category 7: TEMPORAL validity model (VAL-001)."""

    model_config = ConfigDict(extra="forbid")

    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class RelationModel(BaseModel):
    """Category 9: ONTOLOGY relation link."""

    model_config = ConfigDict(extra="forbid")

    type: str
    target: str
    soft_link: bool = False
    created_date: Optional[date] = None


class FrontmatterModel(BaseModel):
    """Canonical 9-category frontmatter model (META-001, META-002, extra='forbid')."""

    model_config = ConfigDict(extra="forbid")

    # Category 1: IDENTITY
    id: str
    title: str
    schema_version: str = DEFAULT_SCHEMA_VERSION
    aliases: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

    # Category 2: ORGANIZATION
    scope: Literal["personal", "engineering"]
    taxonomy_path: str
    taxonomy_id: Optional[str] = None

    # Category 3: CLASSIFICATION
    object_type: str
    domain: str

    # Category 4: FACETS (multi-valued arrays or scalars)
    toolchain: Optional[List[str]] = None
    prog_language: Optional[List[str]] = None
    language: Optional[List[str]] = None
    audience: Optional[str] = None
    architecture: Optional[List[str]] = None
    lifecycle: Optional[str] = None
    test_level: Optional[List[str]] = None

    # Category 5: EPISTEMOLOGY
    evidence: str
    verification: str
    authority: str
    consensus: str

    # Category 6: PROVENANCE
    source_type: str
    source_refs: List[str]
    author: str
    last_modified: date
    reviewer: Optional[str] = None
    last_verified: Optional[date] = None
    next_review: date
    confidence: float = Field(ge=0.0, le=1.0)

    # Category 7: TEMPORAL
    validity: Optional[ValidityModel] = None

    # Category 8: GOVERNANCE
    status: str

    # Category 9: ONTOLOGY
    relations: List[RelationModel] = Field(default_factory=list)


class KnowledgeObject:
    """In-memory representation of a canonical Knowledge Object."""

    def __init__(
        self,
        path: Path,
        frontmatter_dict: Dict[str, Any],
        raw_body: str,
        frontmatter: Optional[FrontmatterModel] = None,
        load_error: Optional[Exception] = None,
    ):
        self.path = path
        self.frontmatter_dict = frontmatter_dict
        self.raw_body = raw_body
        self.frontmatter = frontmatter
        self.load_error = load_error

    @property
    def id(self) -> Optional[str]:
        if self.frontmatter:
            return self.frontmatter.id
        return self.frontmatter_dict.get("id")

    @property
    def title(self) -> Optional[str]:
        if self.frontmatter:
            return self.frontmatter.title
        return self.frontmatter_dict.get("title")

    @property
    def scope(self) -> Optional[str]:
        if self.frontmatter:
            return self.frontmatter.scope
        return self.frontmatter_dict.get("scope")

    @property
    def object_type(self) -> Optional[str]:
        if self.frontmatter:
            return self.frontmatter.object_type
        return self.frontmatter_dict.get("object_type")

    @property
    def domain(self) -> Optional[str]:
        if self.frontmatter:
            return self.frontmatter.domain
        return self.frontmatter_dict.get("domain")

    @property
    def relations(self) -> List[Dict[str, Any]]:
        if self.frontmatter and self.frontmatter.relations:
            return [
                {
                    "type": r.type,
                    "target": r.target,
                    "soft_link": r.soft_link,
                }
                for r in self.frontmatter.relations
            ]
        raw = self.frontmatter_dict.get("relations", [])
        if isinstance(raw, list):
            return [r for r in raw if isinstance(r, dict)]
        return []

    @property
    def body(self) -> str:
        return self.raw_body

    def parse_sections(self) -> Dict[str, str]:
        """Extract Markdown H2 sections from the body (code-fence aware).

        Delegates to the single Section Map implementation (SCHEMA-005) so the
        linter, retrieval and CLI all share one heading parser.
        """
        from trashheap.section_map import build_section_map

        lines = self.raw_body.splitlines()
        sections: Dict[str, str] = {}
        for entry in build_section_map(self.raw_body):
            sections[entry.title] = "\n".join(lines[entry.start_line : entry.end_line]).strip()
        return sections
