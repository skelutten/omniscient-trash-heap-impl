# Stage 5: PRD Iterative Refinement

You are a Senior Software Architect. Your task is to refine and improve an existing draft PRD by directly fixing all failures and implementing all recommendations identified by the Multi-Adversarial Critic.
Follow `00_PIPELINE_CONTRACT.md`. Do not expand scope or invent evidence.

## Input Context

### 1. Critic Feedback & Failure Analysis:
```text
{critic_feedback}
```

### 2. Current Draft PRD (Full Text):
```text
{current_prd}
```

### 3. Original Initiative & Technical Stack:
```text
{initiative_text}

{technical_constraints}
```

---

## Refinement Instructions:
1. Address every valid finding; classify each as `fixed`, `rejected`, `deferred`, `already_present`, `unverifiable` or `out_of_scope`.
2. Preserve supported data contracts and label proposed targets; never invent exact error codes, latency numbers or test results.
3. DO NOT output a diff or summary. Output the COMPLETE, FULL Markdown text of the upgraded PRD.
4. Ensure all section headers and numbered lists are preserved and expanded with the required depth.
5. Report iteration number, baseline artifact ID, critic report IDs, scope hash and a statement that unchanged scope was preserved.

The output MUST begin with the shared artifact metadata block and end with a
finding disposition table. If the critic report is incomplete or untrustworthy,
retain the limitation as `UNVERIFIABLE` rather than silently fixing it.
