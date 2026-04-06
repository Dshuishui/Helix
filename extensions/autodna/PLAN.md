# AutoDNA → OpenClaw Skills 迁移计划

## 背景

AutoDNA（`../AutoDNA/AutoDNA-python/`）是一个基于 LangChain/LangGraph 手工串联的多智能体实验室自动化系统，目标是把它的每个 Agent 迁移为 OpenClaw 的 Skill，利用 OpenClaw 的模块化和消息通道优势重构整个系统。

上游仓库：https://github.com/Dshuishui/AutoDNA
当前工作分支：`AutoDNA-Skills`（基于 `upstream/main` 创建）

---

## AutoDNA 原有架构（LangChain）

6 个专用 Agent，手工编排顺序：

| Agent | 原文件 | 职责 |
|-------|--------|------|
| Literature | `agents/Literature.py` | 在 400+ 论文数据库中检索工艺信息 |
| Protocol | `agents/Protocol.py` | 设计实验步骤和工作流 |
| Reagent | `agents/Reagent.py` | 检查试剂库存 JSON 可用性 |
| Code | `agents/Code.py` | 生成并执行 Python 自动化脚本 |
| Hardware | `agents/Hardware.py` | 转换为硬件设备 API 调用 |
| Hypothesis | `agents/Hypothesis.py` | 失败时生成优化建议（闭环重试） |

串联方式：`ai_scientist.py`（1124行）手工硬编码阶段顺序，通过 `file_id`（Shelve 数据库）在 Agent 间传递数据。

---

## 迁移策略

- **Python 核心逻辑**：保留，不简化
- **LangChain @tool 装饰器**：替换为 OpenClaw Skill 定义
- **LangGraph StateGraph 编排**：替换为 OpenClaw Orchestrator Skill
- **触发/调用方式**：飞书机器人
- **MCP 工具**：暂不实现，等多个 Agent 稳定后再考虑封装

---

## 进度

### 已完成

- [x] 创建 `AutoDNA-Skills` 分支，推送到 `Dshuishui/Helix`
- [x] 创建 `extensions/autodna/` 目录结构
- [x] 分析 AutoDNA 项目全部 6 个 Agent 的逻辑
- [x] 整理 `SKILL-REGISTRATION-GUIDE.md`（含踩坑经验，持续更新）
- [x] 精简 `CLAUDE.md`，原版保留为 `CLAUDE-upstream.md`

- [x] **Skill 1：Reagent Agent**
  - 分析 `Reagent.py` + 库存 JSON 逻辑
  - 编写 `skills/reagent-agent/SKILL.md`
  - 编写 `scripts/get_inventory.py`（自包含，不依赖原项目）
  - 复制 9 个试剂库存 JSON 到 `references/`
  - 打包注册，飞书验证通过

- [x] **Skill 2：Protocol Agent**
  - 分析 `Protocol.py` + `prompts/agents/Protocol/prompt.py`
  - 识别 5 种模式（INITIAL / REFINEMENT / ADJUSTMENT / OPTIMIZING / ALGORITHM）
  - 编写 `skills/protocol-agent/SKILL.md`（覆盖 INITIAL / ADJUSTMENT / OPTIMIZING 三种模式）
  - 补充 RPA 专用规则（Automation + Readiness + 无操作细节）
  - 打包注册，飞书验证通过（两轮测试，修复 DNA 提取步骤问题）

- [x] **Skill 3：Hypothesis Agent**
  - 分析 `Hypothesis.py` + `prompts/agents/Hardware/prompt.py`（提示词复用）
  - 识别 3 阶段逻辑（Stage A 生成假设 → Stage B 摘要 → Stage C 生成建议）
  - Stage B 为内部路由步骤，迁移时省略，直接 A→C
  - 编写 `skills/hypothesis-agent/SKILL.md`
  - 打包注册，飞书验证通过

- [x] **三 Agent 手动串联验证**（`test-logs/three-agent-chain-test-01.md`）
  - Protocol(INITIAL) → Reagent → Protocol(ADJUSTMENT) → Hypothesis 四步串联
  - 数据通过对话上下文自动传递，无需手动复制粘贴
  - 验证结论：框架可行，各 Skill 行为符合预期
  - 已知限制：Protocol 第一次生成不知道库存，ADJUSTMENT 后流程偏简；串联完整化后解决

### 进行中

- [ ] **Reagent Agent 效果对比验证**（等 Gemini API Key 可用时进行）
  - 测试用例：NC-1、Nuclease-Free Water、EDTA、Tween-20、RPA Reagent Buffer（RPA 实验）
  - 对比维度：每个试剂的 available/not available 结论是否一致

### 待办

- [ ] **Skill 4：Code Agent**（下一个迁移目标）
  - 输入：Protocol Agent 输出的实验流程
  - 职责：生成可执行的 Python 自动化脚本
  - 原文件：`agents/Code.py`

- [ ] Literature Agent → Skill（依赖 paper-qa + 400 篇论文数据库，基础设施复杂，暂缓）
- [ ] Hardware Agent → Skill（依赖具体硬件设备 API，高度定制，暂缓）

- [ ] **Orchestrator Skill**（所有 Agent 迁移完成后）
  - 替代 `ai_scientist.py` 的手工编排逻辑
  - 自动按顺序调用各 Skill，强制每步重新注入 Skill 指令（解决"不一致风险"）
  - 完整流程：Protocol(INITIAL) → Reagent → Protocol(ADJUSTMENT) → [run] → Hypothesis → Protocol(OPTIMIZING) → Code → Hardware

---

## 目录结构

```
extensions/autodna/
├── PLAN.md                          # 本文件
├── SKILL-REGISTRATION-GUIDE.md      # 注册标准流程 + 踩坑经验
├── CLAUDE-upstream.md               # 原始 OpenClaw CLAUDE.md 备份
├── test-logs/                       # 飞书测试聊天记录
│   ├── reagent-agent-test-01.md
│   ├── protocol-agent-test-01-before-fix.md
│   ├── protocol-agent-test-02-after-fix.md
│   └── three-agent-chain-test-01.md
└── skills/
    ├── reagent-agent/
    │   ├── SKILL.md
    │   ├── scripts/get_inventory.py
    │   └── references/              # 9 个试剂库存 JSON
    ├── protocol-agent/
    │   └── SKILL.md
    └── hypothesis-agent/
        └── SKILL.md
```

---

## 关键文件路径（AutoDNA 原项目）

```
../AutoDNA/AutoDNA-python/scientist/
├── ai_scientist.py          # 主编排引擎（1124行）
├── agents/
│   ├── Reagent.py           ✅ 已迁移
│   ├── Protocol.py          ✅ 已迁移
│   ├── Hypothesis.py        ✅ 已迁移
│   ├── Code.py              ⬜ 待迁移（下一个）
│   ├── Hardware.py          ⬜ 待迁移（暂缓）
│   └── Literature.py        ⬜ 待迁移（暂缓）
├── llm/
│   ├── model.py             # 模型初始化（Gemini 2.5-Pro）
│   └── my_react_agent.py    # LangGraph ReAct 实现
├── tools/
│   ├── file_manager.py      # Shelve 数据库，Agent 间数据传递
│   └── utils.py             # 缓存系统
├── prompts/agents/          # 各 Agent 的提示词
└── input/reagents/          # 试剂库存 JSON（10+ 种类）
```

---

## 效果对比验证方法

### Reagent Agent 对比（等 Gemini API Key 可用）

```python
# 在 ../AutoDNA/AutoDNA-python/scientist/ 目录下运行
from tools.utils import get_inventory
from agents.Reagent import format_reagents_json, pharmacy_prompt_output_format
from llm.model import pharmacy_model
from langchain_core.prompts import PromptTemplate
from config import settings

settings.rpa = True
reagent_repo = get_inventory(True)
reagent_repo_str = format_reagents_json(reagent_repo)

requested = "NC-1, Nuclease-Free Water, EDTA, Tween-20, RPA Reagent Buffer"
# ... 构造 prompt 并调用
```

对比维度（只比对结论，不要求逐字相同）：

| 试剂 | 原 AutoDNA 结论 | OpenClaw Skill 结论 | 一致？ |
|------|----------------|---------------------|-------|
| NC-1 | | available, 1X | |
| Nuclease-Free Water | | available, liquid | |
| EDTA | | not available | |
| Tween-20 | | not available | |
| RPA Reagent Buffer | | available, 1X | |

---

## 新会话接入方式

在新会话开始时，把本文件路径告诉 Claude：
> "请读取 `extensions/autodna/PLAN.md`，我们继续 AutoDNA 迁移工作"
