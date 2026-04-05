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
- **LangGraph StateGraph 编排**：替换为 OpenClaw Skills 的依赖声明和自动编排
- **触发/调用方式**：飞书机器人（`extensions/feishu/` 已有支持）
- **MCP 工具**：暂不实现，等多个 Agent 稳定后再考虑封装

---

## 进度

### 已完成
- [x] 创建 `AutoDNA-Skills` 分支（基于 upstream/main）
- [x] 推送到 `origin`（`Dshuishui/Helix`）
- [x] 创建 `extensions/autodna/` 目录结构
- [x] 分析 AutoDNA 项目结构和 6 个 Agent 的逻辑
- [x] **第一个 Skill：Reagent Agent（试点完成）**
  - [x] 分析 `Reagent.py` 和库存 JSON 完整逻辑
  - [x] 编写 `skills/reagent-agent/SKILL.md`
  - [x] 编写 `scripts/get_inventory.py`（自包含，不依赖原项目）
  - [x] 打包、注册到 OpenClaw workspace
  - [x] 飞书验证通过，输出结果正确
  - [x] 整理注册标准流程文档 `SKILL-REGISTRATION-GUIDE.md`

### 进行中
- [ ] **第二个 Skill：Literature Agent**

### 待办（试点验证后依次进行）
- [ ] Literature Agent → Skill
- [ ] Protocol Agent → Skill
- [ ] Code Agent → Skill
- [ ] Hardware Agent → Skill
- [ ] Hypothesis Agent → Skill
- [ ] 串联：用 OpenClaw 编排替代 `ai_scientist.py` 的手工 Planner 逻辑

---

## 目录结构

```
extensions/autodna/
├── PLAN.md                        # 本文件，迁移计划和进度
└── skills/
    └── reagent-agent/
        └── SKILL.md               # Reagent Agent 的 Skill 定义（待完成）
```

---

## 关键文件路径（AutoDNA 原项目）

```
../AutoDNA/AutoDNA-python/scientist/
├── ai_scientist.py          # 主编排引擎（1124行）
├── agents/
│   ├── Reagent.py           # 试点迁移目标
│   ├── Literature.py
│   ├── Protocol.py
│   ├── Code.py
│   ├── Hardware.py
│   └── Hypothesis.py
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

## 新会话接入方式

在新会话开始时，把本文件路径告诉 Claude：
> "请读取 `extensions/autodna/PLAN.md`，我们继续 AutoDNA 迁移工作"
