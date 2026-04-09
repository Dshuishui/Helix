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

对应 AutoDNA `ai_scientist.py` 中的 `planner_plan()` 函数（1124 行）。

**当前版本：RPA happy path**
- Stage 1: Protocol(INITIAL) → Stage 2: Reagent → Stage 3: Protocol(ADJUSTMENT，按需) → Stage 4: Code
- 实验失败后手动触发：Hypothesis → Protocol(OPTIMIZING) → Code
- 上下文传递：通过对话历史自动流转，无需用户 copy-paste

**简化项（与原始 AutoDNA 相比）：**
- 移除了 LangGraph ReAct 循环（用 Skill 直接调用替代）
- 移除了 file_id + Shelve 数据库（用对话上下文替代）
- 移除了 Hardware Agent 调用（暂缓）

### 后续扩展计划

**扩展到其他实验类型（PCR、NGS 等）**
- 难度：低。在 Orchestrator SKILL.md Step 1 加新分支，定义各类型的 Stage 序列
- 不影响现有 RPA 逻辑，纯追加

**添加自动重试逻辑**（对应 `planner_plan()` 的 retry loop）
- 难度：低。在 Stage 4 之后加 "成功判断" 步骤
- 失败时：Hypothesis → Protocol(OPTIMIZING) → Code（最多 2 次）
- 追踪 previous hypotheses 传给 Hypothesis Agent 避免重复
- 约 20 行追加到 SKILL.md，不需要重写

---

## 待办（优先级顺序）

1. **飞书验证 Orchestrator**：打包安装，端到端测试完整 RPA 流程
2. **Reagent Agent 效果对比验证**（等 Gemini API Key 可用）
3. **扩展 Orchestrator**：添加重试逻辑（见上方扩展计划）
4. Hardware Agent / Literature Agent（暂缓）

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
