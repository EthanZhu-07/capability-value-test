# 新能力价值测试（Capability Value Test）

[English](README.md) | [简体中文](README.zh-CN.md)

让新接入的 AI 能力所带来的价值，变得可见、可比较、可验证。

Capability Value Test 是一个轻量的 Codex Skill，用于把新接入的 Skill、模型、插件、MCP Server、浏览器、开源工具或工作流，与用户原本使用的方法进行对照。它会先设计公平的 A/B 实验，等待人类确认，再分别执行两种方法，最后交付一个独立 HTML 报告，展示过程、证据、指标、分析和采用建议。

## 为什么需要它

AI 越来越多地调用人类看不见的工具。接入一个新能力后，人往往无法回答三个基本问题：

1. **它真的被调用了吗？** AI 说“我用了”并不等于证据。
2. **它真的带来价值了吗？** 只看到成功结果，并不知道沿用原方法会怎样。
3. **证据在哪里？** 运行过程不可见时，效率提升、Token 减少和质量改善都很难被直观感知。

这个 Skill 会把上述问题转化为一个小型、可审查的实验。目标不是让新能力赢，而是得到可信的采用依据；负面结果或无法下结论，也同样有价值。

## 它能做什么

- 让候选能力与用户真实的原方法完成同一项任务。
- 先展示完整实验方案，获得人类明确批准后才执行。
- 人类不认可或修改方案时，迭代方案并重新请求确认。
- 在确实可获得时，记录真实调用证据、命令、工具调用、日志、时间戳、错误和重试。
- 必须比较结果质量和端到端总耗时。
- 只有宿主真实提供时，才比较 Token 和成本。
- 生成无需联网即可打开的单文件 HTML 报告。
- 在报告最底部，分别展示原方法与新能力的执行日志和调用证据。
- 给出四种结论之一：**采用**、**有条件采用**、**暂不采用**或**证据不足**。

## 人类审批是硬门槛

```text
新能力 + 原方法
      ↓
   设计实验
      ↓
人类审阅/批准 ── 不通过 → 修改后重新审阅
      ↓ 通过
执行原方法 + 执行新能力
      ↓
可视化 HTML 报告 + 采用建议
```

批准只对当次展示的确切实验方案有效。登录、付费、提交、发消息、删除等有后果的动作，仍需遵守各自的授权规则。

## HTML 报告包含什么

1. 结论与一句话摘要。
2. 质量、耗时、Token、成本指标卡。
3. 原方法与新能力的并列执行时间线。
4. 结果与价值对比。
5. 收益、代价、适用场景、不适用场景和采用建议。
6. **最底部：执行日志与调用证据**，原方法和新能力分别呈现。

拿不到的指标会显示“不可用”，不会伪装成零。无头工具的过程会被明确标为执行记录，不会冒充实时录屏。

## 安装

使用 Skills CLI：

```bash
npx -y skills add EthanZhu-07/capability-value-test -g --all
```

或手动克隆：

```bash
git clone https://github.com/EthanZhu-07/capability-value-test.git ~/.codex/skills/capability-value-test
```

如果没有立刻出现，可重启 Agent 宿主。

## 使用方式

显式调用：

```text
使用 $capability-value-test，对比 Lightpanda 和我现在的浏览器工作流。
```

也可以自然描述：

```text
我接入了一个新模型，帮我设计一个 A/B 实验，让我看出它是否提升质量或节省时间。
```

Skill 会先返回实验方案。只有你批准这份确切方案之后，才会开始执行。

## 手动生成报告

渲染器只依赖 Python 标准库：

```bash
python3 scripts/render_report.py tests/sample-experiment.json --output report.html
```

用现代浏览器打开 `report.html` 即可。示例文件只是演示数据，不代表对任何真实产品的测试结论。

## 证据与隐私

报告可以包含简短的命令输出、工具调用元数据、日志和真实截图，但前提是它们确实存在。不得伪造证据，也不得写入密钥、Cookie、认证头、私有 Token 或与实验无关的个人数据。证据文件必须位于实验目录内；不超过 5 MB 的图片可以嵌入单文件报告。

## 局限

- 每组一次运行只能提供方向性证据，不能代替统计结论。
- 公平对照要求两种方法能完成同一项有代表性的任务。
- Token 和成本是否可用，取决于宿主是否提供。
- 如果无法验证新能力确实被调用，结论必须是“证据不足”。
- 无头工具不一定能展示实时可视化界面，报告会改为展示真实事件与输出记录。

## 项目结构

```text
.
├── SKILL.md                       # Agent 指令与工作流
├── agents/openai.yaml             # Codex 界面元数据
├── assets/report-template.html    # 离线可视化报告模板
├── scripts/render_report.py       # JSON 校验与 HTML 渲染器
├── tests/sample-experiment.json   # 正确的演示样例
└── tests/invalid-experiment.json  # 校验失败样例
```

## 开发与验证

```bash
python3 -m py_compile scripts/render_report.py
python3 scripts/render_report.py tests/sample-experiment.json --output /tmp/capability-value-report.html
python3 scripts/render_report.py tests/invalid-experiment.json --output /tmp/invalid.html
```

最后一条命令应该以退出码 `2` 失败。每次推送和 Pull Request，GitHub Actions 都会运行同样的核心校验。

## 许可证

目前项目未包含许可证文件。仓库公开不代表自动授予复制、修改或再分发权限。
