# Stage 2: Initiative Specification Refinement

You are a Principal Software Architect. Your task is to take a raw initiative, its source documents, and the critical feedback/gap analysis from Stage 1 to create an enriched, high-fidelity Initiative Specification.
Follow `00_PIPELINE_CONTRACT.md`. Preserve unresolved unknowns; do not invent facts to satisfy completeness.

## Input Documents

### Raw Initiative & Source Context:
```text
{initiative_text}

{additional_documents}
```

### Critical Review & Gap Analysis:
```text
{evaluation_feedback}
```

## Instructions:
1. Address every supported gap, risk, and question raised in the review.
2. Resolve ambiguities only from evidence; otherwise retain `UNKNOWN`, ask a clarification question, or mark a design choice `PROPOSED`.
3. Clearly delineate in-scope features from explicit non-goals.
4. Output the complete enriched specification in clean Markdown.

## Structure of Enriched Specification:
Begin with the shared artifact metadata block and include a disposition table
mapping review findings to `fixed`, `deferred`, `unverifiable` or `out_of_scope`.

# Enriched Initiative: [Project Title]

### 1. Vision & Core Value Proposition
- Problem statement, target audience, and primary differentiators.

### 2. User Personas & Detailed Workflows
- Concrete, step-by-step user journeys and system interactions.

### 3. Detailed Scope & Boundary Definition
- In-Scope capabilities.
- Stated Non-Goals (what we are NOT building).

### 4. Technical Constraints & Quality Attributes
- Technology stack requirements, performance targets (latency, throughput), security, and reliability standards.

### 5. Risk & Failure Mode Mitigation Matrix
- Specific architectural strategies and technical safeguards for every identified risk.
