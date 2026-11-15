# Test Card and Evidence Ledger

Use this template when the Skill moves from discussion into test design or execution. Keep it proportional: a low-cost comparison can fit in one compact message, while a consequential adoption decision needs a fuller record.

## 1. Pre-registered test contract

```markdown
### Value test contract

- Decision: [make default / conditional use / reject / keep testing / remove]
- Candidate: [capability and version/configuration when known]
- Baseline: [the user's realistic current method]
- Representative task: [exact task and input scope]
- Sample and repetitions: [items, runs, or reason one run is enough]
- Controlled conditions: [same inputs, permissions, environment, output format, stopping rule]
- Primary metric: [the metric that determines the decision]
- Guardrails: [quality, safety, reliability, cost, or side-effect limits]
- Hypothesis: [where the candidate is expected to win and why]
- Provenance plan: [which host-visible calls, logs, versions, IDs, or artifacts will prove execution]
- Observability plan: [live view, timestamps, snapshots, screenshots, or event trail]
- Known confounders: [cache, warm state, run order, prior discovery, login, network]
- Stop rule: [success, failure, budget, time, or safety boundary]
```

If the contract changes after a run starts, record the change and reason before interpreting the result.

## 2. Evidence ledger

Give each material item a stable ID. Keep raw evidence or a usable link/path when the environment allows it.

| Evidence ID | Time | Arm | Observed action or state | Evidence type | Result / location |
|---|---|---|---|---|---|
| B1 | | Baseline | | tool call / screenshot / log / output | |
| C1 | | Candidate | | tool call / screenshot / log / output | |

Distinguish:

- **Observed fact:** directly present in a trace, output, screenshot, or artifact.
- **Calculated metric:** derived from observed timestamps or counts; show the calculation when non-obvious.
- **Interpretation:** a conclusion that may depend on the rubric or decision context.

## 3. Provenance grade

- **P0 — assertion only:** The assistant says it used the capability. Invalid as proof.
- **P1 — invocation observed:** The host shows the tool call or command with the candidate's identity.
- **P2 — invocation plus output:** P1 plus raw result, returned metadata/ID, version, or configuration sufficient to connect invocation to outcome.
- **P3 — independently reproducible:** P2 plus a runnable script, trace, artifact, or procedure that another run can verify.

Minimum acceptable proof of use is P1. Aim for P2 when making adoption claims and P3 when repeatability is central to the value proposition.

## 4. Observability grade

- **O0 — final result only:** No process visibility.
- **O1 — narrated progress:** Human sees status messages but cannot independently inspect actions.
- **O2 — inspectable trail:** Timestamped actions plus intermediate snapshots, logs, or screenshots.
- **O3 — live visible process:** Human can watch the real execution as it occurs.

Do not label narrated progress as live visibility. A headless candidate normally cannot reach O3; compensate with P2/P3 provenance and an O2 trail where feasible.

## 5. Result report

```markdown
### Result

- Test validity: [valid / partially valid / invalid, with confounders]
- Sample size: [runs/items]
- Provenance: [baseline grade, candidate grade, evidence IDs]
- Observability: [baseline grade, candidate grade, evidence IDs]

| Metric | Baseline | Candidate | Delta | Confidence | Evidence |
|---|---:|---:|---:|---|---|
| Correctness / completeness | | | | | |
| Success rate | | | | | |
| End-to-end elapsed time | | | | | |
| Engine/tool execution time | | | | | |
| Human interventions | | | | | |
| Direct cost / resource use | | | | | |

- Verdict: [adopt / conditional / reject / inconclusive]
- Where candidate wins: [...]
- Where baseline wins: [...]
- Break-even condition: [...]
- Material limitations: [...]
- Next test: [only if evidence could change the decision]

Established: [one plain statement].
Not established: [one plain statement].
```

Omit irrelevant metrics rather than filling the table with guesses. Add task-specific quality measures when they matter more than the generic rows.
