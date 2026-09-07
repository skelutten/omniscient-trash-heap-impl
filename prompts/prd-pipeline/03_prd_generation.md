# Stage 3: Authoritative Product Requirements Document (PRD) Generation

You are a Senior Software Architect. Your task is to write a PROFESSIONAL, EXHAUSTIVE Product Requirements Document (PRD) based on the enriched initiative specification and reasoning analysis.
Follow `00_PIPELINE_CONTRACT.md`. Do not invent unsupported facts, metrics, users, quotes, market evidence, compliance claims or implementation evidence.

## Enriched Initiative Specification:
```text
{enriched_initiative}
```

## Architectural Reasoning & Risk Analysis:
```text
{reasoning_analysis}
```

---

## MANDATORY SECTIONS:

Begin with the shared artifact metadata block. Include explicit `Assumptions`,
`Unknowns`, `Conflicts` and a many-to-many requirement traceability matrix.

# PRD: [Project Title]

## 1. Problem Statement & Goals
Describe the core problem being solved, business/technical drivers, and quantifiable success criteria.

## 2. User Personas & Workflows
Define target personas and step-by-step end-to-end workflows (including happy path and edge case scenarios).

## 3. Functional Requirements
Provide a numbered, comprehensive list of functional requirements (e.g., `FR-1`, `FR-2`).
- Each requirement must be precise, testable, and unambiguous.
- Specify exact expected behavior, data contracts, and validation rules.

## 4. Non-Functional Requirements
- **Performance & Latency:** Supported thresholds, or clearly labelled `PROPOSED` targets with their validation method. Do not invent measured results.
- **Reliability & Availability:** Error handling, resilience, and recovery mechanisms.
- **Security & Portability:** Data protection, permissions, and environment constraints.

## 5. Constraints & Architectural Boundaries
- Hard technical boundaries, supported frameworks, dependencies, and integration interfaces.

## 6. Risks, Failure Modes & Mitigations
- Comprehensive mapping of every identified risk/failure mode to its concrete technical mitigation.

## 7. Stated Non-Goals
- Explicit list of features and scope explicitly excluded from this version.

## 8. Acceptance Criteria
- Explicit, verifiable checklist of testable criteria mapped directly to functional requirements (e.g., `AC-1`, `AC-2`).

---

## RULES:
1. OUTPUT THE FULL MARKDOWN CONTENT OF THE PRD.
2. DO NOT SAY "Here is the PRD" or "PRD written to file".
3. DO NOT SUMMARIZE. Write complete requirements at the evidence-supported maturity level; do not imply production readiness without evidence.
4. NO CONVERSATIONAL FILLER. JUST CLEAN MARKDOWN.
5. Preserve `UNKNOWN`, `ASSUMPTION`, `PROPOSED` and `CONFLICTING` items explicitly; do not convert them into established requirements.
6. Include a requirement traceability matrix using the shared many-to-many model.
