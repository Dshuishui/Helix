# AutoDNA → OpenClaw Skills 迁移计划

## 快速上手（新会话用这句话接入）
> "请读取 `extensions/autodna/PLAN.md`，我们继续 AutoDNA 迁移工作"

---

## 背景

AutoDNA（`../AutoDNA/AutoDNA-python/`）是一个基于 LangChain/LangGraph 手工串联的多智能体实验室自动化系统。目标：把每个 Agent 迁移为 OpenClaw Skill，最终用 Orchestrator Skill 替代原来的手工编排逻辑。

- 工作分支：`AutoDNA-Skills`（`Dshuishui/Helix`）
- 原项目：`../AutoDNA/AutoDNA-python/scientist/`
- 飞书机器人：已配置并验证可用（模型：Gemini 2.5 Pro / DeepSeek）

---

## 6 个 Agent 迁移状态总览

| # | Agent | 状态 | Skill 路径 | 说明 |
|---|-------|------|-----------|------|
| 1 | Reagent | ✅ 完成 | `skills/reagent-agent/` | 有 Python 脚本读取库存 JSON |
| 2 | Protocol | ✅ 完成 | `skills/protocol-agent/` | 纯 LLM，3 种模式 |
| 3 | Hypothesis | ✅ 完成 | `skills/hypothesis-agent/` | 纯 LLM，3 阶段简化为 2 阶段 |
| 4 | Code | ✅ 完成 | `skills/code-agent/` | 线性化+代码生成，含 lab_modules.py |
| 5 | Orchestrator | ✅ 完成 | `skills/autodna-orchestrator/` | RPA happy path，串联全流程 |
| 6 | Hardware | ✅ 完成 | `skills/hardware-agent/` | 指导运行脚本+收集结果，脚本由用户在 AutoDNA 环境执行 |
| 7 | Literature | ✅ 完成 | `skills/literature-agent/` | paper-qa 装在 conda autodna 环境，PDF 原地引用 |

---

## 已完成工作

### 基础设施
- `extensions/autodna/` 目录结构建立
- `SKILL-REGISTRATION-GUIDE.md`：注册标准流程 + 全部踩坑经验（持续更新）
- `CLAUDE.md` 精简（原版保留为 `CLAUDE-upstream.md`）
- `test-logs/` 目录：存放飞书测试聊天记录

### Skill 1：Reagent Agent
- 自包含 Python 脚本 `get_inventory.py`（不依赖原项目）
- 9 个试剂库存 JSON 复制到 `references/`
- 飞书验证通过

### Skill 2：Protocol Agent
- 覆盖 INITIAL / ADJUSTMENT / OPTIMIZING 三种模式
- RPA 专用规则（Automation + Readiness + 无操作细节）
- 两轮测试，修复了"DNA 提取步骤"问题（`test-logs/protocol-agent-test-02-after-fix.md`）

### Skill 3：Hypothesis Agent
- AutoDNA 3 阶段（A→B→C）简化为 2 阶段（A→C），Stage B 为内部路由无需保留
- 飞书验证通过

### 三 Agent 手动串联验证
- 测试记录：`test-logs/three-agent-chain-test-01.md`
- 流程：Protocol(INITIAL) → Reagent → Protocol(ADJUSTMENT) → Hypothesis
- 结论：框架可行，数据通过对话上下文自动传递
- 已知限制：Protocol 首次生成不感知库存，ADJUSTMENT 后流程偏简；Orchestrator 完成后自然解决

---

## Code Agent 迁移完成记录

核心逻辑：
1. **线性化**：`extractor_prompt_extract` 规则，把多选项流程展开为一致路径（`### PATH START ###`）
2. **代码生成**：`prompt_code_main` 规则，每条路径生成一个 Python 脚本（`## SCRIPT START ##`）

简化项：代码执行+自动修正循环、WebSocket 硬件回调（用户在 AutoDNA 环境自行运行）

关键文件：`skills/code-agent/references/lab_modules.py`（完整硬件 API，从原项目 `tools/lab_modules.py` 复制）

---

## Orchestrator 迁移完成记录

对应 AutoDNA `ai_scientist.py` 中的 `planner_plan()` + EPA_guidance_prompt 逻辑。

**当前版本：ReAct 风格自由编排（2026-04-09 重构）**

架构与 AutoDNA 对齐：
- AutoDNA 本质是 LangGraph ReAct 循环，6 个 `@tool` 函数，LLM 自主决定调用顺序
- 我们的 Orchestrator 等价实现：LLM 自由决定调用哪些 Skill、顺序如何
- 不再有固定 Stage 序列，适用于任何实验类型（RPA、PCR、NGS 等）

核心机制：
- **完整原始 prompt 传递**：每次 Skill 调用必须附带用户完整原始请求（verbatim）
- **上下文透传**：前序 Skill 的输出直接嵌入下次调用（等价于 AutoDNA file_id 传参）
- **先推理再行动**：每次 Skill 调用前解释原因（对应 AutoDNA EPA_guidance_prompt）
- **失败重试**：最多 2 次；每次 Hypothesis Agent 收到历史假设列表避免重复
- **停止信号**：`### workflow ### / ### final_result ###`（与 AutoDNA 完全一致）

简化项（与原始 AutoDNA 相比）：
- file_id + Shelve DB → 对话上下文（功能等价）
- WebSocket 硬件自动执行 → 用户手动在 AutoDNA 环境运行（硬件基础设施不可迁移）
- LangGraph 状态机 → 对话回合（无 checkpoint/resume 需求）

### 后续扩展计划

**Literature Agent 集成**
- Orchestrator 已在 Available Skills 表中列出 Literature Agent
- LLM 自主决定何时查文献（用户说"查文献"或流程需要时）

---

## 与 AutoDNA 的差距分析（RPA 场景对照）

### AutoDNA 实际执行逻辑（RPA）
- `judge_task_complexity()` 判断为 simple → 单阶段 ReAct 循环
- 每个工具调用都能通过 `get_current_user_prompt()` 访问**完整原始 prompt**
- Hardware 通过 WebSocket 自动执行脚本，荧光仪自动采集数据
- 工具调用顺序由 LLM 自主决定

### 已知差距与修复计划

| # | 差距 | 严重程度 | 修复方案 | 状态 |
|---|------|---------|---------|------|
| 1 | **完整 user prompt 未传给各 Stage** | 高 | Orchestrator 在每个 Stage 调用时附上完整原始输入，不只传摘要 | ✅ 已修 |
| 2 | **荧光判断逻辑（NTC×3 阈值）未传入 Code/Hardware** | 高 | 同上（随完整 prompt 一起传入解决）| ✅ 随 #1 解决 |
| 3 | **Code Agent 未收到库存信息，容器名可能出错** | 高 | Orchestrator Stage 4 把 Reagent 输出传给 Code Agent；Code Agent 规则 5 要求使用库存中的精确名称 | ✅ 已修 |
| 4 | **Code Agent 缺少仪器兼容性预检查** | 中 | Code Agent 新增 Step 0（pre-check），先确认步骤能映射到 lab_modules API | ✅ 已修 |
| 5 | **Hardware 自动执行 → 手动汇报** | 高（不可避免）| 用户连接真实硬件后自然解决；测试阶段用户手动汇报 | ⏸ 硬件依赖 |
| 6 | **ReAct 动态调用 vs 固定 Stage** | 中 | Orchestrator 重构为 ReAct 风格，LLM 自由决定 Skill 调用顺序 | ✅ 已修（2026-04-09）|

### Protocol Agent 已修复项（2026-04-09）
- INITIAL: "DO NOT prepare ANY solutions or buffers"（原文加强）
- ADJUSTMENT: 过滤后输出新 Reagent Check List（未验证试剂）；补充 optional/中间产物规则
- OPTIMIZING: 新增第二步验证（多 option 的 step 只保留最优）

### Orchestrator 已修复项（2026-04-09）
- 架构从固定 6-Stage 重构为 ReAct 风格自由编排，与 AutoDNA LangGraph 对齐
- 每次 Skill 调用必须附带完整原始用户请求（verbatim）
- 停止格式与 AutoDNA EPA_guidance_prompt 完全一致

### Skill 间 file_id 传参已实现（2026-04-10）

对应 AutoDNA 的 shelve 数据库 + file_id 传参机制。

- 新增 `skills/shared/scripts/autodna_store.py`：`write <skill>` / `read <skill>`
- 存储目录：`~/.openclaw/workspace/autodna_store/`
- 每个 Skill 输出后：① 一行 Python 写临时文件 → ② 调用 store.py write → ③ 返回 `File ID: xxx_latest`
- Orchestrator 传 file_id 而不是全文；接收方 Skill 的 Step 0 调用 store.py read
- 受影响 Skills：Protocol(写)、Reagent(写)、Code(读写)、Hardware(读写)、Hypothesis(读写)、Literature(写)

---

## 待办（优先级顺序）

1. **飞书端到端测试**：完整 RPA 流程（Orchestrator → 全链路）
2. **Reagent Agent 效果对比验证**（等 Gemini API Key 可用）
3. **Literature Agent 飞书测试**（需要 Gemini API Key 做 embedding）

---

## 关键路径：完整自动化流程（目标）

```
用户一句话 → Orchestrator
  → Protocol(INITIAL)       生成流程 + 试剂清单
  → Reagent                 验证库存
  → Protocol(ADJUSTMENT)    过滤不可用步骤
  → Code                    生成自动化脚本
  [实验失败时]
  → Hypothesis              生成优化假设
  → Protocol(OPTIMIZING)    修改流程
  → Code                    重新生成脚本
```

---

## 注册 Skill 快速命令

```bash
# 打包（需禁用沙箱）
python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  extensions/autodna/skills/<skill-name> /tmp/autodna-skills

# 更新已有 Skill 时先删旧文件
rm ~/.openclaw/extensions/<skill-name>.skill

# 安装
openclaw plugins install /tmp/autodna-skills/<skill-name>.skill
cd ~/.openclaw/workspace/skills && rm -rf <skill-name>
unzip -o /tmp/autodna-skills/<skill-name>.skill

# 清理 stale config + 重启
openclaw config unset plugins.entries.<skill-name>
openclaw gateway restart
```

详细踩坑记录见：`SKILL-REGISTRATION-GUIDE.md`
