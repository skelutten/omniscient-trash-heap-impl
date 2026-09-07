# Specialized Cognitive Reasoning Modules (CoT Suite)

> **Source**: Extracted from `theloop_v5/reasoning/cot_prompts.py`
> **Usage**: Plug into `THINKING_PROMPT_BASE` for targeted architectural analysis.
> **Shared contract:** Apply `00_PIPELINE_CONTRACT.md`.

---

## 1. FIRST PRINCIPLES THINKING (`FIRST_PRINCIPLES_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for First Principles:
- Break the problem down to irreducible truths and fundamental constraints.
- Challenge every assumption explicitly.
- Identify what would make the goal impossible or trivial.
- Distinguish between essential vs. accidental complexity.
```

---

## 2. PREMORTEM THINKING (`PREMORTEM_THINKING` & `PREMORTEM_CALIBRATED`)

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
- What specific preventive actions would reduce Likelihood by ≥3 points?

After calibration, list the top 3 failure modes that demand immediate mitigation.
```

---

## 3. RED TEAM THINKING (`RED_TEAM_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for Red Team:
- Act as an adversarial attacker trying to break the design, specification, or plan.
- Identify the weakest points and most dangerous attack vectors.
- Think like a malicious or incompetent developer who wants to cause maximum damage.
- List concrete ways the current approach can be exploited or will fail under stress.
```

---

## 4. SOCRATIC QUESTIONING (`SOCRATIC_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for Socratic Questioning:
- Generate sharp, probing questions that expose ambiguities, gaps, and contradictions.
- Challenge vague terms, unstated assumptions, and implicit requirements.
- Ask "what if" questions that test edge cases and robustness.
- Prioritize questions that would force meaningful clarification or redesign.
```

---

## 5. INVERSION THINKING (`INVERSION_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for Inversion:
- Invert the desired outcome: What specific actions would GUARANTEE failure or the opposite result?
- Identify where the current specification or design already enables those failure modes.
- Derive strong, enforceable constraints and tests from the inversions.
- Turn every sabotage path into a preventive requirement.
```

---

## 6. STRAW MAN STRENGTHENING (`STRAW_MAN_THINKING`)

```text
[THINKING_PROMPT_BASE]

Additional Focus for Straw Man Reasoning:
- Phase 1: Build the WEAKEST possible solution that technically addresses requirements. Be deliberately naive.
- Phase 2: Attack the Straw Man — Apply Red Team + Black Hat thinking to demolish it. Identify minimum 8 distinct flaws.
- Phase 3: Iterative Strengthening — Fix the flaws across versions (v1, v2, hardened).
- Track what flaws are unfixable and represent genuine trade-offs.
```
