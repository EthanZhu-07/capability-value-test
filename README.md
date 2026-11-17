# Capability Value Test

[English](README.md) | [简体中文](README.zh-CN.md)

Make the value of a newly added AI capability visible, comparable, and auditable.

Capability Value Test is a lightweight Codex Skill for evaluating a new Skill, model, plugin, MCP server, browser, open-source tool, or workflow against the method you already use. It designs a fair A/B experiment, waits for human approval, executes both arms, and delivers a standalone HTML report with the process, evidence, metrics, analysis, and adoption recommendation.

## Why this exists

AI systems increasingly use tools that operate out of sight. After adding one, a human often cannot answer three basic questions:

1. **Was the new capability actually used?** An assistant saying “I used it” is not proof.
2. **Did it create value?** A successful result does not reveal how the old method would have performed.
3. **Where is the evidence?** Hidden execution makes time savings, token reduction, and quality improvements hard to inspect.

This Skill turns those questions into a small, reviewable experiment. The goal is not to make the new capability win; a negative or inconclusive result is useful evidence too.

## What it does

- Compares the candidate capability with the user's real current method on the same task.
- Shows the complete experiment design and waits for explicit human approval before running anything.
- Revises the design and asks again when the human rejects or changes it.
- Captures real invocation evidence, commands, tool calls, logs, timestamps, errors, and retries when available.
- Compares required metrics: result quality and end-to-end elapsed time.
- Compares tokens and cost only when the host actually reports them.
- Generates a self-contained HTML report that works offline.
- Ends with a separate audit section for baseline and candidate execution evidence.
- Produces one of four verdicts: **Adopt**, **Conditional adoption**, **Do not adopt yet**, or **Inconclusive**.

## Human approval is a hard gate

```text
New capability + current method
             ↓
      Experiment design
             ↓
      Human review/approval ── rejected → revise and review again
             ↓ approved
    Baseline run + candidate run
             ↓
  Visual HTML report + recommendation
```

Approval applies only to the exact design shown. It does not replace permissions required for consequential actions such as login, payment, submission, communication, or deletion.

## What the report contains

1. Verdict and one-line conclusion.
2. Quality, elapsed time, token, and cost cards.
3. Side-by-side execution timelines.
4. Result and value comparison.
5. Benefits, tradeoffs, suitable cases, unsuitable cases, and adoption recommendation.
6. **Final section: execution logs and invocation evidence**, separated by baseline and candidate.

Unavailable metrics are shown as “Not available,” never as zero. Headless execution is presented as a recorded timeline, never misrepresented as a live screen recording.

## Install

With the Skills CLI:

```bash
npx -y skills add EthanZhu-07/capability-value-test -g --all
```

Or clone it manually:

```bash
git clone https://github.com/EthanZhu-07/capability-value-test.git ~/.codex/skills/capability-value-test
```

Restart your agent host if the Skill does not appear immediately.

## Use

Invoke it explicitly:

```text
Use $capability-value-test to compare Lightpanda with my current browser workflow.
```

Or ask naturally:

```text
I added a new model. Design an A/B test so I can see whether it improves quality or saves time.
```

The Skill first returns an experiment plan. Execution begins only after you approve that exact plan.

## Render a report manually

The renderer uses only the Python standard library:

```bash
python3 scripts/render_report.py tests/sample-experiment.json --output report.html
```

Open `report.html` in any modern browser. The sample is demonstration data, not a claim about a real product.

## Evidence and privacy

The report may include concise command output, tool-call metadata, logs, and screenshots when they are actually available. It must never invent evidence or include secrets, cookies, authorization headers, private tokens, or unrelated user data. Evidence file paths must stay inside the experiment directory; images up to 5 MB can be embedded into the standalone report.

## Limits

- One run per arm provides directional evidence, not a statistical guarantee.
- A fair comparison requires both methods to complete the same representative task.
- Tokens and cost may be unavailable depending on the host.
- If candidate invocation cannot be verified, the verdict must be **Inconclusive**.
- Browser-visible animation is not always possible for headless tools; their actual events and outputs are shown as an execution record instead.

## Repository structure

```text
.
├── SKILL.md                       # Agent instructions and workflow
├── agents/openai.yaml             # Codex interface metadata
├── assets/report-template.html    # Offline visual report template
├── scripts/render_report.py       # JSON validator and HTML renderer
├── tests/sample-experiment.json   # Valid demonstration fixture
└── tests/invalid-experiment.json  # Validation failure fixture
```

## Development

```bash
python3 -m py_compile scripts/render_report.py
python3 scripts/render_report.py tests/sample-experiment.json --output /tmp/capability-value-report.html
python3 scripts/render_report.py tests/invalid-experiment.json --output /tmp/invalid.html
```

The last command should fail with exit code `2`. GitHub Actions runs the same core checks on every push and pull request.

## License

No license file is currently included. Public repository visibility does not itself grant permission to copy, modify, or redistribute the code.
