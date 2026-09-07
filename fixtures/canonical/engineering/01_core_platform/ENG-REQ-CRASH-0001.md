---
id: ENG-REQ-CRASH-0001
title: "Zero Truncation Crash Safety via Atomic Writes"
schema_version: "3.8.10"
keywords: [requirement, crash-safety, atomic-writes, posix]
scope: engineering
taxonomy_path: "01. Core Platform & Runtime Architecture"
taxonomy_id: TX-ENG-01
object_type: Requirement
domain: platform_runtime
lifecycle: ongoing
evidence: derived
verification: peer_verified
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["PRD.md"]
author: human:daniel
last_modified: "2026-08-27"
reviewer: human:daniel
last_verified: "2026-08-27"
confidence: 1.0
status: established
validity:
  valid_from: "2026-08-01"
  valid_until: null
relations:
  - {type: PART_OF, target: ENG-FET-LINTER-0001}
---

# Zero Truncation Crash Safety via Atomic Writes

## Summary
All file replacements must execute via .tmp file creation and atomic rename.
