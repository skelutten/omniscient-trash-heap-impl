# Advanced Cognitive Reasoning Modules & Markdown Synthesis

> **Source**: Adapted from `theloop_v5/reasoning/cot_prompts.py`
> **Usage**: Specialized cognitive lenses attached to `THINKING_PROMPT_BASE` for deep multi-dimensional reasoning on PRDs and specifications.
> **Shared contract:** Apply `00_PIPELINE_CONTRACT.md`.

---

## 1. TEMPORAL THINKING (`TEMPORAL_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for Temporal/Causal Chain:
- Map the critical path: What MUST happen in what order?
- Identify feedback loops and delays in the system.
- Find "time bombs" — decisions that lock you in or expire.
- Distinguish between leading vs. lagging indicators of success.
- What dependencies create invisible coupling across time?

Output Format (Markdown):
### Temporal & Causal Analysis
- **Critical Path:** [Ordered sequence of dependency milestones]
- **Feedback Loops & Delays:** [System dynamics]
- **Identified Time Bombs:** [Risky long-term coupling]
- **Leading vs. Lagging Indicators:** [Measurable signals]
```

---

## 2. SECOND-ORDER THINKING (`SECOND_ORDER_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for Consequence Analysis:
- For each proposed action/design, trace immediate (1st order) effects.
- Then trace effects of those effects (2nd order).
- Identify at least one 3rd order consequence that's non-obvious.
- Look for "what happens next Tuesday" vs "what happens next year".
- Flag unintended incentive structures created by decisions.

Output Format (Markdown):
### Second-Order Consequence Analysis
- **First-Order Immediate Effects:** [Direct consequence]
- **Second-Order Systemic Effects:** [Follow-on consequence]
- **Unintended Incentive Structures / 3rd-Order Effects:** [Long-term systemic impact]
```

---

## 3. RESOURCE OPTIMIZATION THINKING (`RESOURCE_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for Resource Optimization:
- Identify the binding constraint (single most limiting factor).
- Map trade-offs: speed vs quality vs scope vs risk.
- Calculate "opportunity cost" of each major decision.
- Find waste: Where are resources being consumed without value?
- What's the marginal benefit of additional effort in each area?
- Distinguish between reusable vs. consumable resources.

Output Format (Markdown):
### Resource Optimization & Constraints
- **Binding Constraint:** [Single most limiting operational or compute factor]
- **Core Trade-offs:** [Speed vs. Quality vs. Complexity]
- **Opportunity Costs:** [What is sacrificed by this choice]
```

---

## 4. EPISTEMIC THINKING (`EPISTEMIC_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for Information Quality:
- Classify each key piece of information: Known-known, known-unknown, unknown-unknown.
- Rate confidence sources: empirical, derived, assumed, speculative.
- Identify what evidence would change your conclusions (falsifiability).
- Find hidden information asymmetries in the system.
- What signals are reliable vs. noisy?
- What critical information is missing entirely?

Output Format (Markdown):
### Epistemic Quality Analysis
- **Known-Knowns (Empirical Ground Truth):** [Verified facts]
- **Known-Unknowns (Explicit Gaps):** [Gaps to investigate]
- **Falsifiability Criteria:** [What evidence disproves our assumptions]
```

---

## 5. LEVELS OF ABSTRACTION THINKING (`LEVELS_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for Abstraction Levels:
- Explicitly state the current abstraction level (strategy, architecture, implementation, etc.)
- What looks correct at this level but breaks at the level below?
- What constraints from higher levels are invisible at this level?
- What details at this level create accidental complexity at other levels?
- Map the "vertical slice": How does a change propagate across levels?
- Identify abstraction leaks and boundary violations.

Output Format (Markdown):
### Levels of Abstraction & Boundary Verification
- **Current Abstraction Level:** [Strategy / Architecture / Implementation]
- **Vertical Slice Propagation:** [How decisions flow down to code]
- **Identified Abstraction Leaks:** [Boundary violations]
```

---

## 6. CALIBRATED PREMORTEM (`PREMORTEM_CALIBRATED`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for PreMortem with Calibration:
- Assume the initiative or task has already failed catastrophically.
- Work backwards: What are the most likely root causes?
- For EACH identified failure mode, explicitly rate:
  * LIKELIHOOD (1-10): How probable is this failure path?
  * IMPACT (1-10): How severe would the consequences be?
  * DETECTABILITY (1-10): How hard would it be to see coming?
- Calculate a CRITICALITY SCORE = Likelihood × Impact
- Prioritize failure modes with Criticality > 50 or Detectability > 8
- What early warning signs would have been missed? Rate detection delay (hours/days/weeks)
- What specific preventive actions would reduce Likelihood by >= 3 points?

Output Format (Markdown):
### Calibrated PreMortem & Failure Ranking

| Failure Mode | Likelihood (1-10) | Impact (1-10) | Criticality (L x I) | Detectability (1-10) | Preventive Mitigation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `[Failure description]` | `[1-10]` | `[1-10]` | `[Score]` | `[1-10]` | `[Concrete technical safeguard]` |

- **Top 3 Priorities Demanding Immediate Mitigation:**
  1. `[Priority 1]`
  2. `[Priority 2]`
  3. `[Priority 3]`
```

---

## 7. CROSS-HATCH SYNTHESIS (`CROSS_HATCH_SYNTHESIS`)

```text
You are a meta-reasoning integrator in the cognitive architecture pipeline.

You have received TWO independent reasoning traces on the same artifact, using different thinking modes.

### Your Synthesis Task:
1. **Convergence** — Where do both modes agree? These are HIGH confidence insights.
2. **Contradictions** — Where do they disagree? Resolve by identifying different assumptions, horizons, or risk appetites.
3. **Synergies** — Does one mode's insight enable or block the other's recommendation?
4. **Integrated Recommendations** — Combine the best of both, explicitly noting trade-offs.

Artifact: {artifact}

Output Format (Markdown):
# Cross-Hatch Synthesis Report

## 1. High-Confidence Convergent Insights
- [Insight 1]

## 2. Resolved Contradictions & Reconciled Assumptions
- [Contradiction and resolution]

## 3. Integrated Architectural Recommendations
- [Unified recommendation]
```

---

## 8. STRAW MAN STRENGTHENING (`STRAW_MAN_STRENGTHENING`)

```text
You are an iterative design critic in the cognitive architecture pipeline.

### Phase 1: Build the Straw Man
Produce the WEAKEST possible solution that technically addresses requirements. Be deliberately naive.

### Phase 2: Attack the Straw Man
Apply Red Team + Black Hat thinking to demolish it. List minimum 8 distinct flaws.

### Phase 3: Iterative Strengthening
Fix the flaws across versions (v1, v2, hardened).

Artifact: {artifact}

Output Format (Markdown):
# Straw Man Hardening Report

## 1. Naive Straw Man & Flaw Demolition (Min 8 Flaws)
1. [Flaw 1]
2. [Flaw 2]
...
8. [Flaw 8]

## 2. Hardened Architecture & Residual Unfixable Trade-offs
- **Hardened Specification:** [Detailed robust design]
- **Residual Trade-offs:** [Explicitly accepted limitations]
```
