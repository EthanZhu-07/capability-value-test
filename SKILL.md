---
name: capability-value-test
description: Design and run evidence-backed value tests for newly added tools, integrations, models, skills, or workflows. Use when the user needs a fair baseline comparison, proof that a capability was actually used, an observable process, or a decision about whether the capability is worth adopting. Do not trigger for ordinary functional testing with no adoption or value question.
---

# Capability Value Test

Make a new capability's value perceptible, auditable, and useful for a real adoption decision. The objective is not to make the candidate win.

## Resolve the three uncertainties

Every useful test should address:

1. **Counterfactual uncertainty:** What would happen with the best realistic existing method?
2. **Process opacity:** What can the human observe while the work happens, or inspect afterward?
3. **Provenance uncertainty:** What evidence proves which tool, model, integration, or workflow actually produced the result?

A successful output alone proves functionality. It does not prove superiority or value.

## Frame the decision before testing

State the decision the evidence should support: adopt, keep, remove, make default, or reserve for particular situations. Then define:

- A representative task and identical input data.
- The candidate capability and the best realistic baseline, not a deliberately weak comparator.
- The success rubric, failure conditions, and stopping rule.
- Which differences are intentionally being tested. Keep other conditions as similar as practical.

If a credible baseline does not exist, do not force an A/B test. Choose a better design:

- **A/B comparison:** same task, candidate versus current method.
- **Ablation:** same system with and without the new component.
- **Before/after:** compare a stable historical workflow with the new one.
- **Shadow or canary test:** run on real work without making the candidate the sole production path.
- **Acceptance-threshold test:** test against explicit quality, latency, cost, or reliability requirements.

Use the smallest design that can change the decision.

## Make the comparison fair

- Keep the task, inputs, permissions, environment, expected output, and stopping rule aligned.
- Separate cold start, first-time exploration, optimized repeat, and scaled batch performance. Do not mix them into one timing.
- Measure end-to-end human-visible time as well as engine execution time when both matter.
- Account for caching, login state, prior knowledge, and test order. Randomize or alternate order when they could bias repeated runs.
- Use multiple runs when variability can change the conclusion. For expensive tests, disclose the limited sample rather than implying statistical certainty.
- Preserve failures, retries, fallbacks, and manual interventions in the record.
- Never expand permissions or create external side effects merely to make a test more realistic; obtain any required authorization at action time.

## Build an evidence packet

Collect evidence during the run instead of reconstructing it afterward.

### Provenance

Record the actual tool or model name, version when available, invocation or command, relevant configuration, and returned identifiers or metadata. Redact secrets. Never claim a capability was used when the execution trace does not establish it.

### Process

Prefer a live visible run when the system supports it. For headless or asynchronous systems, provide a timestamped event trail containing meaningful actions, targets, intermediate states, errors, and screenshots or snapshots. Do not manufacture a fake real-time animation.

### Outcome

Preserve the raw result and evaluate it against a reference answer or a task-specific rubric. Measure correctness and completeness before speed.

### Efficiency and reliability

Record elapsed time, tool calls, tokens or credits when known, manual interventions, error count, and success rate across repeats. Label unavailable measurements instead of estimating them as facts.

### Reproducibility

Save or report the prompt, script, configuration, data scope, and test date needed to repeat the result. Do not persist an artifact unless the user requested it or it is a normal, in-scope part of the test.

## Execute visibly

Before each arm, tell the user which method is starting and what evidence will appear. During long runs, provide concise progress without revealing hidden reasoning. When the user wants to watch a visible baseline, keep that run visible; for a headless candidate, expose the event trail and intermediate proof as it happens.

Run each arm independently. Do not silently reuse the candidate's output in the baseline or vice versa. If the candidate depends on a discovery phase followed by deterministic replay, report both phases separately because they answer different value questions.

## Judge value, not novelty

Prioritize metrics in this order unless the task requires otherwise:

1. Correctness, completeness, and safety.
2. Reliability and recoverability.
3. End-to-end time and human effort.
4. Direct cost and resource use.
5. Observability, auditability, and reproducibility.
6. Scale, only when tested at a representative scale.

A capability may be valuable only for a subset of tasks. State where it wins, where it loses, and the break-even condition instead of forcing a universal verdict.

## Deliver the result

Use a compact report with:

- **Decision:** what adoption question was tested.
- **Test design:** task, baseline, candidate, controls, sample size, and limitations.
- **Evidence manifest:** tool traces, screenshots, logs, raw outputs, scripts, or identifiers actually available.
- **Results table:** baseline, candidate, delta, confidence, and supporting evidence for each important metric.
- **Verdict:** `adopt`, `conditional`, `reject`, or `inconclusive`.
- **Operating boundary:** when to use the candidate and when to keep the baseline.
- **Next test:** only if missing evidence could realistically change the decision.

End with one plain statement of what this test did and did not establish.

## Integrity rules

- Do not describe a tool call, live process, timing, cost, or result that was not observed.
- Distinguish agent reasoning latency, tool round-trip time, and underlying engine time when the instrumentation allows it.
- Do not infer quality from speed or visual polish.
- Do not cherry-pick only successful runs.
- A candidate losing is a valid and useful outcome.
- If provenance or instrumentation is insufficient, return `inconclusive` and name the missing evidence.
