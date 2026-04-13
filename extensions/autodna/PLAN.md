# AutoDNA → OpenClaw Skills 迁移计划

## 快速上手（新会话用这句话接入）
> "请读取 `extensions/autodna/PLAN.md`，我们继续 AutoDNA 迁移工作"

---

## 当前状态（2026-04-12，第三次更新）

### Task A（理论分析）✅ 已完成

- 理论流程对比文档：`extensions/autodna/FLOW-ANALYSIS.md`
- 修复设计差异：storage_write/read → Mode A（自由 ReAct）

### Task B（端到端运行）🔄 进行中

累计运行记录（test-logs/，已加入 .gitignore 不上传 GitHub）：

| 文件 | 时间 | 结果 |
|------|------|------|
| full-pipeline-rpa-01-orchestrator-not-triggered | 04-11 09:53 | orchestrator 未触发，手动执行 |
| full-pipeline-rpa-02-success-265steps | 04-11 10:31 | ✅ 首次成功，265步骤，protocol_flow.json 生成 |
| full-pipeline-rpa-03-429-agent-manual-simulate | 04-11 10:53 | 429 → Agent 违规手动模拟（bug） |
| full-pipeline-rpa-04-429-correct-stop | 04-11 11:05 | 429 → 正确 STOP（修复后） |
| chat-Assistant-1775979058748 | 04-12 14:52 | 404（gemini-2.0-flash 废弃） |
| chat-Assistant-1775981127156 | 04-12 15:47 | 404 → Agent 手动模拟（SKILL.md 漏洞） |
| chat-Assistant-1776005870534 | 04-12 22:52 | 400（urllib ProxyHandler HTTPS 缺陷） |

累计修复问题：

| 问题 | 状态 | 修复方式 |
|------|------|---------|
| GEMINI_API_KEY 未注入 gateway | ✅ | 写入 LaunchAgent plist |
| autodna-orchestrator 未被触发 | ✅ | 扩大 description 触发范围 |
| 429/任意错误时 Agent 手动模拟 | ✅ | SKILL.md ABSOLUTE RULE 覆盖所有 HTTP 错误 |
| gemini-2.0-flash 对新用户废弃 → 404 | ✅ | 8个脚本改为 gemini-2.5-flash |
| urllib ProxyHandler HTTPS CONNECT 缺陷 → 400 | ✅ | 8个脚本改用 curl 子进程发请求 |
| openclaw gateway restart 不重载 plist env → key 未更新 | ✅ | 必须用 launchctl unload + load |
| Protocol(ADJUSTMENT) 步骤缺失 | ⚠️ | 下次关注 |
| Code Agent 生成代码荧光仪不分批 | ✅ | code-agent SKILL.md 加容量规则 |
| autodna_store 旧文件影响新会话 | ✅ | 每次运行前清空 |
| API key 泄漏到 GitHub（commit 含明文 key） | ✅ | git reset + force push + test-logs 加入 .gitignore |
| Protocol Agent 在 RPA Option 内写操作参数（违反 RPA 规则）| ⚠️ | 待加强 protocol-agent SKILL.md 示例 |
| Code Agent timer 累加逻辑错误（wait(time_point*60) 应为 wait(300)）| ✅ | code-agent SKILL.md 加 timer 规则 |
| Code Agent print 中间过程（违反 print only for final results）| ⚠️ | 下次关注，规则已在 SKILL.md 但 LLM 未遵守 |
| Orchestrator 在 Code Agent 完成后未调用 Hardware Agent 就结束 | ✅ | orchestrator SKILL.md 明确 RPA 必须调 Hardware |

**最新修复细节（2026-04-12）**：

1. **gemini-2.0-flash → gemini-2.5-flash**：新 API key 不支持旧模型，8 个 Phase 0 脚本批量替换
2. **urllib → curl 子进程**：Python 3.9 的 `urllib.ProxyHandler` 对 HTTPS CONNECT 隧道实现有缺陷，在 gateway LaunchAgent 子进程里不稳定走代理（HTTP 400 地理限制）。改用 `curl --proxy` 显式指定代理，完全可靠
3. **ABSOLUTE RULE 加强**：从只覆盖 429/missing key，改为覆盖所有非零退出码和任意 HTTP 错误
4. **key 安全**：旧 key（AIzaSyDbLfjg...）已通过 commit 暴露到 public 仓库，现已销毁；新 key 写入 plist，test-logs 加入 .gitignore

**当前状态**：最新修复（curl 子进程）尚未在飞书验证，下次运行应能通过 Phase 0。

### 下一步

**每次运行前**：
```bash
rm -f ~/.openclaw/workspace/autodna_store/*.txt
```

**Step 1**：飞书 `/new` + 发 RPA prompt，验证 Phase 0 脚本能通过（summarize→detect→complexity）

**Step 2**：确认完整流程跑通（Phase 0 → Phase 1 → protocol_flow.json 生成）

**Step 3**：关注 Protocol(ADJUSTMENT) 步骤是否出现（Reagent 检查后 Protocol 应有 ADJUSTMENT）

**Step 4**：运行 AutoDNA baseline 对比
```bash
cd ~/Documents/Github/AutoDNA/AutoDNA-python/scientist
conda activate autodna
GEMINI_API_KEY=<key> python ai_scientist.py --rpa --mock_mode
```

**Step 5**：对比两个 protocol_flow.json 的 `steps[].action` 和 `steps[].parameters`

### 环境配置（当前状态）

- GEMINI_API_KEY（AIzaSyCRgerPay...）已写入 `~/Library/LaunchAgents/ai.openclaw.gateway.plist`
- plist 中代理：`https_proxy=http://127.0.0.1:7890`（脚本现在用 curl 显式指定，不再依赖 urllib 自动读取）
- 所有 Skills 已安装最新版本（autodna-orchestrator 含 curl 子进程版本）
- stale config warning（plugins.entries.autodna-orchestrator）每次重启出现，无害，可忽略

---

## 背景与目标

AutoDNA（`../AutoDNA/AutoDNA-python/`）是基于 LangChain/LangGraph 的多智能体实验室自动化系统。
目标：把全部 Agent 迁移为 OpenClaw Skill，在龙虾平台复现 AutoDNA **所有实验类型**的完整 AI 层效果，
最终实现"一句话 → 龙虾自动完成整个实验流程"。

- 工作分支：`AutoDNA-Skills`（`Dshuishui/Helix`）
- 原项目：`../AutoDNA/AutoDNA-python/scientist/`
- 飞书机器人：已配置并验证可用（模型：Gemini 2.5 Pro / DeepSeek）

---

## AutoDNA 核心架构（对应关系）

```
AutoDNA                              OpenClaw Skills
─────────────────────────────────────────────────────────
ai_scientist.py
  └─ planner_plan()                  autodna-orchestrator (Phase 0 + Phase 2)
       ├─ summarize_task()              scripts/summarize_task.py
       ├─ judge_task_complexity()       scripts/judge_complexity.py
       ├─ choose_system_prompt()        scripts/detect_experiment_type.py
       ├─ decompose_stages()            scripts/decompose_stages.py
       ├─ judge_relevant_stages()       scripts/judge_relevant_stages.py
       ├─ judge_requirement_relevance() scripts/judge_requirement_relevance.py
       ├─ complete_routine()            scripts/complete_routine.py
       ├─ judge_experiment_success()    scripts/judge_success.py
       └─ planner() × N stages         autodna-orchestrator (Phase 1, ReAct loop)
            ├─ Literature tool           literature-agent
            ├─ Protocol tool             protocol-agent
            ├─ Reagent tool              reagent-agent
            ├─ Code tool                 code-agent
            ├─ Hardware tool             hardware-agent
            └─ Hypothesis tool           hypothesis-agent

硬件执行层（已实现）：
  executor/corrector/ + scheduler/    run_experiment.py (Phase 1 纠错 + Phase 2 执行)

数据传递（已实现）：
  shelve file_id 机制                 autodna_store.py + /tmp/autodna_skill_output.txt
```

---

## 迁移状态总览（全部完成）

| # | 组件 | 状态 | 路径 |
|---|------|------|------|
| 1 | Reagent Agent | ✅ | `skills/reagent-agent/` |
| 2 | Protocol Agent | ✅ | `skills/protocol-agent/` |
| 3 | Hypothesis Agent | ✅ | `skills/hypothesis-agent/` |
| 4 | Code Agent | ✅ | `skills/code-agent/` |
| 5 | Hardware Agent | ✅ | `skills/hardware-agent/` |
| 6 | Literature Agent | ✅ | `skills/literature-agent/` |
| 7 | Shared Store | ✅ | `skills/shared/` |
| 8 | Orchestrator (ReAct + Planner 全层) | ✅ | `skills/autodna-orchestrator/` |

Orchestrator scripts（对应 AutoDNA planner_plan 各函数）：

| 脚本 | 对应 AutoDNA | 功能 |
|------|-------------|------|
| `summarize_task.py` | `summarize_task()` | 生成实验简称 |
| `judge_complexity.py` | `judge_task_complexity()` | simple / complex |
| `detect_experiment_type.py` | `choose_system_prompt()` + `choose_toolset()` | 输出 storage_write / storage_read / storage / rpa / default |
| `decompose_stages.py` | `plan_system_prompt` + LLM | 拆分 Stage JSON |
| `judge_relevant_stages.py` | `judge_relevant_stages()` | 历史 Stage 上下文选择 |
| `judge_requirement_relevance.py` | `judge_requirement_relevance()` | 跨 Stage requirement 继承 |
| `complete_routine.py` | `complete_routine()` | DNA Storage Write 协议汇总 |
| `judge_success.py` | `judge_experiment_success()` + `analyze_failure_and_get_retry_stage()` | 整体成功判断 + 重试分析 |

---

## 与 AutoDNA AI 层行为的差距（全部关闭）

| 差距 | 状态 |
|------|------|
| 完整 user prompt 传给各 Skill | ✅ |
| ReAct 动态工具调用顺序（planner） | ✅ |
| file_id 传参（对应 shelve 数据库） | ✅ |
| Code Agent 仪器兼容性预检查 | ✅ |
| Code 自动纠错循环（corrector mock） | ✅ |
| Hardware 自动执行 + 读取 protocol_flow.json | ✅ |
| 任务复杂度判断（simple/complex） | ✅ |
| 复杂任务 Stage 拆分（planner_plan） | ✅ |
| Stage 间历史上下文传递 | ✅ |
| Stage 间 requirement 继承 | ✅ |
| 整体成功判断 + Stage 级重试 | ✅ |
| 实验类型检测 + system prompt 分类 | ✅ |
| Toolset 按实验类型过滤（RPA） | ✅ |
| 多 Stage 协议汇总（DNA Storage Write） | ✅ |
| WebSocket → C++ Scheduler | ⏸ 真实硬件时再做 |

---

## 下一步：理论对比分析 + 端到端验证（最高优先级）

### 任务 A（理论分析，下一个 session 优先做）

**目标**：从代码层面逐步对比，从"接收用户需求"到"输出 protocol_flow.json"，
验证 OpenClaw 龙虾的执行流程和逻辑是否与 AutoDNA 一致。

**分析方式**：不需要实际运行，只需对照代码逻辑，逐层比较：

| 层次 | AutoDNA | OpenClaw | 是否一致 |
|------|---------|---------|---------|
| 入口 | `ai_scientist.py main()` → `main_routine()` | 飞书消息 → autodna-orchestrator SKILL.md | 待分析 |
| 任务分析 | `planner_plan()` Phase 0 | Phase 0 脚本（summarize/complexity/type/decompose） | 待分析 |
| ReAct 循环 | `planner()` → LangGraph agent↔tools 循环 | Orchestrator Phase 1 LLM 自由编排 | 待分析 |
| Protocol 生成 | `Protocol` LangChain tool | protocol-agent SKILL.md | 待分析 |
| Reagent 检查 | `Reagent` LangChain tool | reagent-agent SKILL.md | 待分析 |
| Code 生成 | `Code` LangChain tool | code-agent SKILL.md | 待分析 |
| Hardware 执行 | `Hardware` LangChain tool → `execute_code_to_scheduler()` | hardware-agent → run_experiment.py | 待分析 |
| 脚本纠错 | corrector mock + LLM 修正 | run_experiment.py Phase 1 | 待分析 |
| 调度执行 | scheduler.py → protocol_flow.json | run_experiment.py Phase 2 → protocol_flow.json | 待分析 |

**分析时需要读的关键文件**：
- AutoDNA: `scientist/agents/Protocol.py`, `agents/Code.py`, `agents/Hardware.py`
- AutoDNA: `executor/scheduler/scheduler.py`（protocol_flow.json 生成逻辑）
- 我们: `skills/*/SKILL.md`（各 Agent 的行为描述）
- 我们: `skills/hardware-agent/scripts/run_experiment.py`

### 任务 B（端到端运行对比，需要用户跑）

**前置条件**（已就绪）：
- autodna conda 环境：langchain/langgraph 已安装 ✅
- OpenClaw gateway：已安装所有 Skills ✅
- 需要 GEMINI_API_KEY

**Step 1：运行 AutoDNA baseline**

```bash
cd ~/Documents/Github/AutoDNA/AutoDNA-python/scientist
conda activate autodna

# RPA 实验（simple 路径，建议先跑）
GEMINI_API_KEY=你的key python ai_scientist.py --rpa --mock_mode

# mock 模式遇到荧光读数暂停 → 直接按 Enter 或输入 -1 跳过
```

输出位置：`executor/scheduler/protocol_flow.json`，以及 `output/stage-N/` 各步骤 JSON。

**Step 2：运行 OpenClaw**

把 `prompts/user_prompt_rpa.md` 内容发给飞书机器人，触发 autodna-orchestrator 全链路。

```bash
# 确保 gateway 启动时带上 key
GEMINI_API_KEY=你的key openclaw gateway restart
```

**Step 3：对比 protocol_flow.json**

重点字段：
- `steps[].action`：操作序列类型
- `steps[].parameters`：容器、试剂、体积、时间参数
- 关键仪器操作出现位置（`fluorometer_measure`、`container_allocate`）

成功标准：核心操作序列大体一致，关键参数在合理范围内一致（LLM 生成允许细微差异）。

### 使用的 user prompt 文件

```
../AutoDNA/AutoDNA-python/scientist/prompts/user_prompt_rpa.md      （RPA，先用这个）
../AutoDNA/AutoDNA-python/scientist/prompts/user_prompt_full.md     （DNA 合成）
../AutoDNA/AutoDNA-python/scientist/prompts/user_prompt_storage.md  （DNA 存储）
```

---

## 完整自动化流程（当前实现）

```
用户一句话 → Orchestrator
  │
  ├─ [Phase 0] 任务分析
  │    ├─ summarize_task.py         → experiment_name
  │    ├─ detect_experiment_type.py → storage_write / storage_read / storage / rpa / default
  │    ├─ judge_complexity.py       → simple / complex
  │    ├─ decompose_stages.py       → plan_stages.json (complex only)
  │    └─ [storage_read only] autodna_store read write_summary → 注入初始上下文
  │
  ├─ [Phase 1] 逐 Stage 执行（simple = 1个Stage）
  │    ├─ judge_relevant_stages.py        → 哪些历史Stage输出要传入
  │    ├─ judge_requirement_relevance.py  → 前Stage的requirement是否继承
  │    └─ ReAct 编排（default/rpa: 自由; storage*: 严格逐步）
  │         → Protocol (INITIAL) → 存 protocol_latest
  │         → Reagent            → 存 reagent_latest
  │         → Protocol (ADJUSTMENT) → 更新 protocol_latest
  │         → Code               → 存 code_latest
  │         → Hardware           → 存 hardware_latest
  │              run_experiment.py Phase 1: corrector mock 纠错（最多3次）
  │              run_experiment.py Phase 2: scheduler 运行 → protocol_flow.json
  │         → 失败时: Hypothesis → Protocol(OPTIMIZING) → Code → Hardware（最多2次）
  │         └─ 存 stage_N_output_latest
  │              [storage_write only] 备份 protocol_stage_N
  │
  └─ [Phase 2] 整体判断
       ├─ judge_success.py              → success / failure + retry_stage
       ├─ 失败时从 retry_stage 重新执行（最多2次）
       └─ [storage_write only] complete_routine.py → write_summary_latest
```

---

## 架构关键设计

### Skill 间 file_id 传参

```
每个 Skill 生成输出后：
  ① import pathlib; pathlib.Path('/tmp/autodna_skill_output.txt').write_text(r"""...""")
  ② python3 skills/shared/scripts/autodna_store.py write <skill_name>
  ③ 返回 "File ID: <skill_name>_latest"

下游 Skill 需要时：
  python3 skills/shared/scripts/autodna_store.py read <skill_name>
```

存储目录：`~/.openclaw/workspace/autodna_store/`
Stage 间：`stage_N_output`（如 `stage_1_output_latest.txt`）

### Hardware Agent 两阶段执行

`skills/hardware-agent/scripts/run_experiment.py`

| 阶段 | PYTHONPATH | 作用 |
|------|-----------|------|
| Phase 1 纠错 | `executor/corrector/` | 严格 mock，LLM 自动修正（最多3次） |
| Phase 2 执行 | `executor/scheduler/` | 生成 protocol_flow.json |

### 实验类型 → 行为映射

| detect_experiment_type | 编排模式 | 可用 Skills | 额外行为 |
|-----------------------|---------|------------|--------|
| `storage_write` | 自由 ReAct | 全部 | complete_routine（汇总协议） |
| `storage_read` | 自由 ReAct | 全部 | 加载 write_summary 为初始上下文 |
| `storage` | 严格逐步 | 全部 | — |
| `rpa` | 自由 ReAct | Protocol/Reagent/Code/Hardware | — |
| `default` | 自由 ReAct | 全部 | — |

---

## 注册 Skill 快速命令

```bash
# 打包（需禁用沙箱）
python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  extensions/autodna/skills/<skill-name> /tmp/autodna-skills

# 安装（完整流程）
rm -f ~/.openclaw/extensions/<skill-name>.skill
openclaw plugins install /tmp/autodna-skills/<skill-name>.skill
openclaw config unset plugins.entries.<skill-name>
cd ~/.openclaw/workspace/skills && rm -rf <skill-name>
unzip -o /tmp/autodna-skills/<skill-name>.skill

# 重启
openclaw gateway restart
```

详细踩坑记录见：`SKILL-REGISTRATION-GUIDE.md`
