# Stage 0: Initiative & Input Artifact Generation Suite

> **Source**: Integrated from `prompts/artifact-generation.md` & `prompts/artifact-output-reference.md`
> **Role**: Generates a synchronized bundle of human-readable discovery documents (`input-artifacts/`) and machine-readable `initiative.yaml` from raw product notes.
> **Shared contract:** Apply `00_PIPELINE_CONTRACT.md`.

---

## Task
Generate the requested artifact bundle as separate Markdown files:
1. `initiative.md` (Identity, Intent, Users, Success Metrics, Constraints, Non-Goals, Inspirations, Acceptance Criteria)
2. `market_analysis.md` (Overview, Target Segments, Competitors, Workarounds, Trends, Risks)
3. `opportunity_brief.md` (Problem, Jobs to be Done, Alternatives, High-level Solution, Value Proposition)
4. `problem_statement.md` (Summary, Affected Users, Root Causes, Impact, Evidence, Assumptions)
5. `user_research_notes.md` (Research Objective, Behavioral Observations, Quotes, Pain Points, Studio Paradigm)
6. `initiative.yaml` (Synchronized machine-readable YAML projection)

---

## Inputs
- `name`: initiative or product name
- `description`: concise problem and goal description
- `context`: known domain, users, constraints, references, goals, scope
- `evidence`: observations, data, market sources, and research references

---

## Generation Rules
1. Never invent unsupported features or market sizes; record explicit unknowns as `UNKNOWN` or `TO_VALIDATE` and preserve their source.
2. Preserve raw intent, observations, assumptions, conflicts and evidence before proposing technical structure. Do not force discovery input into taxonomy, object type, domain, epistemology or relation fields unless supported by input or explicitly marked `PROPOSED`.
3. External paradigms are optional context, not evidence. Do not assert alignment with Karpathy's LLM Wiki pattern, Agent Skills, OKF, Graphify or Studio unless the supplied sources support the claim.
4. Emit a bundle manifest containing required file names, bundle ID, source references, evidence status and Markdown/YAML parity notes. The YAML projection MUST NOT silently discard content present in the Markdown artifacts.
