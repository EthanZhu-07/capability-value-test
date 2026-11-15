---
name: capability-value-test
description: Design and run evidence-backed value tests for newly added or proposed tools, integrations, models, skills, and workflows. Use when deciding whether a capability is worth adopting, comparing it with the current method, making an invisible AI process perceptible, or proving that a claimed capability was actually used. Do not trigger for ordinary functional testing with no adoption or value question.
---

# Capability Value Test

Make a new capability's value perceptible, auditable, and useful for a real adoption decision. The objective is not to make the candidate win.

## Resolve three uncertainties

Every test must address:

1. **Counterfactual:** What happens with the best realistic existing method?
2. **Observability:** What can the human watch live or inspect afterward?
3. **Provenance:** What system evidence proves which capability actually produced the result?

The assistant's statement that it used a tool is not provenance evidence. A successful output proves functionality, not superiority or value.

## Pre-register the test

Before running either arm, show a compact test contract containing:

- The adoption decision: make default, use conditionally, reject, keep testing, or remove.
- The candidate and the user's actual current method as baseline. Do not invent a weak comparator.
- One representative task, identical inputs, expected output, permissions, environment, and stopping rule.
- Primary success metric, guardrails, and evidence to capture during each arm.
- Known confounders such as cache, login state, prior discovery, run order, and unavailable instrumentation.

Do not wait for confirmation unless a missing choice would materially change the test or an action requires authorization. Do not change the metrics after seeing the results; disclose any necessary deviation.

Read [references/test-card.md](references/test-card.md) when designing or executing a test. Use its contract, evidence ledger, grading scales, and result template.

## Choose the smallest valid design

- **A/B:** Same task, candidate versus current method.
- **Ablation:** Same system with and without the new component.
- **Before/after:** Stable historical workflow versus the new workflow.
- **Shadow or canary:** Candidate runs on real work without becoming the sole production path.
- **Acceptance threshold:** Use explicit requirements when no credible comparator exists.

Use the design that can change the decision. Do not force an A/B test where the arms cannot be made meaningfully comparable.

## Keep comparisons fair

- Run each arm independently. Never reuse one arm's answer as the other's hidden input.
- Separate setup, cold start, first exploration, optimized repeat, and scaled batch performance. These answer different questions.
- Report end-to-end human-visible time separately from engine or tool execution time when instrumentation permits.
- Account for cache, warm state, network conditions, prior knowledge, run order, and manual interventions.
- Repeat runs when variability could reverse the decision. With a small sample, narrow the conclusion rather than implying statistical certainty.
- Preserve failures, retries, fallbacks, and human help. Candidate losses are valid results.
- Keep permissions and side effects within the user's request. Realism does not authorize additional external actions.

## Collect evidence during execution

Do not reconstruct evidence from memory after the run.

### Provenance

Capture host-visible tool calls or commands, timestamps, actual tool or model name, version when available, relevant configuration, raw output metadata, and returned identifiers. Redact secrets. If the environment cannot establish that the claimed capability ran, mark provenance insufficient and return `inconclusive` for that claim.

### Observability

Use the highest truthful level the system supports:

- Prefer a live visible run when available.
- For headless or asynchronous systems, expose a timestamped action trail, intermediate snapshots, errors, and final artifacts as the run proceeds.
- Never simulate a live process that did not occur.

Headless operation is not automatically a defect, but its reduced visual observability must be disclosed and compensated with stronger provenance and reproducibility evidence.

### Outcome, efficiency, and reproducibility

Preserve raw outputs and score correctness, completeness, and safety before speed. Record elapsed time, tool calls, known tokens or credits, human interventions, errors, and repeat success rate. Save or report the prompt, script, configuration, data scope, and test date required to repeat the result. Label unavailable measurements; do not estimate them as facts.

## Execute visibly

Before each arm, state which method is starting and what proof the user will see. During long runs, provide concise progress. Give every material artifact an evidence ID from the ledger so a claim can point to its source.

When discovery is followed by deterministic replay, report both phases separately. First-run exploration measures adaptability; replay measures repeat-work efficiency. Do not average them into one number.

## Decide value

Prioritize unless the task requires otherwise:

1. Correctness, completeness, and safety.
2. Reliability and recoverability.
3. End-to-end time and human effort.
4. Direct cost and resource use.
5. Observability, provenance, and reproducibility.
6. Scale, only when tested at representative scale.

Return one verdict:

- `adopt`: evidence supports making the candidate the normal method.
- `conditional`: candidate wins only under stated conditions or above a break-even point.
- `reject`: current evidence supports keeping the baseline.
- `inconclusive`: missing, invalid, or conflicting evidence could change the decision.

State where the capability wins, where it loses, and the break-even condition. Do not force a universal verdict for a capability that serves only a subset of tasks.

## Integrity rules

- Never claim a tool call, live process, timing, cost, or result that was not observed.
- Do not use assistant narration alone as evidence that a capability ran.
- Do not infer quality from speed, novelty, or visual polish.
- Do not cherry-pick successful runs or hide fallback use.
- Distinguish observed fact, calculated metric, and interpretation.
- End with one plain statement of what the test established and what it did not.
