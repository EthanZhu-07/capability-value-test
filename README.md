# Capability Value Test

A Codex skill for making the value of a newly added tool, integration, model, skill, or workflow perceptible and auditable.

新接入一个 AI 能力后，单凭“成功得到结果”通常无法判断它是否真的有价值。这个 Skill 会围绕三个问题设计验收：

1. **缺少反事实基线：** 如果继续使用原来的方法，结果会怎样？
2. **过程不可见：** 人类能实时看到什么，或者事后核验什么？
3. **调用来源不可信：** 有什么证据证明候选能力真的被调用了？

## What it does

- Selects a realistic baseline instead of a weak strawman.
- Chooses A/B, ablation, before/after, shadow/canary, or threshold testing according to the decision.
- Separates first-time exploration, cold start, optimized replay, and scaled batch performance.
- Collects provenance, process, outcome, efficiency, reliability, and reproducibility evidence.
- Grades provenance from unsupported assistant assertion (`P0`) to independently reproducible proof (`P3`).
- Grades observability from final-result-only (`O0`) to a genuinely live visible process (`O3`).
- Returns an `adopt`, `conditional`, `reject`, or `inconclusive` verdict.
- States where the new capability wins, loses, and reaches its break-even point.

The goal is not to make the new capability win. A negative or inconclusive result is valid evidence.

## Install

```bash
git clone https://github.com/ETHAN-7TB/capability-value-test.git ~/.codex/skills/capability-value-test
```

Restart Codex after installation if the skill does not appear immediately.

## Use

Invoke it explicitly:

```text
Use $capability-value-test to design and run a perceptible, auditable value test for this new capability.
```

It may also be selected automatically when the user asks whether a newly added capability is worth adopting, requests a fair comparison with the current method, or needs proof that the capability was actually used.

## Files

- `SKILL.md` — decision framework and testing workflow.
- `agents/openai.yaml` — Codex interface metadata.
- `references/test-card.md` — pre-registered test contract, evidence ledger, proof grades, and result template.
