---
id: ENG-CMP-PARSER-0001
title: Pydantic Frontmatter Parser Module
schema_version: 3.8.10
keywords:
- parser
- pydantic
- frontmatter
- yaml
scope: engineering
taxonomy_path: 01. Domain & System Architecture
taxonomy_id: TX-ENG-01
object_type: Component
domain: runtime_frameworks
prog_language:
- python
toolchain:
- pytest
- ruff
lifecycle: delivered
evidence: observed
verification: peer_verified
authority: authoritative
consensus: accepted
source_type: code_repository
source_refs:
- src/trashheap/models.py
author: duckburg-agent/vibe-coder
last_modified: '2026-08-27'
reviewer: human:daniel
last_verified: '2026-08-27'
confidence: 0.95
status: established
validity:
  valid_from: '2026-08-01'
  valid_until: null
relations:
- type: PART_OF
  target: ENG-FET-LINTER-0001
next_review: '2027-02-17'
---



# Pydantic Frontmatter Parser Module

## Summary
Implements zero-drift parsing with extra=forbid and strict type coercion.

Related: [ENG-FET-LINTER-0001](ENG-FET-LINTER-0001.md).
