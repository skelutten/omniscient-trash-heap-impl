---
id: ENG-IFC-CLI-0001
title: "Command Line Interface Contract"
schema_version: "3.8.10"
keywords: [interface, cli, commands, exit-codes]
scope: engineering
taxonomy_path: "01. Core Platform & Runtime Architecture"
taxonomy_id: TX-ENG-01
object_type: Interface
domain: platform_runtime
architecture: [baremetal]
evidence: observed
verification: peer_verified
authority: normative
consensus: accepted
source_type: internal_document
source_refs: ["specs/ARCHITECTURE.md"]
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

# Command Line Interface Contract

## Summary
CLI command structure for lint, validate, rebuild, query, and stage-lint.
