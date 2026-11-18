# Capability Value Test

**English** | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [العربية](README.ar.md)

> Make the use of a new capability visible, and make the value it creates measurable.

Capability Value Test is an agent-agnostic Skill for verifying whether a newly integrated capability (such as a Skill, model, plugin, MCP server, browser, open-source component, or agent workflow) was actually invoked and whether it creates measurable value compared with the previous method.

It designs a fair A/B test between the previous method and the method enabled by the new capability. A human reviews the complete design before either arm runs. After execution, it produces a standalone, visual, traceable HTML report.

## Why it exists

After integrating a new capability, people often cannot answer:

1. **Was it actually invoked, and where is the evidence?**
2. **Did it create value, and can that value be quantified?**
3. **Can its use process and concrete value be understood visually?**

The problem is not only whether an integration works. Its process is often invisible and its value cannot be measured against the previous way of working.

## How it works

1. Define the new capability and the methods before and after integration.
2. Choose one real task both methods can complete.
3. Keep inputs, environment, constraints, timing scope, and evaluation criteria aligned.
4. Present the complete A/B test design for human review; revise it when rejected.
5. Run both arms only after explicit approval.
6. Record the process, outputs, metrics, and invocation evidence for both arms.
7. Analyze the differences and render a standalone HTML report.

The goal is not to make the new capability win. It is to establish what changed and whether the evidence supports adoption.

## What the HTML report shows

### 1. Final recommendation

The report uses exactly one verdict:

- **Adopt**
- **Do not adopt**
- **Inconclusive — more evidence is required**

It explains the basis, strengths, problems, suitable and unsuitable scenarios, and experimental limits.

### 2. Value and benefits

The report can compare result quality, end-to-end elapsed time, token usage, cost, steps, errors, and retries. It interprets the differences instead of showing raw numbers alone. Metrics unavailable from the host are displayed as “Not available,” never as zero.

### 3. Proof of invocation

The final section keeps separate evidence for both arms, such as commands, tool or API calls, key inputs and outputs, logs, timestamps, task IDs, status values, errors, and retries. Evidence must be real and secrets must be redacted.

## Human approval is required

```text
Previous method + method enabled by the new capability
                         ↓
                  Experiment design
                         ↓
        Human review ── rejected → revise and review again
                         ↓ approved
                     Run both arms
                         ↓
             Visual HTML report + verdict
```

Approval applies only to the exact design shown. Consequential actions such as login, payment, submission, communication, or deletion still require their own authorization.

## Fair-test principles

Both arms should use the same task, inputs, constraints, timing scope, quality criteria, and evidence level. Any unavoidable difference and its possible effect must be disclosed in the report.

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

## Limits and privacy

- One run per arm is directional evidence, not a statistical guarantee.
- Both methods must be able to complete the same representative task.
- Tokens and cost can be compared only when the host exposes them.
- If invocation cannot be verified, the verdict must be **Inconclusive**.
- Headless execution is shown as an execution record, never misrepresented as a live screen recording.
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

No license file is currently included. Public visibility does not itself grant permission to copy, modify, or redistribute the project.
