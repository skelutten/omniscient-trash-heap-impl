---
id: ENG-SEQ-INGEST-0001
title: "Source Intake to Staging Sequence Flow"
schema_version: "3.8.10"
keywords: [sequence, ingestion, staging, flow]
scope: engineering
taxonomy_path: "01. Core Platform & Runtime Architecture"
taxonomy_id: TX-ENG-01
object_type: Sequence
domain: platform_runtime
architecture: [container]
evidence: observed
verification: peer_verified
authority: authoritative
consensus: accepted
source_type: internal_document
source_refs: ["specs/INGEST-PIPELINE.md"]
author: human:daniel
last_modified: "2026-08-27"
reviewer: human:daniel
last_verified: "2026-08-27"
confidence: 0.95
status: established
validity:
  valid_from: "2026-08-01"
  valid_until: null
relations:
  - {type: PART_OF, target: ENG-PRT-PROMO-0001}
---

# Source Intake to Staging Sequence Flow

## Summary
Execution sequence: raw payload -> injection fence -> SHA-256 staging record.
