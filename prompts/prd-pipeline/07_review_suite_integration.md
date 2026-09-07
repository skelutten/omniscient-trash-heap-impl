# Stage 7: Specification Review Suite (Reviewers 01–08 & Arbitrator)

> **Source**: Integrated from `prompts/review/` (`01_initiative_and_spec_richness.md` through `08_review_arbitrator.md`)
> **Role**: Formal 8-reviewer audit and arbitration gate over generated specifications and PRDs.
> **Shared contract:** Apply `00_PIPELINE_CONTRACT.md`.

---

## Reviewer Roster:
1. **Reviewer 01 (Initiative & Spec Richness):** Evaluates semantic completeness, workflows, and concrete examples.
2. **Reviewer 02 (Critical Systems Reasoning):** Analyzes missing constraints, unaddressed risks, and failure modes.
3. **Reviewer 03 (Anti-Clerk & Vision Preservation):** Enforces active intelligence and prevents reduction to hollow CRUD infrastructure.
4. **Reviewer 04 (Adversarial Red Team & PreMortem):** Evaluates attack vectors, race conditions, and catastrophic failure paths.
5. **Reviewer 05 (First Principles & Socratic Gaps):** Challenges core assumptions and validates irreducible truths.
6. **Reviewer 06 (Temporal & Second-Order Effects):** Maps critical path dependencies, feedback loops, and long-term coupling.
7. **Reviewer 07 (Tactical Conformance & Error Code Audit):** Verifies linter error codes (`E001`–`E099`), schema registry alignment, and Agent Skill compliance.
8. **Reviewer 08 (Review Arbitrator):** Synthesizes all 7 reviewer findings, resolves conflicts, and issues the final PASS / REVISE / BLOCK verdict.

## Execution contract

The caller MUST provide a corpus manifest and explicitly select `fresh` or
`delta` mode. Reviewers 01–07 MUST receive the same corpus boundary and return
evidence-bound reports with exact artifact references, conservative severity,
explicit `UNVERIFIABLE` status for unavailable companions, and a machine-readable
findings manifest. Reviewer 08 is executed separately using
`08_review_arbitrator.md`; it MUST receive all returned reports and MUST account
for each finding exactly once. A roster entry is not evidence that its report or
implementation exists.
