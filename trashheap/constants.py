"""Package constants, error codes, and exit codes for The Omniscient Trash Heap."""

from enum import IntEnum

VERSION = "3.8.10"
DEFAULT_SCHEMA_VERSION = "3.8.10"


class ExitCode(IntEnum):
    """Deterministic CLI exit codes (VALIDATION.md §Exit Codes)."""

    SUCCESS = 0
    VALIDATION_ERROR = 1
    STRICT_WARNING = 2
    CONFIG_OR_ARG_ERROR = 3
    NOT_FOUND = 4


# Metadata Categories (META-001)
METADATA_CATEGORIES = {
    "IDENTITY": {"id", "title", "schema_version", "aliases", "keywords"},
    "ORGANIZATION": {"scope", "taxonomy_path", "taxonomy_id"},
    "CLASSIFICATION": {"object_type", "domain"},
    "FACETS": {
        "toolchain",
        "prog_language",
        "language",
        "audience",
        "architecture",
        "lifecycle",
        "test_level",
    },
    "EPISTEMOLOGY": {"evidence", "verification", "authority", "consensus"},
    "PROVENANCE": {
        "source_type",
        "source_refs",
        "author",
        "last_modified",
        "reviewer",
        "last_verified",
        "next_review",
        "confidence",
    },
    "TEMPORAL": {"validity"},
    "GOVERNANCE": {"status"},
    "ONTOLOGY": {"relations"},
}

ALL_FRONTMATTER_FIELDS = set().union(*METADATA_CATEGORIES.values())

# Regex patterns
ID_PATTERN = r"^(PERS|ENG)-[A-Z]{2,5}-[A-Z0-9][A-Z0-9_]*-([0-9]{4})$"
YEAR_TAG_PATTERN = r"^[0-9]{4}$"
DOMAIN_TAG_PATTERN = r"^[A-Z0-9][A-Z0-9_]*$"
ACTOR_PATTERN = r"^(human:[a-z0-9._-]+|process:[a-z0-9._-]+|[a-z0-9._-]+/[A-Za-z0-9._-]+)$"

# Registry files
REGISTRY_FILES = [
    "object_registry.yaml",
    "relation_registry.yaml",
    "taxonomy_registry.yaml",
    "epistemic_registry.yaml",
    "governance_policy.yaml",
    "facet_registry.yaml",
    "source_registry.yaml",
    "actor_registry.yaml",
    "threshold_policy.yaml",
    "spec_ownership.yaml",
]
