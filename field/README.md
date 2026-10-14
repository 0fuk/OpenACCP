# Field Rules (实战规则集,2026-10 同步)

这是 OpenACCP 作者在一个真实多会话、多代理生产项目(Node + PostgreSQL 业务系统,连续发版 1.6.x → 1.7.10)里跑出来的**现役规则**。仓库根目录的 `skills/*-openaccp` 是 OpenACCP 的原始角色模型;本目录是它在实战中演化后的版本,以中文写成,按「一次做对、最少 token、owner 零输入」为目标。两套可并存:原始 skills 讲角色与契约,`field/` 讲门、节奏与纪律。

> 文内出现的路径(`C:\VyqoAI\Yirun\...`)、协调目录名(`coordination_dawn`)、角色代号(C1/C2/C3、DP 线)都是该项目的实例,换项目时整体替换即可;没有任何凭据、客户数据或内部主机地址。

## 与原始 OpenACCP 角色模型的对应

| OpenACCP 原始概念 | 实战演化 | 文件 |
|---|---|---|
| Primary orchestrator | 主编排 Cn(只编排 / 终审 / 合流 / 台账,不下场写码);换代用 `/reboot` 交接件 | `skills/reboot/`、`skills/orch-plan/` |
| Frontier lane / worker / reviewer | 每线一棵 git worktree + 文件信箱定向件(文件名即路由) | `skills/coordination-worktree/` |
| Handoff consume / acceptance | **五门发版范式**:①任务门 ②合流门 ③盲测门 ④发布门 ⑤真人门;每门硬门清单 + 五门台账 | `skills/5gate/` |
| Review report | 发版三路验证(全量回归 + 无背景盲测 + 交叉判读「既有 / 新引入」) | `skills/verify-3way/` |
| Reviewer | 两名独立高级复核(A 改动纪律 / B 影响半径),复核不降档 | `skills/senior-review/` |
| Return-wake protocol | 无人值守推进:文件信箱唯一通道 + Monitor + ScheduleWakeup 兜底 + 30 分钟活性判停 | `skills/keep-pushing/`、`skills/moniter-on/` |
| Current manifest / machine summary | compact 前先外置 checkpoint(owner 原话、门次、基面 SHA、在飞表) | `skills/compact-s/` |
| Discovery | 导航校准(对照台账 / 计划 / 终点逐项核偏) | `skills/compass/` |
| Formal report / human explain | 正式报告与说人话(中文版) | `skills/formal-report/`、`skills/human-explain/`、`skills/cn-prose/` |
| — | 旧系统快照换库全流程(读取 · 验真 · 彩排 · 切库 · 回滚锚) | `skills/db-cutover/` |
| — | GitHub 作为可信最终备份的同步与验证 | `skills/gh-backup/` |
| — | 决策级盲区调研;功能开发规程 | `skills/need-research/`、`skills/feature-dev/` |
| Authority charter | 施工通则:环境、禁区(禁 stash / amend / force-push、rm 只许字面路径)、验证精简口径、token 纪律 | `rules/施工通则-20261003.md` |

## 用法

把 `field/skills/<name>` 整目录复制到 `~/.claude/skills/<name>`(Claude Code),或按你的 agent 平台的 skill 目录安装;`rules/` 内容放进项目根的 `CLAUDE.md` 或等价的常驻规则文件。

## 核心经验(都已写进对应 skill)

- 全量回归只在合流门跑一次;施工线禁全量(实案 11.5 h → 1.7 h)。
- 返工是最大的 token 黑洞:一次性过的硬门写进①门验收。
- 每次派工必挂叫醒;被唤醒先看子代理 output 文件 mtime,> 30 分钟无动作就停掉重派。
- 盲测员不带任何背景;红卡先用 `git diff <上一生产标签>..<rc>` 判既有再定是否阻发车。
- compact 不是损失点:checkpoint 龄不超过 60 分钟,摘要与 checkpoint 冲突以 checkpoint 为准。
- owner 候拍板的题必带推荐与代价,不留 open question。
