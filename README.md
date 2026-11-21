# Capability Value Test

**English** | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [العربية](README.ar.md)

> Make the use of a new capability visible, and make the value it creates measurable.

Capability Value Test is an agent-agnostic Skill for verifying whether a newly integrated capability (such as a Skill, model, plugin, MCP server, browser, open-source component, or agent workflow) was actually invoked and whether it creates measurable value compared with the previous method.

It designs a fair A/B test between the previous method and the method enabled by the new capability. By default, the experiment uses three representative task samples drawn from the user's recurring work, common scenarios, or examples supplied by the user. A human reviews the complete design before either method runs. After execution, it produces a standalone, visual, traceable HTML report.

## Why it exists

After integrating a new capability, people often cannot answer:

1. **Was it actually invoked, and where is the evidence?**
2. **Did it create value, and can that value be quantified?**
3. **Can its use process and concrete value be understood visually?**

The problem is not only whether an integration works. Its process is often invisible and its value cannot be measured against the previous way of working.

## How it works

1. Define the new capability and the methods before and after integration.
2. Select three representative task samples from the user's recurring work, prior conversation context, or directly supplied examples.
3. In every round, give both methods the same input, output requirements, stopping rule, and evaluation criteria.
4. Define how correctness, completeness, and end-to-end time will be judged.
5. Present the complete three-round design for human review; revise it when rejected.
6. Run both methods in all three rounds only after explicit approval.
7. Record each round's process, outputs, elapsed time, available metrics, and invocation evidence.
8. Separate experiment observations from cited public information, then synthesize concrete usage scenarios and a recommendation.
9. Render the result as a standalone HTML report in the user's conversation language by default, with a top-right language dropdown.

The goal is not to make the new capability win. It is to establish what changed and whether the evidence supports adoption.

## What the HTML report shows

### Decision summary

The unnumbered report header shows:

- the original and new methods;
- the verdict: adopt, do not adopt, or inconclusive;
- the main reason for the verdict;
- what the experiment tested;
- the value question;
- the test date.

### 1. Core comparison and experiment analysis

This section shows aggregate three-round metrics, a compact result table for each round, experiment observations, cited external findings, benefits, tradeoffs, suitable and unsuitable scenarios, usage guidance, and remaining uncertainty.

Every metric card identifies the original and new methods and explains the difference in plain language. Metrics unavailable from the host are displayed as “Not available,” never as zero.

### 2. Experiment design and evidence

This section explains why the three samples were selected, how the comparison was kept fair, and how correctness and completeness were judged.

Each round can be expanded into side-by-side execution timelines for the original and new methods. Timelines start at `00:00` and show only meaningful recorded events. Model calls, tool calls, commands, inputs, outputs, errors, and retries are attached to the step where they occurred and can be expanded on demand.

The timeline is an execution record, not a live recording. Unrecorded events are shown as unavailable rather than reconstructed as fact.

The report initially uses the user's conversation language. A language button in the top-right opens a dropdown for switching the narrative offline. Raw commands, logs, errors, and tool output stay in their original form so the evidence remains auditable.

## Human approval is required

```text
Previous method + method enabled by the new capability
                         ↓
          Select three representative samples
                         ↓
              Three-round experiment design
                         ↓
        Human review ── rejected → revise and review again
                         ↓ approved
              Run both methods in three rounds
                         ↓
       Results + invocation evidence + research
                         ↓
             Visual HTML report + verdict
```

Approval applies only to the exact design shown. Consequential actions such as login, payment, submission, communication, or deletion still require their own authorization.

## Fair-test principles

In each round, both methods should receive the same task sample, inputs, constraints, timing scope, quality criteria, and evidence level.

The experiment should not repeat the same input three times merely to increase the count. The samples should represent work the user actually performs. If recurring tasks are unknown, ask for examples or label proposed tasks as assumptions. Any unavoidable difference and its possible effect must be disclosed in the report.

## Example uses

- Compare Chrome and Lightpanda on the same web task.
- Compare two models on quality, time, and token usage.
- Determine whether a new Skill reduces steps and elapsed time.
- Compare an MCP server with an existing API or manual workflow.

## Install

Install to supported agents with the Skills CLI:

```bash
npx -y skills add EthanZhu-07/capability-value-test -g --all
```

Or clone the repository and follow your agent's Skill-directory convention:

```bash
git clone https://github.com/EthanZhu-07/capability-value-test.git
```

## Use

```text
Use Capability Value Test to compare my existing browser method with the method enabled by Lightpanda. Show me the test design before running it.
```

The agent must return the design first and wait for human approval.

## Render a report manually

The renderer uses only the Python standard library:

```bash
python3 scripts/render_report.py tests/sample-experiment.json --output report.html
```

The result is a self-contained HTML file that opens offline in a modern browser. The fixtures are demonstration data, not claims about real products.

The HTML layout is a versioned, fixed report format. Every report keeps the same section order and includes a short explanation below each major heading so readers know what the section means and how to interpret its evidence. Experiment-specific content changes through `experiment.json`; individual runs do not create custom layouts.

## Limits and privacy

- Three representative rounds reduce single-run luck but still provide task-scoped directional evidence, not a statistical guarantee.
- Samples should come from the user's recurring work, common scenarios, or directly supplied examples.
- Both methods must receive the same input and evaluation rules in each round.
- Tokens and cost can be compared only when the host exposes them.
- If invocation cannot be verified, the verdict must be **Inconclusive**.
- Headless execution is shown as a timestamped execution record with expandable evidence, never misrepresented as a live screen recording.
- Three rounds cannot prove that the capability is better for every task.
- Secrets, cookies, authorization headers, private tokens, and unrelated personal data must not enter the report.

## Repository structure

```text
.
├── SKILL.md                       # Agent-agnostic instructions and workflow
├── agents/openai.yaml             # Optional host UI metadata
├── assets/report-template.html    # Offline visual report template
├── scripts/render_report.py       # JSON validator and HTML renderer
└── tests/                         # Valid and invalid demonstration fixtures
```

## Development

```bash
python3 -m py_compile scripts/render_report.py
python3 scripts/render_report.py tests/sample-experiment.json --output /tmp/capability-value-report.html
python3 scripts/render_report.py tests/invalid-experiment.json --output /tmp/invalid.html
```

The last command should fail with exit code `2`. GitHub Actions runs the core checks on pushes and pull requests.

## License

Released under the [MIT License](LICENSE).
