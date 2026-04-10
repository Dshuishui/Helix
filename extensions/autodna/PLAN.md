# AutoDNA → OpenClaw Skills 迁移计划

## 快速上手（新会话用这句话接入）
> "请读取 `extensions/autodna/PLAN.md`，我们继续 AutoDNA 迁移工作"

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

## 迁移状态总览

| # | 组件 | 状态 | 路径 |
|---|------|------|------|
| 1 | Reagent Agent | ✅ | `skills/reagent-agent/` |
| 2 | Protocol Agent | ✅ | `skills/protocol-agent/` |
| 3 | Hypothesis Agent | ✅ | `skills/hypothesis-agent/` |
| 4 | Code Agent | ✅ | `skills/code-agent/` |
| 5 | Hardware Agent | ✅ | `skills/hardware-agent/` |
| 6 | Literature Agent | ✅ | `skills/literature-agent/` |
| 7 | Shared Store | ✅ | `skills/shared/` |
| 8 | Orchestrator (单 Stage ReAct) | ✅ | `skills/autodna-orchestrator/` |
| 9 | Planner 层（复杂度判断 + Stage 拆分） | ✅ | `skills/autodna-orchestrator/scripts/` |

---

## 完整自动化流程（当前实现）

```
用户一句话 → Orchestrator
  │
  ├─ [Phase 0] 任务分析
  │    ├─ summarize_task.py      → experiment_name
  │    ├─ judge_complexity.py    → simple / complex
  │    └─ decompose_stages.py    → plan_stages.json (complex only)
  │
  ├─ [Phase 1] 逐 Stage 执行（simple = 1个Stage）
  │    ├─ judge_relevant_stages.py → 哪些历史Stage输出要传入
  │    └─ ReAct 自由编排（LLM 自主决定调用顺序）
  │         → Protocol (INITIAL) → 存 protocol_latest
  │         → Reagent            → 存 reagent_latest
  │         → Protocol (ADJUSTMENT) → 更新 protocol_latest
  │         → Code               → 存 code_latest
  │         → Hardware           → 存 hardware_latest
  │              Phase 1: corrector mock 纠错（最多3次，Gemini LLM 修正）
  │              Phase 2: scheduler 运行 → protocol_flow.json
  │         → 失败时: Hypothesis → Protocol(OPTIMIZING) → Code → Hardware（最多2次重试）
  │         └─ 存 stage_N_output_latest
  │
  └─ [Phase 2] 整体判断
       ├─ judge_success.py       → success / failure + retry_stage
       └─ 失败时从 retry_stage 重新执行（最多2次）
```

---

## 架构关键设计

### 1. Skill 间 file_id 传参（对应 AutoDNA shelve 数据库）

```
每个 Skill 生成输出后：
  ① import pathlib; pathlib.Path('/tmp/autodna_skill_output.txt').write_text(r"""...""")
  ② python3 skills/shared/scripts/autodna_store.py write <skill_name>
  ③ 返回 "File ID: <skill_name>_latest"

下游 Skill 需要时：
  python3 skills/shared/scripts/autodna_store.py read <skill_name>
```

存储目录：`~/.openclaw/workspace/autodna_store/`

Stage 间传递使用 `stage_N_output` 作为 skill_name（如 `stage_1_output`）。

### 2. Orchestrator = planner_plan + planner 合并

- **Phase 0**：Python 脚本调 Gemini API，判断复杂度 + 拆分 Stage
- **Phase 1**：LLM 自主 ReAct 循环，对应 AutoDNA `planner()` + EPA_guidance_prompt
- **Phase 2**：Python 脚本判断整体成功，对应 AutoDNA `judge_experiment_success()`

所有 Phase 0/2 的 Python 脚本在 `skills/autodna-orchestrator/scripts/`，
全部使用 stdlib urllib 调 Gemini REST API，无外部依赖。

### 3. Hardware Agent：两阶段自动执行（对应 AutoDNA mock 模式）

`skills/hardware-agent/scripts/run_experiment.py`

| 阶段 | PYTHONPATH | 对应 AutoDNA | 作用 |
|------|-----------|-------------|------|
| Phase 1 纠错 | `executor/corrector/` | `corrector_path` | 严格 mock，检测错误 |
| Phase 2 执行 | `executor/scheduler/` | `scheduler_path` | 生成 protocol_flow.json |

纠错循环：有 stderr → Gemini API 修正（`prompt_corrector` 模板）→ 最多3次

### 4. AutoDNA 架构层次说明

```
AI 层（已迁移）：  OpenClaw Skills ↔ AutoDNA Python Agents + planner_plan
执行层（已实现）：  run_experiment.py ↔ executor/scheduler/ Python 调度器
硬件层（待连接）：  C++ Scheduler (/AutoDNA/Scheduler/) → Modbus → PLC → 仪器
```

---

## 与 AutoDNA 完整行为的差距（当前状态）

| # | 差距 | 状态 |
|---|------|------|
| 完整 user prompt 传给各 Skill | ✅ |
| ReAct 动态工具调用顺序 | ✅ |
| file_id 传参（非全文嵌入） | ✅ |
| Code Agent 仪器兼容性预检查 | ✅ |
| Code 自动纠错循环 | ✅ |
| Hardware 自动执行 + 读取结果 | ✅ |
| 任务复杂度判断（simple/complex） | ✅ |
| 复杂任务 Stage 拆分（planner_plan） | ✅ |
| Stage 间历史上下文传递 | ✅ |
| 整体成功判断 + Stage 级重试 | ✅ |
| 实验类型检测 + system prompt 分类（storage vs default） | ✅ |
| Stage 间 requirement 继承（judge_requirement_relevance） | ✅ |
| 多 Stage 协议汇总（CoflowCache + complete_routine） | ✅ |
| Toolset 按实验类型过滤（RPA 排除 Literature/Hypothesis） | ✅ |
| WebSocket → C++ Scheduler | ⏸ 连接真实硬件时再做 |

---

## 待办（优先级顺序）

1. **打包安装更新后的 Orchestrator**：把新增的 scripts/ 目录一起打包安装
2. **飞书端到端测试（简单实验）**：用 RPA 或其他单 Stage 实验跑完整链路，验证 simple 路径
3. **飞书端到端测试（复杂实验）**：用 DNA 存储/读取等多 Stage 实验，验证 Stage 拆分路径
4. **Reagent Agent 效果对比验证**（需 Gemini API Key）
5. **Literature Agent 飞书测试**（需 Gemini API Key 做 embedding）
6. **C++ Scheduler 对接**（有真实硬件时）：WebSocket 模式 lab_modules，对齐 reagents.json

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
