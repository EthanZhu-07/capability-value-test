---
name: capability-value-test
description: Design and run a visual A/B test for a new AI capability. Use when a user wants proof that a Skill, model, plugin, MCP server, browser, or tool was invoked and wants to compare its quality, time, tokens, or cost with the current method. Requires plan approval and delivers an HTML report.
---

# Capability Value Test

Turn “Is this new capability actually valuable?” into a small experiment the user can inspect rather than a claim they must trust.

Deliver a standalone HTML report that shows:

- whether the candidate capability was verifiably invoked;
- how the current method and candidate performed the same real task;
- how their result quality and end-to-end time compare;
- token usage and cost when the host actually exposes them;
- where the candidate is useful, where it is not, and whether to adopt it.

One run provides directional evidence only. Never present it as universal proof.

## Use this Skill when

- a user has added a new Skill, model, plugin, MCP server, browser, open-source tool, or workflow;
- the capability operates partly or entirely out of sight;
- the user wants to compare it with their existing method;
- the user asks whether it saves time, tokens, money, or improves the result;
- the user wants an HTML artifact that visualizes the process and conclusion.

Do not use it for ordinary “does this function work?” checks, formal statistical experiments, or comparisons where the two methods cannot perform the same task.

## Minimum inputs

Determine four things:

1. **Candidate** — the newly added capability.
2. **Baseline** — the user's real current method.
3. **Representative task** — one real task both methods can complete.
4. **Primary value question** — usually quality, elapsed time, tokens, or cost.

Infer these from the conversation and environment when reliable. If a missing choice would materially change the test, ask one combined question instead of interviewing the user field by field. If no baseline is supplied, propose a realistic one.

## Invariants

- Give both arms the same task, inputs, goal, output requirements, and stopping rule.
- Execute each arm independently. Do not pass one arm's answer to the other.
- An assistant statement such as “I used the tool” is not proof of invocation.
- Invocation proof must come from host-visible tool calls, commands, logs, task metadata, or raw outputs that identify the capability.
- Never fabricate time, tokens, cost, logs, screenshots, commands, or execution events.
- Display unavailable metrics as “Not available”; never convert missing data to zero.
- Do not present a reconstructed headless timeline as a live recording. Label it as an execution record.
- Normal authorization rules still apply to login, payment, submission, deletion, communication, or other side effects.
- Use the user's language for the test plan, report content, and final response.

## Workflow

### 1. Design the experiment

Create a compact experiment plan containing:

```text
Candidate:
Baseline:
Shared task:
Input and expected output:
Primary metric:
Required metrics: result quality, end-to-end elapsed time
Optional metrics: tokens, cost
Invocation evidence expected from each arm:
Known limitations:
Stopping rule:
```

Default to one run per arm. This is an MVP value check, not a statistical benchmark.

If a fair A/B comparison is impossible, explain why and revise the task or baseline before requesting approval. Do not manufacture a comparator.

### 2. Obtain human approval

Show the complete experiment plan before executing either arm.

Do not begin the baseline or candidate run until the user explicitly approves the plan with language such as “approved,” “run it,” or “use this design.”

If the user rejects or changes the plan:

1. incorporate the feedback;
2. show the revised complete plan;
3. request approval again;
4. never apply approval for an earlier version to the revised design.

Approval of the experiment design does not replace action-time authorization required for consequential operations.

### 3. Execute the baseline

Tell the user that the baseline run is starting.

Capture only information actually observed:

- method name and available version/configuration;
- start and end timestamps;
- end-to-end elapsed seconds;
- three to eight meaningful process steps;
- invocation evidence: tool call, command, log, task metadata, or raw output;
- final result summary;
- optional screenshot or evidence file;
- tokens and cost only when the host reports them.

### 4. Execute the candidate

Tell the user that the candidate run is starting. Capture the same fields as the baseline.

The evidence must identify the candidate by its real tool, model, Skill, command, or integration name. If no system evidence connects the candidate to the execution, mark the invocation as unverified.

### 5. Compare the arms

Evaluate these metrics:

| Metric | Requirement |
|---|---|
| Result quality | Required. Prefer an objective reference or explicit task requirements. If judgment is subjective, label it as AI-assessed and explain the basis. |
| End-to-end elapsed time | Required. Measure the complete task, not only a fast internal tool call. |
| Tokens | Optional. Compare only when both values are reported by the host. |
| Cost | Optional. Compare only when both values are reported in compatible units. |

Check result quality before efficiency. A faster failed result is not an improvement.

Calculate differences and percentages only when units match, values are present, and the denominator is greater than zero.

### 6. Write the recommendation

Use exactly one verdict:

- **Adopt** — the candidate meets the task requirements and clearly improves the primary value metric.
- **Conditional adoption** — the candidate is valuable only in stated situations, repeated workflows, or above a clear break-even point.
- **Do not adopt yet** — the baseline is more suitable for this representative task.
- **Inconclusive** — invocation, result quality, or a decision-critical metric lacks sufficient evidence.

Explain:

- the candidate's concrete benefit;
- its tradeoff or lost capability;
- when to use it;
- when to keep the baseline;
- what this one experiment did not establish.

### 7. Build the report data

Create an output directory inside the current task workspace. Write the observed experiment data to `experiment.json`, following the structure in `tests/sample-experiment.json` next to this Skill.

Do not include secrets, cookies, authorization headers, private tokens, or unrelated user data. Redact sensitive values before writing evidence.

Use `null` for unavailable token and cost values. Keep raw evidence concise; include only the portion needed to verify execution.

### 8. Render the standalone HTML

Run:

```bash
python3 <skill-directory>/scripts/render_report.py <output-directory>/experiment.json --output <output-directory>/report.html
```

The renderer uses only the Python standard library and creates a self-contained HTML file without external CDNs, fonts, or scripts.

The HTML must present, in this order:

1. experiment title, shared task, verdict, and one-line conclusion;
2. core metric cards for quality, time, tokens, and cost;
3. side-by-side baseline and candidate process timelines;
4. result summaries and value differences;
5. benefits, tradeoffs, use cases, limitations, and adoption recommendation;
6. **as the final section: Execution logs and invocation evidence**.

The final evidence section must contain separate baseline and candidate columns with:

- invocation status: “Verified” or “Unverified”;
- actual capability name and available version/configuration;
- chronological execution steps;
- commands, code, tool-call information, logs, task metadata, and raw output excerpts that were actually observed;
- errors and retries when they occurred;
- optional screenshots or evidence files.

Long logs must be collapsed by default and expandable by the user. Never write assistant-authored prose in a way that imitates a system log.

### 9. Verify the artifact

Open or render `report.html` and check:

- it loads without network access;
- the baseline and candidate are not swapped;
- units are consistent;
- missing metrics display “Not available,” not zero;
- the verdict matches the observed data and written analysis;
- the invocation evidence is visible in the final section;
- no secrets or private identifiers appear in the page.

Fix any defect before delivery.

### 10. Deliver

The final response should contain only what the user needs to act:

1. a clickable link to `report.html`;
2. the one-sentence adoption recommendation;
3. the most important limitation of the experiment.

## Incomplete experiments

Never fabricate a complete experiment when:

- one arm cannot run;
- the methods cannot complete the same task;
- no evidence proves that the candidate ran;
- a critical result cannot be read;
- execution requires authorization the user has not provided.

Preserve the completed evidence, generate a report when useful, label the experiment incomplete, and use the verdict **Inconclusive**.

## Completion criteria

The task is complete only when:

- the user approved the exact experiment design that was executed;
- both arms ran, or the report records why an arm could not run;
- invocation evidence is present or explicitly marked missing;
- result quality and elapsed time are compared;
- the HTML is generated and visually verified;
- its final section contains the execution logs and invocation evidence;
- the report includes analysis, a verdict, and the experiment's main limitation.
