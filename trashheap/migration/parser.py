"""Legacy markdown parser and metadata normalizer (plans/60-OLD-WIKI-MIGRATION.md).

Enforces:
- Rule 4: Extract link and facet proposals as read-only suggestions.
- Rule 5: Malformed metadata triggers explicit QuarantineRecord.
- Rule 6: Normalize legacy singular source_ref to source_refs array while preserving relative paths.
- Rule 8: Anti-contamination: preserve legacy tags for audit, initialize canonical keywords as empty.
- Rule 9: Distinguish verified-personal from inferred scope; fail closed on ambiguous scope.
- Rule 10: Record conservative defaults (draft, unverified, placeholder confidence).
- Rule 11 & D95: Opt-in frontmatter: required|derived mode with title extraction and privacy stripping.
"""

import hashlib
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Union

import yaml

from trashheap.constants import ACTOR_PATTERN, ID_PATTERN
from trashheap.migration.models import (
    FacetProposal,
    FrontmatterMode,
    LinkProposal,
    MigrationMap,
    QuarantineRecord,
)
from trashheap.models import FrontmatterModel, KnowledgeObject
from trashheap.registry.loader import LoadedRegistries
from trashheap.slug import slugify_text


class LegacyParser:
    """Deterministic legacy corpus parser and normalizer."""

    def __init__(self, loaded_registries: LoadedRegistries):
        self.registries = loaded_registries
        self.tax_by_id = {node.taxonomy_id: node for node in self.registries.taxonomy}

    def parse_file(
        self,
        rel_path: str,
        content_bytes: bytes,
        migration_map: MigrationMap,
    ) -> Union[
        Tuple[KnowledgeObject, List[LinkProposal], List[FacetProposal], List[str]], QuarantineRecord
    ]:
        """Parse a single legacy markdown file into canonical representation or quarantine record."""
        # 1. Decode UTF-8
        try:
            raw_text = content_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            return QuarantineRecord(
                file_path=rel_path,
                reason="unicode_decode_error",
                error_detail=str(e),
            )

        legacy_fm: Dict[str, Any] = {}
        body_text = raw_text

        # 2. Frontmatter processing (Rule 11, D95)
        if migration_map.frontmatter_mode == FrontmatterMode.REQUIRED:
            parts = raw_text.split("---", 2)
            if len(parts) < 3:
                return QuarantineRecord(
                    file_path=rel_path,
                    reason="missing_frontmatter",
                    error_detail="File missing required YAML frontmatter fence ('---')",
                )
            try:
                parsed_fm = yaml.safe_load(parts[1])
                if not isinstance(parsed_fm, dict):
                    return QuarantineRecord(
                        file_path=rel_path,
                        reason="malformed_metadata",
                        error_detail="Frontmatter is not a YAML dictionary",
                    )
                legacy_fm = parsed_fm
                body_text = parts[2]
            except Exception as e:
                return QuarantineRecord(
                    file_path=rel_path,
                    reason="malformed_metadata",
                    error_detail=f"YAML parse error: {e}",
                )

        elif migration_map.frontmatter_mode == FrontmatterMode.DERIVED:
            # Opt-in derived mode (D95): external docs without frontmatter
            # Privacy stripping: strip author/signum macros
            stripped_text = raw_text
            for macro in migration_map.privacy_stripping:
                # Match e.g. %docResp or %docResp: user or %docResp user
                pattern = r"%" + re.escape(macro.lstrip("%")) + r"[:\s]+[^\r\n]*"
                stripped_text = re.sub(pattern, "", stripped_text)

            # Extract title: from %docTitle macro or first # H1
            title_match = re.search(r"%docTitle[:\s]+([^\r\n]+)", raw_text)
            if title_match:
                extracted_title = title_match.group(1).strip()
            else:
                h1_match = re.search(r"^#\s+([^\r\n]+)", stripped_text, re.MULTILINE)
                if h1_match:
                    extracted_title = h1_match.group(1).strip()
                else:
                    extracted_title = (
                        Path(rel_path).stem.replace("_", " ").replace("-", " ").title()
                    )

            legacy_fm = {
                "title": extracted_title,
                "source_refs": [rel_path],
            }
            body_text = stripped_text

        # 3. Scope resolution (Rule 9)
        # 3. Scope resolution (Rule 9)
        raw_scope = legacy_fm.get("scope")
        if raw_scope in ("personal", "engineering"):
            scope = raw_scope
        elif migration_map.target_scope:
            scope = migration_map.target_scope
        else:
            # Rule 9: Uncertain scope remains ambiguous and never defaults silently to personal
            return QuarantineRecord(
                file_path=rel_path,
                reason="ambiguous_scope",
                error_detail="Scope could not be verified; explicit target_scope required",
            )

        # 4. Anti-contamination rule (Rule 8): preserve legacy tags for audit, keywords empty
        legacy_tags: List[str] = []
        raw_tags = legacy_fm.get("tags") or legacy_fm.get("keywords") or []
        if isinstance(raw_tags, list):
            legacy_tags = [str(t).strip() for t in raw_tags if str(t).strip()]
        elif isinstance(raw_tags, str):
            legacy_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]

        # 5. Taxonomy mapping
        taxonomy_id = None

        raw_tax = (
            legacy_fm.get("taxonomy_id")
            or legacy_fm.get("taxonomy_path")
            or legacy_fm.get("category")
        )
        if raw_tax and str(raw_tax) in migration_map.taxonomy_mapping:
            taxonomy_id = migration_map.taxonomy_mapping[str(raw_tax)]
        elif raw_tax and str(raw_tax) in self.tax_by_id:
            taxonomy_id = str(raw_tax)
        else:
            # Default taxonomy for scope
            if scope == "engineering":
                taxonomy_id = "TX-ENG-01"
            else:
                taxonomy_id = "TX-PERS-01"

        tax_node = self.tax_by_id.get(taxonomy_id)
        if not tax_node:
            return QuarantineRecord(
                file_path=rel_path,
                reason="invalid_taxonomy",
                error_detail=f"Resolved taxonomy ID '{taxonomy_id}' not in registry",
            )

        if tax_node.scope != scope:
            taxonomy_id = "TX-ENG-01" if scope == "engineering" else "TX-PERS-01"
            tax_node = self.tax_by_id[taxonomy_id]

        taxonomy_path = tax_node.name

        # 6. Object type mapping
        raw_type = legacy_fm.get("object_type") or legacy_fm.get("type") or "Article"
        mapped_type = migration_map.type_mapping.get(str(raw_type), str(raw_type))
        if mapped_type not in self.registries.object_types:
            mapped_type = "Article"
        obj_spec = self.registries.object_types.get(mapped_type)
        type_code = (
            getattr(obj_spec, "code", mapped_type[:3].upper())
            if obj_spec
            else mapped_type[:3].upper()
        )

        # 7. Source refs normalization (Rule 6)
        source_refs: List[str] = []
        if "source_ref" in legacy_fm and legacy_fm["source_ref"]:
            source_refs.append(str(legacy_fm["source_ref"]))
        if "source_refs" in legacy_fm and isinstance(legacy_fm["source_refs"], list):
            for s in legacy_fm["source_refs"]:
                if s and str(s) not in source_refs:
                    source_refs.append(str(s))
        if not source_refs:
            source_refs.append(rel_path)

        # 8. Deterministic ID generation
        existing_id = legacy_fm.get("id")
        scope_prefix = "PERS" if scope == "personal" else "ENG"
        if (
            existing_id
            and re.match(ID_PATTERN, str(existing_id))
            and str(existing_id).startswith(scope_prefix)
        ):
            obj_id = str(existing_id)
        else:
            tag_strat = getattr(obj_spec, "tag_strategy", "domain") if obj_spec else "domain"
            if tag_strat == "year":
                tag = str(date.today().year)
            else:
                raw_tag = (
                    slugify_text(legacy_fm.get("title", "untitled"))[:12].upper().replace("-", "_")
                )
                tag = raw_tag if raw_tag else "NOTE"
            rel_hash = hashlib.sha256(rel_path.encode("utf-8")).hexdigest()
            num_suffix = f"{int(rel_hash[:4], 16) % 9000 + 1000}"
            obj_id = f"{scope_prefix}-{type_code}-{tag}-{num_suffix}"

        # 9. Conservative metadata construction (Rule 10)
        today_iso = date.today().isoformat()
        next_review_iso = (date.today() + timedelta(days=365)).isoformat()

        # Domain fallback
        domain = legacy_fm.get("domain")
        if not domain or domain not in self.registries.domains:
            if migration_map.default_domain in self.registries.domains:
                domain = migration_map.default_domain
            else:
                domain = "software_engineering" if scope == "engineering" else "formal_science"

        # Consensus fallback
        raw_consensus = legacy_fm.get("consensus")
        if raw_consensus in ("proposed", "contested"):
            consensus = raw_consensus
        else:
            consensus = "proposed"

        # Author sanitization
        raw_author = legacy_fm.get("author")
        if raw_author:
            clean_str = str(raw_author).strip().lower()
            if re.match(ACTOR_PATTERN, clean_str):
                author = clean_str
            else:
                sanitized = re.sub(r"[^a-z0-9._-]", "_", clean_str).strip("_")
                author = f"human:{sanitized}" if sanitized else "process:migration"
        else:
            author = "process:migration"

        frontmatter_dict: Dict[str, Any] = {
            "id": obj_id,
            "title": legacy_fm.get("title") or Path(rel_path).stem.replace("_", " ").title(),
            "schema_version": "3.8.10",
            "aliases": [],
            "keywords": [],  # Anti-contamination: empty canonical keywords (Rule 8)
            "scope": scope,
            "taxonomy_path": taxonomy_path,
            "taxonomy_id": taxonomy_id,
            "object_type": mapped_type,
            "domain": domain,
            "evidence": legacy_fm.get("evidence", "unverified"),
            "verification": legacy_fm.get("verification", "unverified"),
            "authority": legacy_fm.get("authority", "local_curator"),
            "consensus": consensus,
            "source_type": legacy_fm.get("source_type", "curated"),
            "source_refs": source_refs,
            "author": author,
            "last_modified": legacy_fm.get("last_modified", today_iso),
            "reviewer": "human:operator",
            "last_verified": today_iso,
            "next_review": next_review_iso,
            "confidence": (
                float(legacy_fm["confidence"])
                if "confidence" in legacy_fm
                and isinstance(legacy_fm["confidence"], (int, float, str))
                and str(legacy_fm["confidence"]).replace(".", "", 1).isdigit()
                else 0.5
            ),
            "validity": legacy_fm.get("validity")
            if isinstance(legacy_fm.get("validity"), dict)
            else None,
            "status": "draft",
            "relations": [],
        }

        # Inject required facets if present in legacy or fallback
        FACET_DEFAULTS: Dict[str, Any] = {
            "language": ["en"],
            "audience": migration_map.default_audience
            if migration_map.default_audience
            else "engineer",
            "toolchain": ["none"],
            "lifecycle": "ongoing",
            "architecture": ["none"],
            "prog_language": ["none"],
        }
        required_facets = getattr(obj_spec, "required_facets", []) if obj_spec else []
        for rf in required_facets:
            val = legacy_fm.get(rf)
            if val is not None:
                frontmatter_dict[rf] = val
            elif rf in FACET_DEFAULTS:
                frontmatter_dict[rf] = FACET_DEFAULTS[rf]

        try:
            validated_fm = FrontmatterModel.model_validate(frontmatter_dict)
        except Exception as e:
            return QuarantineRecord(
                file_path=rel_path,
                reason="frontmatter_validation_error",
                error_detail=str(e),
            )

        # 10. Extract link and facet proposals (Rule 4)
        link_proposals: List[LinkProposal] = []
        # Find [[wiki links]]
        for match in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", body_text):
            raw_link = match.group(1).strip()
            link_proposals.append(
                LinkProposal(
                    source_file=rel_path,
                    raw_link=raw_link,
                    inferred_target=None,
                    resolved=False,
                )
            )

        facet_proposals: List[FacetProposal] = []
        # Propose matches for legacy tags against registered facets
        facet_vocab: Dict[str, Set[str]] = {}
        for facet_name, facet_spec in self.registries.facets.items():
            if hasattr(facet_spec, "values"):
                facet_vocab[facet_name] = set(facet_spec.values)
            elif isinstance(facet_spec, dict) and "values" in facet_spec:
                facet_vocab[facet_name] = set(facet_spec["values"])

        for tag in legacy_tags:
            tag_lower = tag.lower()
            for fname, allowed_vals in facet_vocab.items():
                if tag_lower in allowed_vals:
                    facet_proposals.append(
                        FacetProposal(
                            source_file=rel_path,
                            raw_term=tag,
                            facet_name=fname,
                            matched_value=tag_lower,
                            accepted=True,
                        )
                    )
                else:
                    facet_proposals.append(
                        FacetProposal(
                            source_file=rel_path,
                            raw_term=tag,
                            facet_name=fname,
                            matched_value=None,
                            accepted=False,
                        )
                    )

        ko = KnowledgeObject(
            path=Path(rel_path),
            frontmatter_dict=frontmatter_dict,
            raw_body=body_text.strip(),
            frontmatter=validated_fm,
        )

        return ko, link_proposals, facet_proposals, legacy_tags
