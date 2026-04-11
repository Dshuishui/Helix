# AutoDNA ↔ OpenClaw 流程对比分析

> 目的：从具体例子出发，逐步对比两个平台从"收到用户需求"到"输出 protocol_flow.json"的完整流程。
> 用途：理论验证 + 端到端 debug 时快速定位问题。

---

## 一、简单任务（Simple Task）流程分析

### 示例实验

**用户输入**：
> "请用 RPA（Recombinase Polymerase Amplification）方法对 DNA 样品进行扩增，使用荧光检测确认扩增效果，目标扩增量为 2µg。"

**预期分类**：simple（单阶段，无需拆分子步骤）

---

### AutoDNA 完整流程

```
用户输入 (user_prompt_rpa.md)
│
├─ [Step A] main_routine()
│    ├─ get_experiment_type() → ExperimentType.RPA     ← CLI 参数 --rpa 决定
│    ├─ choose_toolset()      → [Protocol, Reagent, Code, Hardware]
│    │                                                  ← RPA 排除 Literature 和 Hypothesis
│    ├─ choose_system_prompt() → EPA_guidance_prompt    ← RPA 非 STORAGE，用自由 ReAct 提示
│    └─ planner_plan(user_prompt, system_prompt, toolset)
│
├─ [Step B] planner_plan() Phase 0：任务分析
│    ├─ summarize_task(prompt)
│    │    └─ plan_model → "RPA DNA Amplification with Fluorescence"
│    │    └─ 缓存到 output/stage-0/summarize_task_output.txt
│    │
│    └─ judge_task_complexity(experiment_name)
│         └─ plan_model → "simple"
│         └─ 缓存到 output/stage-0/judge_task_complexity_output.txt
│         └─ 判断为 simple → 直接进入单阶段执行，跳过 Stage 拆分
│
├─ [Step C] planner() Phase 1：单阶段 ReAct 执行
│    │
│    │  ★ ReAct 核心机制说明：
│    │    每次工具调用不是预先排好顺序的，而是"思考 → 行动 → 观察 → 再思考"的循环。
│    │    AI 每次看到工具返回的结果后，才决定下一步做什么。
│    │    这个循环由 LangGraph 驱动，AI 可以调用任意工具任意次，直到它认为任务完成。
│    │
│    ├─ create_my_react_agent(react_model, toolset, stage=1, prompt=EPA_guidance_prompt)
│    └─ graph.stream({"messages": [("user", user_prompt)]})
│
│         ════════════════ ReAct 循环开始 ════════════════
│
│         ┌─ [Reasoning 1] AI 收到用户需求，思考第一步
│         │    输入：用户 prompt（RPA 扩增需求）+ 可用工具列表
│         │    AI 推理：
│         │      "我需要先设计一个 RPA 实验方案，然后检查试剂可用性，
│         │       再生成代码执行。第一步应该调用 Protocol 工具生成初始方案，
│         │       因为没有任何已有方案，应该是 INITIAL 模式。"
│         │    → 决定调用 Protocol
│         │
│         ├─ [Action 1] Protocol(experiment_name="RPA amplification", file_ids=[])
│         │    ├─ choose_mode_by_LLM([]) → INITIAL（无历史 Protocol file_id）
│         │    ├─ prompt_generate_from_scratch → LLM 生成 Part/Step/Option 方案
│         │    └─ → file_id: "Protocol_abc123"
│         │
│         ├─ [Observation 1] AI 收到工具返回：
│         │    "已生成 RPA 实验方案，包含3个Part，使用了
│         │     RPA Kit、MgOAc Buffer 等试剂。
│         │     file_id: Protocol_abc123"
│         │
│         ├─ [Reasoning 2] AI 思考下一步
│         │    AI 推理：
│         │      "方案已生成，但我需要确认实验室里是否有这些试剂。
│         │       如果某些试剂不可用，方案需要调整。
│         │       → 调用 Reagent 工具检查库存可用性。"
│         │    → 决定调用 Reagent
│         │
│         ├─ [Action 2] Reagent(file_ids=["Protocol_abc123"])
│         │    ├─ 读取 Protocol_abc123 内容，提取 Reagent Check List
│         │    ├─ 查询本地 inventory（reagent_manager）
│         │    └─ → file_id: "Reagent_def456"
│         │         （结果：RPA Kit ✅，MgOAc ✅，Primer_A ❌ 不可用）
│         │
│         ├─ [Observation 2] AI 收到工具返回：
│         │    "Primer_A 不可用，其余试剂均可用。
│         │     file_id: Reagent_def456"
│         │
│         ├─ [Reasoning 3] AI 思考下一步
│         │    AI 推理：
│         │      "Primer_A 不可用，原方案中使用 Primer_A 的 Option 需要删除。
│         │       → 重新调用 Protocol，传入原方案 + 试剂检查结果，
│         │         让它过滤掉不可用的选项（ADJUSTMENT 模式）。"
│         │    → 决定再次调用 Protocol
│         │
│         ├─ [Action 3] Protocol(experiment_name, file_ids=["Protocol_abc123","Reagent_def456"])
│         │    ├─ choose_mode_by_LLM(file_ids) → ADJUSTMENT
│         │    │    （检测到同时有 Protocol + Reagent file_id）
│         │    ├─ prompt1：过滤 Primer_A 相关 Option
│         │    └─ → file_id: "Protocol_ghi789"（过滤后方案）
│         │
│         ├─ [Observation 3] AI 收到工具返回：
│         │    "方案已过滤，Primer_A 相关步骤已移除，
│         │     剩余步骤均可用现有试剂执行。
│         │     file_id: Protocol_ghi789"
│         │
│         ├─ [Reasoning 4] AI 思考下一步
│         │    AI 推理：
│         │      "实验方案已验证可行。下一步需要把这个方案
│         │       转换成自动化 Python 脚本，才能让硬件执行。
│         │       → 调用 Code 工具，输入验证后的方案。"
│         │    → 决定调用 Code
│         │
│         ├─ [Action 4] Code(code_request_id="Protocol_ghi789")
│         │    ├─ linearize_procedure() → 消歧多路径 → 单一 PATH
│         │    ├─ prompt_code_main → LLM 生成 Python 脚本
│         │    ├─ correct_and_execute_code()         ← ★ 纠错在 Code Agent 内
│         │    │    ├─ execute_code(corrector_path)  ← PYTHONPATH=executor/corrector/
│         │    │    ├─ 若 stderr → corrector() LLM 修正
│         │    │    └─ 最多 3 次
│         │    └─ → file_ids: ["Code_jkl012"]
│         │
│         ├─ [Observation 4] AI 收到工具返回：
│         │    "已生成可执行 Python 脚本，通过 corrector 验证无语法错误。
│         │     file_ids: Code_jkl012"
│         │
│         ├─ [Reasoning 5] AI 思考下一步
│         │    AI 推理：
│         │      "代码已生成并通过验证。现在需要在实验室硬件上执行，
│         │       获得实际实验结果。→ 调用 Hardware 工具执行。"
│         │    → 决定调用 Hardware
│         │
│         ├─ [Action 5] Hardware(file_ids=["Code_jkl012"], repeat_num=1)
│         │    ├─ execute_code_to_scheduler(["Code_jkl012"], scheduler_path, 1)
│         │    │    ├─ 运行脚本（PYTHONPATH=executor/scheduler/）
│         │    │    └─ → 生成 protocol_flow.json
│         │    ├─ [mock 模式] get_input_set() → 询问用户输入荧光计读数
│         │    └─ 返回实验结果摘要
│         │
│         ├─ [Observation 5] AI 收到工具返回：
│         │    "实验执行完成，protocol_flow.json 已生成，
│         │     荧光读数：Time=30min, Fluorescence=1250 RFU（用户输入）"
│         │
│         └─ [Reasoning 6] AI 判断任务是否完成
│               AI 推理：
│                 "Protocol 已生成 → 试剂已验证 → 代码已执行 → 结果已收集。
│                  实验目标（RPA 扩增 + 荧光检测）已完成，可以输出最终结果。"
│               → 停止循环，输出最终结果
│
│         ════════════════ ReAct 循环结束 ════════════════
│
│   AI 输出：
│   ### workflow ###
│   (Protocol INITIAL → Reagent → Protocol ADJUSTMENT → Code → Hardware)
│   ### final_result ###
│   (扩增成功，protocol_flow.json 已生成)
│
└─ [Step D] planner_plan() 简单任务提前返回
     └─ 直接 return final_message.content（无 Phase 2 判断，无 complete_routine）
```

**为什么是这个顺序？**

| 顺序 | 原因 |
|------|------|
| Protocol → Reagent | 必须先有方案，才能知道需要检查哪些试剂 |
| Reagent → Protocol(ADJUSTMENT) | 必须先有试剂可用性信息，才能过滤方案 |
| Protocol(ADJUSTMENT) → Code | 必须先有验证过的方案，才能生成可执行代码 |
| Code → Hardware | 必须先有可运行脚本，才能执行实验 |
| 纠错在 Code 内 | Code 生成后立即用 corrector mock 验证，确保交给 Hardware 的代码可运行 |

---

### OpenClaw 完整流程

```
用户消息（飞书 → autodna-orchestrator）
│
├─ [Step A] Phase 0：任务分析（固定顺序执行）
│    │
│    ├─ Step 0a: summarize_task.py "<user_prompt>"
│    │    └─ Gemini API → "RPA DNA Amplification with Fluorescence"
│    │    └─ 缓存到 ~/.openclaw/workspace/autodna_store/plan_experiment_name.txt
│    │
│    ├─ Step 0b: detect_experiment_type.py "<user_prompt>"
│    │    └─ Gemini API → "rpa"
│    │    └─ 缓存到 autodna_store/plan_experiment_type.txt
│    │    └─ 确定：Mode A（自由 ReAct），可用 Skills：Protocol/Reagent/Code/Hardware
│    │
│    ├─ Step 0c: judge_complexity.py "<experiment_name>"
│    │    └─ Gemini API → "simple"
│    │    └─ 缓存到 autodna_store/plan_complexity.txt
│    │    └─ simple → 跳过 Step 0d（无需拆分 Stage）
│    │
│    └─ Step 0e: 跳过（非 storage_read）
│
├─ [Step B] Phase 1：单 Stage 执行（Mode A，自由 ReAct）
│    │
│    │  ★ ReAct 核心机制说明：
│    │    Orchestrator LLM 本身就是 ReAct 的执行者。
│    │    它每次调用一个 Skill，等待返回结果，再根据结果决定下一步。
│    │    OpenClaw 中 Skill 的调用顺序和 AutoDNA 中 Tool 的调用顺序，
│    │    由同一个科学逻辑驱动，因此期望是一致的。
│    │
│    ════════════════ ReAct 循环开始 ════════════════
│
│    ┌─ [Reasoning 1] Orchestrator LLM 收到用户需求，思考第一步
│    │    输入：用户 prompt（RPA 扩增需求）+ SKILL.md 指导
│    │    AI 推理：
│    │      "用户需要做 RPA 扩增实验。我需要：
│    │       1. 先生成实验方案（Protocol INITIAL）
│    │       2. 再检查试剂可用性（Reagent）
│    │       3. 根据试剂过滤方案（Protocol ADJUSTMENT）
│    │       4. 生成代码（Code）
│    │       5. 执行实验（Hardware）
│    │       现在没有任何已有方案，第一步调用 protocol-agent。"
│    │    → 决定调用 protocol-agent
│    │
│    ├─ [Action 1] [Invoking: protocol-agent]
│    │    ├─ Orchestrator 发送完整用户需求
│    │    ├─ protocol-agent 判断模式 → INITIAL（无历史 protocol）
│    │    ├─ 生成 Part/Step/Option 格式方案
│    │    ├─ autodna_store.py write protocol
│    │    └─ 返回 "File ID: protocol_latest"
│    │
│    ├─ [Observation 1] Orchestrator 收到返回：
│    │    "已生成 RPA 实验方案，含 Primer_A、RPA Kit 等试剂。
│    │     File ID: protocol_latest"
│    │
│    ├─ [Reasoning 2] Orchestrator 思考下一步
│    │    AI 推理：
│    │      "方案已有，但不知道实验室里是否有这些试剂。
│    │       如果 Primer_A 之类的试剂没有，方案需要调整。
│    │       → 调用 reagent-agent 检查库存。"
│    │    → 决定调用 reagent-agent
│    │
│    ├─ [Action 2] [Invoking: reagent-agent]
│    │    ├─ 传入 [File ID: protocol_latest]
│    │    ├─ reagent-agent 提取 Reagent Check List，查询库存
│    │    ├─ autodna_store.py write reagent
│    │    └─ 返回 "File ID: reagent_latest"
│    │         （结果：RPA Kit ✅，MgOAc ✅，Primer_A ❌）
│    │
│    ├─ [Observation 2] Orchestrator 收到返回：
│    │    "Primer_A 不可用，其余试剂均可用。
│    │     File ID: reagent_latest"
│    │
│    ├─ [Reasoning 3] Orchestrator 思考下一步
│    │    AI 推理：
│    │      "Primer_A 不可用，需要把原方案中用到 Primer_A 的步骤删掉。
│    │       → 再次调用 protocol-agent，传入原方案 + 试剂结果，
│    │         让它做 ADJUSTMENT 过滤。"
│    │    → 决定再次调用 protocol-agent
│    │
│    ├─ [Action 3] [Invoking: protocol-agent]
│    │    ├─ 传入 [File ID: protocol_latest] + [File ID: reagent_latest]
│    │    ├─ protocol-agent 判断模式 → ADJUSTMENT
│    │    ├─ 过滤 Primer_A 相关 Option
│    │    ├─ autodna_store.py write protocol（覆盖更新）
│    │    └─ 返回 "File ID: protocol_latest"（已更新）
│    │
│    ├─ [Observation 3] Orchestrator 收到返回：
│    │    "方案已过滤，Primer_A 步骤移除，剩余步骤可执行。
│    │     File ID: protocol_latest"
│    │
│    ├─ [Reasoning 4] Orchestrator 思考下一步
│    │    AI 推理：
│    │      "方案已验证，现在需要转换成自动化 Python 脚本。
│    │       → 调用 code-agent，传入验证后的方案。"
│    │    → 决定调用 code-agent
│    │
│    ├─ [Action 4] [Invoking: code-agent]
│    │    ├─ 传入 [File ID: protocol_latest] + [File ID: reagent_latest]
│    │    ├─ Step 0a: autodna_store.py read protocol
│    │    ├─ Step 0b: 预检查仪器兼容性
│    │    ├─ Step 1: 线性化 → ### PATH START ### 格式
│    │    ├─ Step 2: 生成 ## SCRIPT START ## Python 脚本
│    │    ├─ autodna_store.py write code
│    │    └─ 返回 "File ID: code_latest"
│    │         ★ 注意：code-agent 不做纠错，只生成代码
│    │
│    ├─ [Observation 4] Orchestrator 收到返回：
│    │    "Python 脚本已生成，含 lab_modules API 调用。
│    │     File ID: code_latest"
│    │
│    ├─ [Reasoning 5] Orchestrator 思考下一步
│    │    AI 推理：
│    │      "脚本已生成。下一步需要在硬件上执行，
│    │       获得实际实验结果（protocol_flow.json）。
│    │       → 调用 hardware-agent。"
│    │    → 决定调用 hardware-agent
│    │
│    ├─ [Action 5] [Invoking: hardware-agent]
│    │    ├─ 传入 [File ID: code_latest]
│    │    ├─ Step 0: autodna_store.py read code
│    │    ├─ Step 1: run_experiment.py
│    │    │    ├─ Phase 1 纠错循环：            ← ★ 纠错在 Hardware Agent 内
│    │    │    │    ├─ CORRECTOR_DIR PYTHONPATH
│    │    │    │    ├─ 若有 stderr → Gemini LLM 修正
│    │    │    │    └─ 最多 3 次
│    │    │    └─ Phase 2 执行：SCHEDULER_DIR → protocol_flow.json
│    │    ├─ Step 2: 解析 protocol_flow.json，输出结果摘要
│    │    ├─ autodna_store.py write hardware
│    │    └─ 返回 "File ID: hardware_latest"
│    │
│    ├─ [Observation 5] Orchestrator 收到返回：
│    │    "实验执行完成，protocol_flow.json 已生成，
│    │     荧光读数 mock 值 -1（真实硬件时为实际读数）"
│    │
│    └─ [Reasoning 6] Orchestrator 判断任务是否完成
│          AI 推理：
│            "Protocol ✅ → Reagent ✅ → Protocol ADJUSTMENT ✅
│             → Code ✅ → Hardware ✅。
│             实验目标已完成，输出最终结果。"
│          → 停止循环
│
│    ════════════════ ReAct 循环结束 ════════════════
│
│   Orchestrator 输出：
│   ### stage_complete ###
│   Stage 1: RPA DNA Amplification
│   (结果摘要)
│
└─ [Step C] Phase 2：整体判断
     ├─ judge_success.py "<user_goal>" 1
     └─ {"success": true} → 输出 ### workflow ### 和 ### final_result ###
```

**为什么是这个顺序？**

与 AutoDNA 完全相同的科学逻辑，见上表。Orchestrator LLM 根据 SKILL.md 的指导和科学常识做出相同判断。

---

### 简单任务：AutoDNA vs OpenClaw 对比

| 步骤 | AutoDNA | OpenClaw | 一致？ |
|------|---------|---------|--------|
| 实验类型检测 | CLI 参数 `--rpa` | `detect_experiment_type.py` LLM 分类 | ✅ 等价 |
| Toolset 选择 | `choose_toolset()` 排除 Lit/Hyp | SKILL.md 明确排除 | ✅ 相同 |
| System prompt | `EPA_guidance_prompt`（5行，极简）| SKILL.md（详细步骤指导）| ✅ 行为等价，指导更详细 |
| 任务摘要 | `summarize_task()` | `summarize_task.py` | ✅ 相同 |
| 复杂度判断 | `judge_task_complexity()` | `judge_complexity.py` | ✅ 相同 |
| ReAct 循环 | LangGraph `create_my_react_agent` | Orchestrator LLM `[Invoking: ...]` | ✅ 等价 |
| Protocol 模式检测 | `choose_mode_by_LLM(file_ids)` 查历史 | protocol-agent 读消息上下文 | ✅ 等价 |
| 代码纠错时机 | **Code Agent 内部** | **Hardware Agent 内部** | ✅ 结果相同，位置不同 |
| 试剂可用性输入 | 交互式 `input()` | 读 `protocol_flow.json` | ⚠️ Mock 设计差异 |
| Phase 2 判断 | simple 任务**跳过** | 总是运行 `judge_success.py` | ⚠️ 多一步，无害 |
| `protocol_flow.json` 生成 | `executor/scheduler/` PYTHONPATH | `run_experiment.py` Phase 2 同路径 | ✅ 完全相同 |

**差异总结（简单任务）：**

1. **代码纠错位置**：AutoDNA 在 Code Agent 内，OpenClaw 在 Hardware Agent 内。结果相同。
2. **Mock 结果收集**：AutoDNA 需要用户手动输入荧光读数；OpenClaw 直接读 protocol_flow.json（-1 mock 值）。真实硬件时两者行为趋同。
3. **Phase 2 多余判断**：OpenClaw 对 simple 任务多跑一次 judge_success，AutoDNA 跳过。无害。

---

## 二、复杂任务（Complex Task）流程分析

### 示例实验

**用户输入**：
> "请将字符串 'HELLO' 编码并写入 DNA 分子进行存储，要求完成 DNA 序列设计、寡核苷酸合成和 DNA 扩增验证三个步骤，扩增使用 PCR 方法，验证荧光阈值 > 500 RFU。"

**预期分类**：complex（三个性质不同的子实验）、experiment_type = storage_write

---

### AutoDNA 完整流程（复杂任务）

```
用户输入 (user_prompt_write.md)
│
├─ [Step A] main_routine()
│    ├─ get_experiment_type() → ExperimentType.WRITE   ← CLI 参数 --write
│    ├─ choose_toolset()      → [全部6个工具]           ← WRITE 包含 Literature 和 Hypothesis
│    ├─ choose_system_prompt() → EPA_guidance_prompt    ← ★ WRITE 返回自由 ReAct（不是 storage prompt）
│    └─ planner_plan(user_prompt, system_prompt, toolset)
│
├─ [Step B] planner_plan() Phase 0：任务分析
│    │
│    ├─ summarize_task(prompt)
│    │    └─ plan_model → "DNA Storage Write with PCR Verification"
│    │    └─ 缓存到 output/stage-0/summarize_task_output.txt
│    │
│    ├─ judge_task_complexity(experiment_name)
│    │    └─ plan_model → "complex"（三个性质不同的子实验）
│    │    └─ 缓存到 output/stage-0/judge_task_complexity_output.txt
│    │
│    ├─ [settings.read = False，跳过 write_summary 加载]
│    │
│    └─ 生成结构化 Stage 计划（plan_system_prompt + prompt → plan_model）
│         └─ 输出 JSON：
│              [
│                {"name": "DNA Sequence Design and Encoding",
│                 "user_requirement": "encode 'HELLO', use standard DNA encoding scheme"},
│                {"name": "DNA Oligo Synthesis",
│                 "user_requirement": ""},
│                {"name": "DNA PCR Amplification and Verification",
│                 "user_requirement": "fluorescence threshold > 500 RFU"}
│              ]
│         └─ 缓存到 output/stage-0/decompose_task_output.json
│
│
├─ [Step C] planner_plan() Phase 1：逐 Stage 执行
│    │
│    │  ══════════════════════════════════════════════
│    │  Stage 1: DNA Sequence Design and Encoding
│    │  ══════════════════════════════════════════════
│    │
│    ├─ i=0，Stage 1，跳过 requirement 继承检查（无前序 Stage）
│    ├─ judge_relevant_stages(stage_1, history=[], ...) → []（无历史）
│    ├─ 构建 Stage 1 prompt：
│    │    """
│    │    Current Stage Goal: DNA Sequence Design and Encoding
│    │    ---
│    │    Requirement for this stage: encode 'HELLO', use standard DNA encoding scheme
│    │    ---
│    │    Original user request: [原始完整 prompt]
│    │    Please focus ONLY on executing this current stage.
│    │    """
│    │
│    ├─ [planner(stage_1_prompt, EPA_guidance_prompt, toolset, stage=1)]
│    │    │
│    │    │  ════ Stage 1 ReAct 循环 ════
│    │    │
│    │    ├─ [Reasoning 1] AI 思考：
│    │    │    "需要设计 DNA 序列编码 'HELLO'，查询文献是否有标准编码方案"
│    │    │    → 调用 Literature
│    │    │
│    │    ├─ [Action] Literature(question="What is the standard scheme for encoding text into DNA?")
│    │    │    └─ 搜索本地论文库 → 返回编码方案文献摘要 → file_id: "Literature_lit001"
│    │    │
│    │    ├─ [Reasoning 2] AI 思考：
│    │    │    "有了编码方案，生成 'HELLO' 对应的 DNA 序列设计 Protocol"
│    │    │    → 调用 Protocol (INITIAL)
│    │    │
│    │    ├─ [Action] Protocol(experiment_name, file_ids=["Literature_lit001"])
│    │    │    └─ INITIAL 模式，生成序列设计方案 → file_id: "Protocol_p001"
│    │    │
│    │    ├─ [Reasoning 3] AI 思考：
│    │    │    "方案完成，Stage 1 目标已达成（序列设计，不需要硬件执行）"
│    │    │    → 输出 ### final_result ###
│    │    │
│    │    └─ 返回 final_message（含 ### final_result ###）
│    │
│    ├─ 提取 final_result → previous_stage_output_content
│    ├─ stage_history.append({stage_num:1, stage_name:"DNA Sequence Design", output:...})
│    ├─ CoflowCache 记录 best_protocol → stage_protocols[0] = "Protocol_p001"
│    └─ 缓存 output/coflow_cache/stage-1_cache.md
│
│    │  ══════════════════════════════════════════════
│    │  Stage 2: DNA Oligo Synthesis
│    │  ══════════════════════════════════════════════
│    │
│    ├─ i=1，Stage 2
│    │
│    ├─ [requirement 继承检查]
│    │    judge_requirement_relevance(
│    │      current="DNA Oligo Synthesis",
│    │      prev="DNA Sequence Design and Encoding",
│    │      prev_req="encode 'HELLO'...",
│    │      prev_result=stage_1_output
│    │    )
│    │    → plan_model → "YES"（序列设计的 requirement 对合成阶段仍有约束）
│    │    → user_requirement = "" + " encode 'HELLO'..."（继承拼接）
│    │
│    ├─ judge_relevant_stages("DNA Oligo Synthesis", history=[stage1], stage_num=2, ...)
│    │    → plan_model → [1]（Stage 1 的输出是合成的直接输入：DNA 序列）
│    │
│    ├─ 构建 Stage 2 prompt：
│    │    """
│    │    Result from Stage 1: DNA Sequence Design and Encoding
│    │    [Stage 1 的完整输出内容]
│    │    ---
│    │    Current Stage Goal: DNA Oligo Synthesis
│    │    ---
│    │    Requirement for this stage: encode 'HELLO'...（继承）
│    │    ---
│    │    Please focus ONLY on executing this current stage.
│    │    """
│    │
│    ├─ [planner(stage_2_prompt, EPA_guidance_prompt, toolset, stage=2)]
│    │    │
│    │    │  ════ Stage 2 ReAct 循环 ════
│    │    │
│    │    ├─ [Reasoning 1] AI 思考：
│    │    │    "有了 Stage 1 的序列设计，需要生成合成 Protocol，
│    │    │     然后检查试剂，再生成代码，执行合成"
│    │    │    → 调用 Protocol (INITIAL)
│    │    │
│    │    ├─ [Action] Protocol(file_ids=["Protocol_p001"的内容注入])
│    │    │    └─ INITIAL，基于序列设计生成合成方案 → file_id: "Protocol_p002"
│    │    │
│    │    ├─ [Reasoning 2] 检查试剂 → [Action] Reagent → [Observation] 试剂全部可用
│    │    │
│    │    ├─ [Reasoning 3] 生成代码 → [Action] Code → [Observation] code 已生成
│    │    │
│    │    ├─ [Reasoning 4] 执行 → [Action] Hardware
│    │    │    └─ run_experiment.py → protocol_flow.json（合成步骤）
│    │    │
│    │    ├─ [Reasoning 5] AI 思考：
│    │    │    "合成完成，Stage 2 目标达成"
│    │    │    → 输出 ### final_result ###
│    │    │
│    │    └─ 返回 final_message
│    │
│    ├─ stage_history.append({stage_num:2, ...})
│    ├─ CoflowCache 更新 → stage_protocols[1] = "Protocol_p002"
│    └─ 缓存 stage-2_cache.md
│
│    │  ══════════════════════════════════════════════
│    │  Stage 3: DNA PCR Amplification and Verification
│    │  ══════════════════════════════════════════════
│    │
│    ├─ i=2，Stage 3
│    │
│    ├─ [requirement 继承检查]
│    │    judge_requirement_relevance(
│    │      current="DNA PCR Amplification and Verification",
│    │      prev="DNA Oligo Synthesis",
│    │      prev_req="encode 'HELLO'...",（Stage 2 继承来的）
│    │    )
│    │    → "NO"（HELLO 编码约束对 PCR 验证无约束）
│    │    → user_requirement = "fluorescence threshold > 500 RFU"（保持原值）
│    │
│    ├─ judge_relevant_stages("DNA PCR Amplification", history=[stage1,stage2], stage_num=3, ...)
│    │    → [2]（Stage 2 合成的产物是 PCR 的输入）
│    │
│    ├─ 构建 Stage 3 prompt：
│    │    """
│    │    Result from Stage 2: DNA Oligo Synthesis
│    │    [Stage 2 完整输出]
│    │    ---
│    │    Current Stage Goal: DNA PCR Amplification and Verification
│    │    ---
│    │    Requirement for this stage: fluorescence threshold > 500 RFU
│    │    ---
│    │    Please focus ONLY on executing this current stage.
│    │    """
│    │
│    └─ [planner(stage_3_prompt, EPA_guidance_prompt, toolset, stage=3)]
│         │
│         │  ════ Stage 3 ReAct 循环 ════
│         │
│         ├─ Protocol(INITIAL) → Reagent → Protocol(ADJUSTMENT) → Code → Hardware
│         │    └─ Hardware 执行 → protocol_flow.json（PCR 步骤）
│         │
│         ├─ [mock] 用户输入荧光读数 400 RFU（< 500 阈值，实验失败）
│         │
│         ├─ [Reasoning] AI 思考：
│         │    "荧光值 400 RFU < 500 RFU，未达标。
│         │     → 调用 Hypothesis Agent 分析失败原因"
│         │    → 调用 Hypothesis
│         │
│         ├─ [Action] Hypothesis(file_ids=["Protocol_latest","Hardware_latest"])
│         │    └─ 生成假设：引物浓度过低 → file_id: "Hypothesis_h001"
│         │
│         ├─ [Reasoning] "根据假设优化方案"
│         │    → Protocol(OPTIMIZING, file_ids=["Protocol_latest","Hypothesis_h001"])
│         │    → Code → Hardware（重试，最多2次）
│         │
│         └─ [Reasoning 最终] "荧光 620 RFU > 500 ✅，Stage 3 完成"
│              → 输出 ### final_result ###
│
│
├─ [Step D] planner_plan() Phase 2：整体成功判断 + 重试
│    │
│    ├─ judge_experiment_success(previous_stage_output, initial_prompt)
│    │    └─ plan_model → "YES"（三个 Stage 均完成，荧光验证通过）
│    │
│    └─ complete_routine()                              ← ★ 仅 settings.write 时保存 summary
│         ├─ 读取 stage_protocols = ["Protocol_p001", "Protocol_p002", "Protocol_p003"]
│         ├─ 拼接所有 Stage 的 Protocol 内容
│         ├─ plan_model → 摘要：产物特性、编码信息、存储条件
│         └─ 写入 input/final_write_summary.md（供后续 Read 实验使用）
```

---

### OpenClaw 完整流程（复杂任务）

```
用户消息（飞书 → autodna-orchestrator）
│
├─ [Step A] Phase 0：任务分析（固定顺序执行）
│    │
│    ├─ summarize_task.py → "DNA Storage Write with PCR Verification"
│    │    └─ 缓存到 autodna_store/plan_experiment_name.txt
│    │
│    ├─ detect_experiment_type.py → "storage_write"
│    │    └─ 确定：Mode B（严格逐步），全部6个Skills，最后运行 complete_routine
│    │
│    ├─ judge_complexity.py → "complex"
│    │
│    └─ decompose_stages.py "<user_prompt>"
│         └─ Gemini → JSON：
│              [
│                {"name": "DNA Sequence Design and Encoding",
│                 "user_requirement": "encode 'HELLO', standard DNA encoding"},
│                {"name": "DNA Oligo Synthesis",
│                 "user_requirement": ""},
│                {"name": "DNA PCR Amplification and Verification",
│                 "user_requirement": "fluorescence threshold > 500 RFU"}
│              ]
│         └─ 缓存到 autodna_store/plan_stages.json
│         └─ Orchestrator 宣告：
│              "Task decomposed into 3 stages: [Stage 1: ..., Stage 2: ..., Stage 3: ...]"
│
│
├─ [Step B] Phase 1：逐 Stage 执行
│    │
│    │  ══════════════════════════════════════════════
│    │  Stage 1: DNA Sequence Design and Encoding
│    │  ══════════════════════════════════════════════
│    │
│    ├─ Step 1a: 跳过（无历史）
│    │
│    ├─ Step 1b: 构建 Stage 1 prompt（同 AutoDNA 结构）
│    │
│    ├─ Step 1c: Mode B 执行（storage_write → 严格逐步）
│    │    │
│    │    │  ════ Stage 1 ReAct 循环（Mode B）════
│    │    │
│    │    ├─ [Reasoning 1] Orchestrator 思考：
│    │    │    "Stage 1 目标是序列设计，先查文献获取编码方案"
│    │    │    → 调用 literature-agent
│    │    │
│    │    ├─ [Action 1] [Invoking: literature-agent]
│    │    │    └─ 返回 DNA 编码方案文献 → File ID: literature_latest
│    │    │
│    │    ├─ [Observation 1] 收到文献内容
│    │    │
│    │    ├─ [Reasoning 2] "有了编码方案，生成序列设计 Protocol"
│    │    │    → 调用 protocol-agent (INITIAL)
│    │    │
│    │    ├─ [Action 2] [Invoking: protocol-agent]
│    │    │    ├─ 传入 [File ID: literature_latest]
│    │    │    ├─ INITIAL 模式，生成序列设计方案
│    │    │    └─ 返回 File ID: protocol_latest
│    │    │
│    │    ├─ [Reasoning 3] "Stage 1 仅需序列设计，无需硬件执行，完成"
│    │    │    → 输出 ### stage_complete ###
│    │    │
│    │    └─ ════ Stage 1 ReAct 结束 ════
│    │
│    ├─ Step 1d: 保存 Stage 1 输出
│    │    ├─ autodna_store.py write stage_1_output
│    │    └─ ★ storage_write 备份 protocol：
│    │         cp protocol_latest.txt → protocol_stage_1_latest.txt
│    │
│    │  ══════════════════════════════════════════════
│    │  Stage 2: DNA Oligo Synthesis
│    │  ══════════════════════════════════════════════
│    │
│    ├─ Step 1a: 历史上下文判断
│    │    │
│    │    ├─ judge_requirement_relevance.py 2 "DNA Sequence Design" "encode 'HELLO'..." "DNA Oligo Synthesis"
│    │    │    → "yes" → user_requirement 继承 "encode 'HELLO'..."
│    │    │
│    │    └─ judge_relevant_stages.py 2 "DNA Oligo Synthesis" "<initial_goal>"
│    │         → [1] → 读取 stage_1_output 作为上下文
│    │
│    ├─ Step 1b: 构建 Stage 2 prompt（注入 Stage 1 输出 + 继承的 requirement）
│    │
│    ├─ Step 1c: Mode B 执行
│    │    │
│    │    │  ════ Stage 2 ReAct 循环（Mode B）════
│    │    │
│    │    ├─ [Reasoning 1] "合成需要先有 Protocol"
│    │    │    → [Action] protocol-agent (INITIAL，基于Stage1输出)
│    │    │
│    │    ├─ [Reasoning 2] "检查试剂"
│    │    │    → [Action] reagent-agent
│    │    │
│    │    ├─ [Reasoning 3] "过滤方案"
│    │    │    → [Action] protocol-agent (ADJUSTMENT)
│    │    │
│    │    ├─ [Reasoning 4] "生成代码"
│    │    │    → [Action] code-agent
│    │    │
│    │    ├─ [Reasoning 5] "执行实验"
│    │    │    → [Action] hardware-agent
│    │    │         └─ run_experiment.py → protocol_flow.json（合成步骤）
│    │    │
│    │    └─ [Reasoning 6] "合成完成" → ### stage_complete ###
│    │
│    ├─ Step 1d: 保存 Stage 2 输出
│    │    ├─ autodna_store.py write stage_2_output
│    │    └─ cp protocol_latest.txt → protocol_stage_2_latest.txt
│    │
│    │  ══════════════════════════════════════════════
│    │  Stage 3: DNA PCR Amplification and Verification
│    │  ══════════════════════════════════════════════
│    │
│    ├─ Step 1a: 历史上下文判断
│    │    ├─ judge_requirement_relevance.py 3 "DNA Oligo Synthesis" "encode 'HELLO'..." "DNA PCR..."
│    │    │    → "no" → user_requirement 不继承，保持 "fluorescence > 500 RFU"
│    │    └─ judge_relevant_stages.py 3 "DNA PCR..." "<goal>" → [2]
│    │         → 读取 stage_2_output 作为上下文
│    │
│    ├─ Step 1b: 构建 Stage 3 prompt
│    │
│    ├─ Step 1c: Mode B 执行
│    │    │
│    │    │  ════ Stage 3 ReAct 循环（Mode B）════
│    │    │
│    │    ├─ Protocol(INITIAL) → Reagent → Protocol(ADJUSTMENT) → Code → Hardware
│    │    │    └─ protocol_flow.json（PCR 步骤），荧光 mock 值 = -1
│    │    │
│    │    ├─ [Reasoning] "mock 模式荧光值 -1，无法判断阈值，
│    │    │               Hardware 报告实验结果待验证"
│    │    │    ← 注意：OpenClaw 无交互式输入，读 protocol_flow.json
│    │    │
│    │    └─ [Reasoning] "Stage 3 执行完毕" → ### stage_complete ###
│    │
│    └─ Step 1d: 保存 Stage 3 输出 + 备份 protocol_stage_3_latest.txt
│
│
└─ [Step C] Phase 2：整体判断 + complete_routine
     │
     ├─ judge_success.py "<user_goal>" 3
     │    ├─ 读取 stage_1/2/3_output_latest.txt
     │    ├─ Gemini → "YES"（三个 Stage 均完成）
     │    └─ {"success": true}
     │
     └─ complete_routine.py 3                    ← ★ storage_write 专属
          ├─ 读取 protocol_stage_1/2/3_latest.txt
          ├─ Gemini 摘要：产物特性、编码信息、存储条件
          ├─ autodna_store.py write write_summary
          └─ 返回 [STORED: write_summary_latest]
               （供后续 Read 实验用 Step 0e 加载）
```

---

### 复杂任务：AutoDNA vs OpenClaw 对比

| 步骤 | AutoDNA | OpenClaw | 一致？ |
|------|---------|---------|--------|
| Stage 拆分 | `plan_system_prompt` + `plan_model` → JSON | `decompose_stages.py` 同样 prompt → JSON | ✅ 相同 |
| Stage 间上下文 | `judge_relevant_stages()` → 读 stage_history | `judge_relevant_stages.py` → 读 autodna_store | ✅ 相同 |
| Requirement 继承 | `judge_requirement_relevance()` | `judge_requirement_relevance.py` | ✅ 相同 |
| Stage prompt 构建 | 历史上下文 + Goal + Requirement + 原始 prompt | 同样结构（Step 1b） | ✅ 相同 |
| Stage 内 ReAct | `planner()` LangGraph，EPA_guidance_prompt（自由）| Mode A（自由 ReAct）| ✅ 已对齐 |
| Protocol 备份 | `CoflowCache` 记录 best_protocol，`stage_protocols[]` | `cp protocol_latest → protocol_stage_N_latest` | ✅ 等价 |
| 成功判断 | `judge_experiment_success()` + 重试最多2次 | `judge_success.py` + 重试最多2次 | ✅ 相同 |
| complete_routine | `settings.write` 时执行，读 `stage_protocols` | `storage_write` 时执行，读 `protocol_stage_N_latest` | ✅ 相同 |
| write_summary 保存 | `input/final_write_summary.md` | `autodna_store/write_summary_latest.txt` | ✅ 等价 |
| storage_read 加载 | `settings.read` 时读 FINAL_WRITE_SUMMARY | Step 0e 读 `write_summary_latest` 注入 prompt | ✅ 相同 |

**差异总结（复杂任务）：**

1. **Stage 内 ReAct 模式**：已对齐。storage_write 和 storage_read 均已改为 Mode A（自由 ReAct），与 AutoDNA EPA_guidance_prompt 行为一致。

2. **mock 荧光读数**：AutoDNA 交互式输入，OpenClaw 读 -1（mock），不影响 protocol_flow.json 的步骤内容。

3. **Stage 1 无硬件执行**：两边均可能出现（AI 判断序列设计阶段不需要 Hardware），行为一致。

---

## 三、Debug 参考：问题定位指南

当端到端运行出现问题时，按以下顺序排查：

| 阶段 | 现象 | 检查位置 |
|------|------|---------|
| Phase 0 | 实验类型识别错误 | `autodna_store/plan_experiment_type.txt` |
| Phase 0 | 复杂度判断错误 | `autodna_store/plan_complexity.txt` |
| Protocol INITIAL | 生成的方案不合理 | `autodna_store/protocol_latest.txt` |
| Protocol ADJUSTMENT | 试剂过滤结果错误 | `autodna_store/reagent_latest.txt` + `protocol_latest.txt` |
| Code | 生成代码语法错误 | `autodna_store/code_latest.txt` |
| Hardware Phase 1 | 纠错失败 | `run_experiment.py` stderr 输出 |
| Hardware Phase 2 | protocol_flow.json 未生成 | `executor/scheduler/protocol_flow.json` 是否存在 |
| Phase 2 | 成功判断错误 | `autodna_store/stage_1_output_latest.txt` |
