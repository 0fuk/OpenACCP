# OpenACP

OpenACP, short for **Open Agent Coordination Protocol**, is a workflow kit for coordinating multiple AI agents around real project work.

It is not an agent runtime, model framework, IDE plugin, or prompt pack. OpenACP does not try to replace Codex, Claude Code, Aider, OpenHands, SWE-agent, LangGraph, CrewAI, AutoGen, or the OpenAI Agents SDK. Those tools help agents run, code, call tools, or build graphs. OpenACP focuses on the part that usually gets messy after agents start moving fast:

- 哪些材料是当前事实，哪些只是参考，哪些已经过期。
- 谁可以只读分析，谁可以准备任务包，谁可以真正修改文件。
- worker 做完以后，它的结果到底证明了什么。
- reviewer 的建议是不是 final acceptance。
- 多个 thread、worktree、handoff、review report 之间如何接上。
- human owner 什么时候必须做最终决定，什么时候 agent 其实可以继续推进。

一句话：**AI agents can do work; OpenACP keeps the work coordinated, reviewable, and recoverable.**

中文说人话：agent 已经会写代码、查资料、做 review。OpenACP 管的是这些 agent 之间的事实、权限、交接、验收和恢复，不让多 agent 项目变成一堆聊天记录和半截结论。

## Who This Is For

OpenACP 适合已经开始把 AI agent 当“协作团队”使用的人，而不是只想让单个 agent 回答一个问题的人。

| 你是谁 | 你可能遇到的问题 | OpenACP 帮你做什么 |
|---|---|---|
| 同时开多个 agent 的独立开发者 | 一个 thread 查 spec，一个 thread 改代码，一个 thread 做 review，最后分不清谁的结论还能信。 | 把每个 thread 变成有角色、有 scope、有 handoff 的工作单元。 |
| 创业团队或工程负责人 | agent 执行很快，但 merge、release、客户影响、风险接受仍然需要清楚责任人。 | 把执行权限和最终验收权限分开。worker 可以做事，Primary/human 才能 final accept。 |
| 大型 repo 维护者 | 迁移、重构、测试、文档和发布准备并行推进，状态散落在 branch、PR、CI 和聊天里。 | 用 source pack、CARD、authority charter、handoff、review report 和 consume result 串起来。 |
| AI coding workflow 负责人 | 团队已经在用 Codex、Claude Code、Aider、OpenHands 等工具，但规则、handoff 和验收方式不统一。 | 给不同工具一套通用 coordination artifact，不绑定某一个 runtime。 |
| 复杂交付项目 owner | 后端、前端、测试、安全、文档、运营资料同时变动，agent 产出很多，真正能接受的结果需要筛选。 | 区分“agent 产出过”和“项目已经接受”，让证据、缺口和最终决定可追踪。 |
| 只有 PRD 或模糊想法的人 | 还没有 spec、source pack、scope boundary 或 task card，agent 容易直接猜需求。 | 用 bootstrap 把粗 PRD 先整理成事实包、范围边界、假设、开放问题和第一批任务卡。 |

OpenACP 不适合一问一答的小任务，也不替代测试、CI、代码审查、安全审查、法律审查或工程判断。它让这些东西更容易被 agent 和 human 一起看懂。

## Quick Start

在 Codex 或 Claude Code 里直接问：

```text
Install https://github.com/0fuk/OpenACP as a skill + workflow kit, then follow the README startup flow.
```

安装流程应该做三件事：

1. 安装 `skills/` 里的 OpenACP skills。
2. 安装 Python workflow kit，并跑基础验证。
3. 自动给你一份 formal report，说明安装是否完成、还缺什么输入。

安装和验证完成后，agent 会问你三个东西：

- **working directory**：必须提供。agent 需要知道项目工作应该发生在哪里。
- **source pack、PRD、spec、design doc、facts path 或上传材料**：这是项目事实来源。如果还没有整理好的 facts path，可以上传材料，agent 会先当作 candidate facts 组织。
- **preferred language**：后续 Primary、Frontier、worker、reviewer、discovery 的回复都应该保持同一种语言。

你提供这些后，startup agent 应该：

1. 在你的工作目录下写入完整 Primary prompt record。
2. 在同一位置写入短 launcher 文件。
3. 在当前聊天里给你一个可复制的短 Primary launcher，用 fenced `prompt` block 包起来。
4. 用自然语言告诉你：从左侧新建一个 thread，把这个短 launcher 粘贴进去启动。

完整 prompt body 应该落盘，不应该塞进聊天。聊天里只放短 launcher。只给 `.short.md` 文件链接、附件、文件列表或 `Get-Content` 命令都不够。

## What Happens After Startup

GitHub install startup **只启动一个 Primary**，不会默认给你两个 Frontier。原因很简单：还没看项目事实之前，没人知道你的项目需要 1 条 lane、2 条 lane，还是 4 条 lane。

Primary thread 启动后会先做这些事：

1. 读取你的 working directory 和事实材料。
2. 判断哪些 source 是 current、reference、deprecated 或 invalid。
3. 建立 source pack、scope boundary、current manifest、sequence registry。
4. 把工作拆成 CARDs。
5. 根据复杂度和风险决定需要几个 Frontier lane。通常 1-5 个，超过 5 个要你明确同意。
6. 为每个选中的 Frontier 写完整 prompt record 和短 launcher。
7. 在聊天里给你每个 Frontier 的可复制短 launcher，并告诉你分别开哪个新 thread。

Primary 不是“计划机器人”。它的工作是持续收口：能通过 B0/B1/B2 安全推进的事情，就继续派发、消费、复查、重分类；只有真正需要 final authority 的事情才交给 human 或 Primary 做 B3 决定。

## You Can Also Start Orchestrators Manually

OpenACP 不只支持 README install startup。安装好 skills 之后，你也可以手动创建新的 Primary 或 Frontier。

手动启动 Primary 的自然语言方式：

```prompt
Use primary-orchestrator-openacp to start OpenACP coordination for this project.

Working directory: <your project path>
Facts input: <source pack, PRD, spec, design doc, facts path, or uploaded materials>
Preferred language: <Chinese / English / your choice>

First review the workspace and facts, create or refresh source pack, scope boundary, current manifest, sequence registry, and CARDs. Then decide how many Frontier lanes are actually needed. Return human-readable status and only copyable short Frontier launchers for selected lanes.
```

手动启动 Frontier 的自然语言方式：

```prompt
Use frontier-orchestrator-openacp for this lane.

Lane objective: <what this lane should close>
Authority: B2 lane-local unless explicitly narrowed
Working directory: <project path>
Facts/source pack: <path or artifact>
Assigned CARDs: <CARD ids or task cards>
Preferred language: <same as Primary>

Continue B0/B1/B2 lane-local closure. Dispatch worker, reviewer, discovery, or validation subagents when safe. Do not return to the human unless the next action truly needs final authority or missing user facts.
```

如果你已经有完整 prompt record，推荐使用短 launcher：短 launcher 只告诉新 thread 去哪里读完整 prompt record、执行哪个 Prompt ID、用什么语言、按 UTF-8 读取、读不干净就停止。这样聊天窗口不会被长 prompt 淹没。

## How Orchestrators Communicate

OpenACP 不是靠“上一个聊天窗口记得什么”来协作。它靠项目里的 coordination artifacts。

典型通信链路是：

```text
Primary
  -> writes CARDs, authority charters, Frontier prompt records
  -> gives short Frontier launchers

Frontier
  -> reads assigned CARDs and source pack
  -> runs B0/B1/B2 lane-local closure
  -> dispatches worker/reviewer/discovery subagents when safe
  -> consumes child handoffs
  -> writes lane status, child ledger, Primary-ready packet

worker / reviewer / discovery
  -> returns handoff, review report, machine summary, or evidence summary

Primary
  -> consumes handoffs and reviewer evidence
  -> accepts, rejects, amends, splits follow-up, or asks for B3 human decision
```

这些 artifact 的意义：

| Artifact | 说人话解释 |
|---|---|
| `source pack` | 当前事实清单。告诉 agent 哪些材料能驱动实现，哪些只是参考。 |
| `scope boundary` | 范围边界。告诉 agent 什么可以做、什么不能碰。 |
| `assumptions ledger` | 假设账本。把没被证明但暂时采用的判断显式记录下来。 |
| `CARD` / `task card` | 可执行任务单。没有 scope、acceptance、verification、stop condition，就不该让 worker 猜着做。 |
| `authority charter` | 权限合同。说明谁能读、谁能写、能影响哪些文件、不能做哪些 side effects。 |
| `prompt record` | 完整任务指令，落盘保存，供新 thread 按 Prompt ID 读取。 |
| `short launcher` | 聊天里可复制的短启动器，指向完整 prompt record。 |
| `handoff` | worker/reviewer/discovery 的交接证据。它证明做了什么，也说明没证明什么。 |
| `consume result` | 上级 orchestrator 对 handoff 的消费结论。handoff 存在不等于已接受。 |
| `formal report` | 给人看的正式状态：做了什么、进度、缺口、下一步、依据。 |
| `machine summary` | 给 agent 或 validator 快速定位用的压缩摘要。 |

## Role Model

| Role | 它做什么 | 它不能做什么 |
|---|---|---|
| `Primary` | 项目主协调者。拆 CARD、分 lane、发 authority charter、消费 handoff、决定最终接受或拒绝。 | 不应把 worker/reviewer 的结论直接当 final acceptance。 |
| `Frontier` | 一条 lane 的 orchestrator。持续推进 B0/B1/B2：发现事实、准备包、派 worker/reviewer、消费 child handoff、形成 Primary-ready packet。 | 不是默认 implementation worker；不能做 B3 final merge/release/acceptance。 |
| `worker` | 在明确 scope 和 authority 下执行窄任务，产出 handoff 和验证证据。 | 不能扩 scope、不能自行变更 final authority、不能声称最终验收。 |
| `reviewer` | 只读检查 scope、正确性、验证证据、side effect 和 overclaim。 | 不能 merge、commit、waive 或 final accept。 |
| `discovery` | 只读查事实、分类 gap、准备下一步。 | 不能实现，也不能把 reference material 自动提升成 current fact。 |
| `human owner` | 决定产品意图、风险接受、最终发布和高风险例外。 | 不应该被迫处理 agent 自己能通过 B0/B1/B2 继续推进的小事。 |

## B0 / B1 / B2 / B3

这四个不是抽象术语，而是“这个 agent 现在到底能做多大动作”的权限门槛。

| Level | 人话解释 | 典型动作 |
|---|---|---|
| `B0` | 只读和整理。可以查事实、做 review、识别风险，但不改项目。 | source discovery、risk scan、review、backlog refresh、事实分类。 |
| `B1` | 准备执行。可以把 gap 变成 task card、worker package、verification matrix、handoff schema。 | 写任务包、列测试计划、准备 owner question、生成 dispatch-ready packet。 |
| `B2` | 有边界的执行。可以在 task card 和 authority charter 允许范围内派 worker 做 scoped implementation。 | worker dispatch、worktree setup、局部修改、验证、child handoff consume。 |
| `B3` | 最终权威。决定是否接受、merge、release、publish、waive 或对外声明完成。 | final acceptance、PR/CI/merge、release、publication、final waiver。 |

核心原则：**B3 卡住时，不代表 B0/B1/B2 都要停。** 如果还能查事实、收窄范围、准备任务包、派 scoped worker 或补 review，Frontier 和 Primary 应该继续推进，而不是把所有事情都丢回给 human。

## Skills

OpenACP 的 `skills/` 是可安装的 agent workflow instructions。它们不是装饰目录，每个 skill 都对应一个真实协作角色或治理动作。

| Skill | 什么时候用 | 它的价值 |
|---|---|---|
| `primary-orchestrator-openacp` | 启动或运行项目级 Primary。需要拆 lane、派 Frontier/worker/reviewer、消费 handoff、做最终判断时用。 | 保持主线收口，防止多个 agent 产出混在一起没人验收。 |
| `frontier-orchestrator-openacp` | 运行一条 bounded lane。需要 lane backlog、discovery、worker package、reviewer dispatch、child handoff consume 时用。 | 让 Frontier 持续在 B0/B1/B2 内推进，不动不动把小事交回 human。 |
| `worker-openacp` | 执行明确 task card 下的窄任务。 | 让实现工作有 scope、allowed effects、verification 和 handoff，而不是随意改。 |
| `reviewer-openacp` | 只读检查 task card、branch、diff、handoff、prompt 或 status artifact。 | 把“看起来可以”变成有依据的 approve/amend/reject/split-follow-up 建议。 |
| `discovery-openacp` | 事实、scope、source status、risk 或 next safe action 不清楚时。 | 先查清楚再动手，避免把猜测当事实。 |
| `source-pack-openacp` | 创建、审查或更新 source pack 和 manifest。 | 决定 current/reference/deprecated/invalid sources，防止旧文档污染当前实现。 |
| `bootstrap-openacp` | 只有粗 PRD、产品想法、issue list 或散乱笔记时。 | 先生成最小 source pack、scope boundary、assumptions、open questions、starter spec 和 task cards。 |
| `handoff-consume-openacp` | 准备接受、拒绝、修订、合并、发布或继续派发之前。 | 判断 handoff 到底证明了什么，不把“有产物”误认为“已完成”。 |
| `formal-report-openacp` | 需要给 human owner 和下游 agent 汇报状态时。 | 统一 Response ID、进度、缺口、依据和下一步，避免机器日志式回复。 |
| `human-explain-openacp` | 用户需要知道现在到底发生了什么、下一步该做什么时。 | 把 Prompt ID、lane、handoff、B0/B1/B2/B3 翻译成自然语言。 |
| `validator-openacp` | 发 prompt、消费 handoff、发布包、验证 report 或 launcher 前。 | 检查结构、编码、source status、authority boundary、overclaim、public package hygiene。 |

## Core Technology

OpenACP 的核心不是“更多 prompt”，而是几种可复用的协调技术。

### Source-Driven Coordination

工作必须从当前事实出发。一个 PRD、旧 spec、聊天记录、截图或 note 不会自动成为 current source。OpenACP 要求 agent 先说明材料状态：

- `current`: 可以驱动实现。
- `reference`: 可以提供背景，但不能扩大 scope。
- `deprecated`: 已被新材料替代。
- `invalid`: 读取错误、角色错配、污染、过期或不可信。

### Authority Boundary

OpenACP 显式记录 authority。worker 可以完成实现，reviewer 可以建议接受，Frontier 可以形成 lane 证据，但最终是否 merge/release/final accept 仍由 B3 owner 决定。

### Active Closure

Primary 和 Frontier 不应该只是报告“还缺什么”。它们应该持续问：

- 这个 gap 能不能 B0 查清楚？
- 能不能 B1 打包成任务？
- 能不能 B2 派 scoped worker 或 reviewer？
- 真的只剩 B3 final authority 吗？

只有所有可见 gap 都是 `needs_final_authority` 或 `explicitly_out`，Frontier 才应该把 lane 交回 Primary。

### Handoff Consume

handoff 是证据，不是终点。上级 orchestrator 必须 consume：

- scope 是否符合 task card。
- changed files 是否在 allowed files 内。
- verification 是否具体。
- skipped checks 是否有理由。
- reviewer 是否发现问题。
- 是否存在 overclaim。

### Human-Readable Status

OpenACP 反对把机器日志当用户回复。Primary、Frontier、worker、reviewer 都应该解释：

- 做了什么。
- 什么已经证明。
- 什么只是 provisional。
- 缺什么。
- 下一步谁应该做什么。

## Minimum Useful Setup

最小有用 OpenACP 工作包不需要很复杂：

```text
source pack
scope boundary
assumptions ledger
task card
authority charter
worker handoff
review report
consume result
formal report
```

如果你连这些都没有，从 `bootstrap-openacp` 开始。不要让 implementation worker 在没有 task card、acceptance、verification 和 stop condition 的情况下直接猜需求。

## Repository Map

```text
docs/        Concepts, role model, authority model, bootstrap, coordination, validator rules.
templates/   Reusable Markdown templates for source packs, specs, prompts, reports, handoffs.
schemas/     Minimal JSON Schemas for machine-checkable coordination artifacts.
tools/       Validator and helper CLI.
skills/      Portable agent skills for using OpenACP workflows.
examples/    Strict fixtures and concept examples.
```

## Examples

- `examples/single-worker-flow/`: 完整 strict-validation fixture。
- `examples/prd-only-bootstrap/`: 从粗 PRD 启动的 bootstrap fixture。
- `examples/primary-two-frontier-kickoff/`: Primary 在 CARD 和 lane analysis 后生成 Frontier launchers 的概念示例。
- `examples/primary-orchestrator-flow/`: final-authority dispatch 和 consume 的概念示例。
- `examples/frontier-lane-flow/`: lane authority 的概念示例。
- `examples/multi-worktree-review/`: 多 worker 和 reviewer sidecar 的概念示例。

前两个更适合直接跑验证。后面几个主要展示结构和词汇，不代表完整项目包。

## Local CLI

如果你只是想本地试一下：

```bash
git clone https://github.com/0fuk/OpenACP.git
cd OpenACP
python -m pip install -e .
openacp --version
openacp-validate --version
```

如果你只有粗 PRD 或散乱材料，可以创建 starter package：

```bash
openacp init ./my-openacp-package
openacp init ./my-openacp-package --write
```

`openacp init` 默认 dry run。它是 bootstrap fallback，不是正常 startup flow。正常使用时，推荐先安装 skills，然后让 Primary 根据真实 working directory 和 facts input 创建项目专属 prompt records 和 launchers。

## Positioning

Claude Workflow、SuperClaude、Aider、OpenHands、SWE-agent、LangGraph、CrewAI、AutoGen、OpenAI Agents SDK 和 Codex 都可以和 OpenACP 一起用。

区别是：

- runtime / coding agent 负责“让 agent 跑起来、调用工具、写代码”。
- OpenACP 负责“让多 agent 的工作可追踪、可审查、可交接、可验收”。

一个偏执行层，一个偏协调协议层。OpenACP 的目标不是抢 agent runtime 的位置，而是让不同 runtime 产出的结果可以进入同一套项目事实和 authority boundary。

## Public Package Hygiene

公开仓库里不应该放内部 response logs、私有 source packs、本地绝对路径、客户材料、凭证或生产日志。私有运行材料应该放在项目自己的 ignored local paths 里，例如 `.openacp-local/` 或你的团队指定目录。

发布前建议跑：

```bash
python tools/openacp_validate_selftest.py
python tools/openacp_validate.py --artifact . --ruleset public-package --strict
```

Validator 只能检查结构、常见泄漏和常见 overclaim。它不是完整 secret scanner，也不是语义正确性证明。正式发布前仍建议使用专用 secret scanner 和人工 review。
