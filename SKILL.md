---
name: capability-value-test
description: Design and run a visual A/B test between an existing method and the method enabled by a newly integrated capability. Use when a user wants proof that a Skill, model, plugin, MCP server, browser, open-source component, or agent workflow was invoked and wants to quantify its value. Requires human approval before execution and delivers a traceable HTML report.
---

# Capability Value Test

Turn “Is this new capability actually valuable?” into a small experiment the user can inspect rather than a claim they must trust.

Deliver a standalone HTML report that shows:

- whether the candidate capability was verifiably invoked;
- how the current method and candidate performed the same real task;
- how their result quality and end-to-end time compare;
- token usage and cost when the host actually exposes them;
- where the candidate is useful, where it is not, and whether to adopt it.
- experiment findings, external research, and the final synthesis as distinct evidence layers;
- the user's conversation language by default, with an offline language switcher in the top-right corner.

One run provides directional evidence only. Never present it as universal proof.

## Use this Skill when

- a user has added a new Skill, model, plugin, MCP server, browser, open-source tool, or workflow;
- the capability operates partly or entirely out of sight;
- the user wants to compare it with their existing method;
- the user asks whether it saves time, tokens, money, or improves the result;
- the user wants an HTML artifact that visualizes the process and conclusion.

Do not use it for ordinary “does this function work?” checks, formal statistical experiments, or comparisons where the two methods cannot perform the same task.

## Minimum inputs

Determine six things:

1. **Candidate** — the newly added capability.
2. **Baseline** — the user's real current method.
3. **Representative task** — one real task both methods can complete.
4. **Primary value question** — usually quality, elapsed time, tokens, or cost.
5. **Audience context** — the user's domain knowledge and what would make the task immediately understandable.
6. **Report language** — the user's primary conversation language plus useful alternate report languages.

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
- Prefer a representative task the user can understand without learning unrelated jargon. Technical sophistication is not evidence quality.
- Keep raw commands, logs, error messages, and tool output in their original language. Translate their labels and explanations, never the evidence itself.
- External research may add context but must never overwrite, excuse, or contradict an observed experiment result without saying so explicitly.

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
Audience and comprehension check:
Default report language and alternate languages:
Known limitations:
Stopping rule:
```

Default to one run per arm. This is an MVP value check, not a statistical benchmark.

Before requesting approval, apply a comprehension gate:

- explain the shared task in one plain-language sentence;
- remove domain jargon that is unrelated to the value question;
- prefer outcomes the user can independently recognize as correct;
- if the task assumes specialist knowledge the user has not shown, replace it with a simpler representative task.

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

### 6. Research missing decision context

First write down what the experiment directly established. Then check whether the experiment alone supports concrete benefits, tradeoffs, and usage scenarios.

When it does not, search the public web for current context. Prefer official documentation, the official repository, product documentation, and primary sources; add reputable independent sources only when they materially improve the decision. Record the source title, publisher, direct URL, retrieval date, and the specific finding supported by that source.

Keep three layers separate:

1. **Experiment findings** — observed in the approved A/B test.
2. **External research** — supported by cited public sources.
3. **Synthesis** — the recommendation produced from both layers.

Describe scenarios concretely. Each scenario must identify who is doing what task, in what environment, why the capability fits or does not fit, the evidence basis, and confidence. Avoid labels such as “good for static pages” without a real example.

If browsing is unavailable or reliable sources cannot be found, say so in the report instead of inventing context.

### 7. Write the recommendation

Use exactly one verdict:

- **Adopt** — the candidate meets the task requirements and clearly improves the primary value metric.
- **Do not adopt** — the baseline is more suitable for this representative task.
- **Inconclusive** — invocation, result quality, or a decision-critical metric lacks sufficient evidence.

Explain:

- the candidate's concrete benefit;
- its tradeoff or lost capability;
- its suitable and unsuitable scenarios;
- what this one experiment did not establish.

### 8. Build the report data

Create an output directory inside the current task workspace. Write the observed experiment data to `experiment.json`, following the structure in `tests/sample-experiment.json` next to this Skill.

The `analysis` object must contain:

- non-empty `experiment_findings`;
- `research.status`, `research.summary`, and cited `research.sources` when research completed;
- concrete `scenarios` with audience, task, environment, recommendation, reason, evidence basis, confidence, and source references;
- benefits, tradeoffs, and the final recommendation.

Set `i18n.default_locale` from the user's primary conversation language. Include at least that locale plus useful alternates in `i18n.locales`; when the user has not specified alternatives, prefer English, Simplified Chinese, Japanese, and Korean where practical. Each non-default locale contains translated narrative content. Raw evidence content remains untranslated.

Do not include secrets, cookies, authorization headers, private tokens, or unrelated user data. Redact sensitive values before writing evidence.

Use `null` for unavailable token and cost values. Keep raw evidence concise; include only the portion needed to verify execution.

### 9. Render the standalone HTML

Run:

```bash
python3 <skill-directory>/scripts/render_report.py <output-directory>/experiment.json --output <output-directory>/report.html
```

The renderer uses only the Python standard library and creates a self-contained HTML file without external CDNs, fonts, or scripts.

#### Fixed report format

Use `assets/report-template.html` as the fixed report format. Do not create a new layout for an individual experiment, remove sections, or reorder the sections. Experiment-specific differences belong in `experiment.json`, not in a custom HTML structure. Change the format only when intentionally revising this Skill and update the renderer contract and tests at the same time.

Every major section must keep its short reader-facing explanation directly below the heading. These explanations are part of the format, not optional experiment content:

- **Core comparison** — explain that unavailable measurements remain unavailable and are not treated as zero.
- **Process comparison** — explain that the timeline is an execution record and not a live recording.
- **Experiment findings** — explain that this section contains only observations from the approved A/B test.
- **External research** — explain that public sources add context the experiment alone could not establish.
- **Analysis and recommendation** — explain that the synthesis uses both evidence layers while preserving their differences.
- **Execution logs and invocation evidence** — explain that the final section contains the observable evidence used to verify both methods actually ran.

The renderer enforces this structure and must fail rather than silently generate a report when a required section, explanation field, format marker, or section order is missing.

The HTML must present, in this order:

1. experiment title, shared task, verdict, and one-line conclusion;
2. core metric cards for quality, time, tokens, and cost;
3. side-by-side baseline and candidate process timelines;
4. result summaries and value differences;
5. experiment findings;
6. external research with direct source links and retrieval dates;
7. benefits, tradeoffs, concrete scenarios, limitations, and adoption recommendation;
8. **as the final section: Execution logs and invocation evidence**.

The report must initially show only the default language. Put the current language control in the top-right corner; clicking it opens a dropdown list. Changing the selection updates the complete report without network access. Do not display bilingual headings side by side.

The final evidence section must contain separate baseline and candidate columns with:

- invocation status: “Verified” or “Unverified”;
- actual capability name and available version/configuration;
- chronological execution steps;
- commands, code, tool-call information, logs, task metadata, and raw output excerpts that were actually observed;
- errors and retries when they occurred;
- optional screenshots or evidence files.

Long logs must be collapsed by default and expandable by the user. Never write assistant-authored prose in a way that imitates a system log.

### 10. Verify the artifact

Open or render `report.html` and check:

- it loads without network access;
- the baseline and candidate are not swapped;
- units are consistent;
- missing metrics display “Not available,” not zero;
- the verdict matches the observed data and written analysis;
- the invocation evidence is visible in the final section;
- no secrets or private identifiers appear in the page.
- the default language matches the user's conversation language;
- the top-right dropdown opens, closes, marks the active language, and switches all translated narrative content;
- the report declares the fixed format version and retains every required section explanation;
- raw evidence stays unchanged when the report language changes;
- experiment findings, external research, and synthesis are visibly distinct;
- scenarios are concrete rather than generic labels.

Fix any defect before delivery.

### 11. Deliver

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
