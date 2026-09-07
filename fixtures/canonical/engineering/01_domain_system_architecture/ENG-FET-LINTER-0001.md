---
id: ENG-FET-LINTER-0001
title: Five Layer Deterministic Validation Engine
schema_version: 3.8.10
keywords:
- linter
- validation
- error-codes
- layer1-5
scope: engineering
taxonomy_path: 01. Domain & System Architecture
taxonomy_id: TX-ENG-01
object_type: Feature
domain: runtime_frameworks
toolchain:
- pytest
- ruff
prog_language:
- python
lifecycle: delivered
evidence: observed
verification: formal_proof
authority: normative
consensus: accepted
source_type: internal_document
source_refs:
- specs/VALIDATION.md
author: human:daniel
last_modified: '2026-08-27'
reviewer: human:daniel
last_verified: '2026-08-27'
confidence: 1.0
status: established
validity:
  valid_from: '2026-08-01'
  valid_until: null
relations:
- type: PART_OF
  target: ENG-PRD-LLMWIKI-0001
next_review: '2027-02-17'
---



# Five Layer Deterministic Validation Engine

## Summary
Validates frontmatter, structural IDs, semantic facets, DAG cycles, and cross-object referential integrity.
