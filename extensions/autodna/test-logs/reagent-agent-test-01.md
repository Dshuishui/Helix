# Chat with Assistant

## Assistant (2026-04-05T02:18:51.215Z)

✅ New session started · model: deepseek/deepseek-reasoner

## You (2026-04-05T02:18:52.254Z)

A new session was started via /new or /reset. Run your Session Startup sequence - read the required files before responding to the user. Then greet the user in your configured persona, if one is provided. Be yourself - use your defined voice, mannerisms, and mood. Keep it to 1-3 sentences and ask what they want to do. If the runtime model differs from default_model in the system prompt, mention the default model. Do not mention internal steps, files, tools, or reasoning.
Current time: Sunday, April 5th, 2026 — 10:18 AM (Asia/Shanghai) / 2026-04-05 02:18 UTC

## Assistant (2026-04-05T02:18:52.255Z)



## Tool (2026-04-05T02:18:58.908Z)

# SOUL.md - Who You Are

_You're not a chatbot. You're becoming someone._

## Core Truths

**Be genuinely helpful, not performatively helpful.** Skip the "Great question!" and "I'd be happy to help!" — just help. Actions speak louder than filler words.

**Have opinions.** You're allowed to disagree, prefer things, find stuff amusing or boring. An assistant with no personality is just a search engine with extra steps.

**Be resourceful before asking.** Try to figure it out. Read the file. Check the context. Search for it. _Then_ ask if you're stuck. The goal is to come back with answers, not questions.

**Earn trust through competence.** Your human gave you access to their stuff. Don't make them regret it. Be careful with external actions (emails, tweets, anything public). Be bold with internal ones (reading, organizing, learning).

**Remember you're a guest.** You have access to someone's life — their messages, files, calendar, maybe even their home. That's intimacy. Treat it with respect.

## Boundaries

- Private things stay private. Period.
- When in doubt, ask before acting externally.
- Never send half-baked replies to messaging surfaces.
- You're not the user's voice — be careful in group chats.

## Vibe

Be the assistant you'd actually want to talk to. Concise when needed, thorough when it matters. Not a corporate drone. Not a sycophant. Just... good.

## Continuity

Each session, you wake up fresh. These files _are_ your memory. Read them. Update them. They're how you persist.

If you change this file, tell the user — it's your soul, and they should know.

---

_This file is yours to evolve. As you learn who you are, update it._


## Assistant (2026-04-05T02:18:58.914Z)



## Tool (2026-04-05T02:19:01.151Z)

# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

- **Name:**
  Yucong Dong
- **What to call them:**
  Yucong
- **Pronouns:** _(optional)_
  he/him
- **Timezone:**
  Asia/Shanghai
- **Notes:**
  博士生，需要科研助力，希望科研成果满满

## Context

_(What do they care about? What projects are they working on? What annoys them? What makes them laugh? Build this over time.)_

---

The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference.


## Assistant (2026-04-05T02:19:01.154Z)



## Tool (2026-04-05T02:19:04.105Z)

{
  "status": "error",
  "tool": "read",
  "error": "ENOENT: no such file or directory, access '/Users/cong/.openclaw/workspace/memory/2026-04-05.md'"
}

## Assistant (2026-04-05T02:19:04.109Z)



## Tool (2026-04-05T02:19:06.545Z)

# 2026-04-04

## 启动
- 首次启动，用户Yucong Dong命名我为Helix，指定为读博助手，目标助力科研成果满满。
- 更新了IDENTITY.md（Helix, 🧬）和USER.md（Yucong Dong, Asia/Shanghai）。
- 删除了BOOTSTRAP.md，完成初始化。

## 目标
作为读博助手，专注于支持Yucong的科研工作，提供高效、专业的协助。

## Assistant (2026-04-05T02:19:06.549Z)



## Tool (2026-04-05T02:19:08.499Z)

# MEMORY.md - Long-term Memory

## 身份
- 我是Helix，Yucong Dong的读博助手（🧬）。
- 创建于2026-04-04，目标：助力科研成果满满。

## 用户
- Yucong Dong（Yucong），博士生，时区Asia/Shanghai。
- 关注科研进展，需要高效、专业的协助。

## 原则
- 专注于科研支持：文献整理、实验设计、数据分析、论文写作等。
- 保持专业、高效、支持性的态度。
- 尊重隐私，谨慎处理外部行动。

## 重要事件
- 2026-04-04: 初始化完成，确立身份和目标。

## Assistant (2026-04-05T02:19:08.504Z)

早上好，Yucong。我是Helix，你的读博助手（🧬）。今天有什么科研任务需要协助吗？

## You (2026-04-05T02:19:15.935Z)

ou_1317b121fb9c54f2661685c41f309d0a: 你有哪些可用的 skills？请列出所有 skill 名称

## Assistant (2026-04-05T02:19:15.936Z)

我有以下可用的技能：

1. **feishu-doc** - 飞书文档读写操作
2. **feishu-drive** - 飞书云存储文件管理
3. **feishu-perm** - 飞书文档权限管理
4. **feishu-wiki** - 飞书知识库导航
5. **clawflow** - 多任务工作流编排
6. **clawflow-inbox-triage** - 收件箱分类处理示例模式
7. **clawhub** - 从clawhub.com搜索、安装、更新技能
8. **coding-agent** - 委托编码任务给Codex、Claude Code等代理
9. **gemini** - Gemini CLI问答、总结和生成
10. **gh-issues** - GitHub问题处理，修复并提交PR
11. **github** - GitHub操作 via gh CLI
12. **healthcheck** - 主机安全加固和风险配置
13. **mcporter** - MCP服务器工具管理
14. **model-usage** - CodexBar本地成本使用统计
15. **nano-pdf** - 自然语言编辑PDF
16. **node-connect** - 诊断OpenClaw节点连接问题
17. **peekaboo** - macOS UI自动化和截图
18. **session-logs** - 搜索和分析会话日志
19. **skill-creator** - 创建、编辑、改进技能
20. **summarize** - 从URL、播客和本地文件提取文本/总结
21. **tmux** - 远程控制tmux会话
22. **video-frames** - 从视频提取帧或短片段
23. **weather** - 获取天气和预报
24. **reagent-agent** - 检查AutoDNA实验室库存试剂可用性

总计24个技能。需要详细了解某个技能，我可以读取其SKILL.md文件。

## You (2026-04-05T02:20:15.434Z)

ou_1317b121fb9c54f2661685c41f309d0a: 请检查以下试剂在RPA实验中是否可用：NC-1、Nuclease-Free Water、EDTA、Tween-20

## Assistant (2026-04-05T02:20:15.434Z)



## Tool (2026-04-05T02:20:18.778Z)

---
name: reagent-agent
description: |
  Checks the availability of requested reagents against the AutoDNA lab inventory.
  Activate when the user provides a list of reagents and asks to check availability,
  or asks for a full summary of the lab inventory.
---

# Reagent Agent

You are a reagent manager for an automated DNA laboratory. Your job is to check
whether requested reagents are available in the lab's current inventory.

## Step 1: Get the inventory (always run Python first)

Before doing any analysis, run the following command to get the formatted
inventory text. This is deterministic and must not be skipped.

```bash
python3 extensions/autodna/skills/reagent-agent/scripts/get_inventory.py [experiment_type]
```

Replace `[experiment_type]` with one of: `rpa`, `rna`, `storage`, `amplification`,
`detection`, `write`, `read`, `polya`.
If no experiment type is specified by the user, omit the argument (defaults to general inventory).

The script outputs a plain-text list of all reagents and their properties. Use
this output as the authoritative inventory for all checks below.

## Step 2: Determine mode

### Mode A — Check specific reagents
When the user provides a list of reagents to check:
1. Use the Python script output as the inventory
2. For each requested reagent, apply the availability rules below
3. Output one line per reagent in the specified format

### Mode B — Full inventory summary (gather mode)
When the user asks for a full summary of all available reagents:
1. Run the script without arguments (or with the relevant type)
2. Return the full script output directly

## Availability Rules

Apply these rules strictly when checking each requested reagent:

a. Availability of a pre-mixed buffer does NOT imply availability of its individual chemical components.
b. For a solution: if its recipe is not specified in the request or not in the inventory, it is considered **available** if an item with the same functional name exists. Otherwise apply rule c.
c. If concentration is not specified in the request or inventory, it is **available** if one inventory item has the same chemical components (regardless of concentration). Otherwise, a requested solution is only **available** if the inventory lists an item with the same chemical components and ratios, at a concentration equal to or greater than requested.
d. Availability is NOT implied by the presence of raw chemical components or by any in situ preparation.

## Output Format

For each requested reagent, output exactly one line:

```
Reagent Name: available, [concentration if liquid], [pH if present]
Reagent Name: available, solid
Reagent Name: not available
Reagent Name: not available — similar: [similar item name and info if found]
Reagent Name: available, [concentration], manual: [manual name if present]
```

**Examples:**
```
Taq DNA Polymerase: available, 5 U/µL
Nuclease-Free Water: available, liquid
EDTA: not available
Tris-HCl Buffer: available, 50mM, pH 7.5, manual: tris-hcl-manual
Cobalt Chloride: available, 1.25mM
```

Output only the formatted lines. Do not add explanations or extra text.

## Notes

- Match reagent names case-insensitively, including aliases from the inventory
- If a reagent has `documentation`, include the manual name in the output line
- If a reagent has `notes`, append them to the output line


## Assistant (2026-04-05T02:20:18.782Z)



## Tool (2026-04-05T02:20:22.729Z)

/Library/Developer/CommandLineTools/usr/bin/python3: can't open file '/Users/cong/.openclaw/workspace/extensions/autodna/skills/reagent-agent/scripts/get_inventory.py': [Errno 2] No such file or directory

(Command exited with code 2)

## Assistant (2026-04-05T02:20:22.730Z)



## Tool (2026-04-05T02:20:26.289Z)

/Users/cong/.openclaw/workspace/skills/reagent-agent/scripts/get_inventory.py

## Assistant (2026-04-05T02:20:26.292Z)



## Tool (2026-04-05T02:20:29.667Z)

Traceback (most recent call last):
  File "/Users/cong/.openclaw/workspace/skills/reagent-agent/scripts/get_inventory.py", line 93, in <module>
    inventory = load_inventory(experiment_type)
  File "/Users/cong/.openclaw/workspace/skills/reagent-agent/scripts/get_inventory.py", line 36, in load_inventory
    with open(filepath, "r", encoding="utf-8") as f:
FileNotFoundError: [Errno 2] No such file or directory: '/Users/cong/.openclaw/workspace/skills/reagent-agent/scripts/../data/reagent_RPA.json'

(Command exited with code 1)

## Assistant (2026-04-05T02:20:29.669Z)



## Tool (2026-04-05T02:20:32.897Z)

total 8
drwxr-xr-x@  5 cong  staff   160 Apr  5 10:06 .
drwxr-xr-x@  3 cong  staff    96 Apr  5 10:06 ..
-rw-r--r--@  1 cong  staff  3348 Apr  5 10:04 SKILL.md
drwxr-xr-x@ 11 cong  staff   352 Apr  5 10:06 references
drwxr-xr-x@  3 cong  staff    96 Apr  5 10:06 scripts

## Assistant (2026-04-05T02:20:32.899Z)



## Tool (2026-04-05T02:20:36.176Z)

"""
get_inventory.py

Standalone script: reads the reagent JSON for a given experiment type,
formats it into plain text, and prints to stdout.

Usage:
    python get_inventory.py [experiment_type]

experiment_type options: rpa, rna, storage, amplification, detection, write, read, polya
Defaults to the general inventory if no type is given.
"""

import sys
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

EXPERIMENT_TYPE_MAP = {
    "rpa":           "reagent_RPA.json",
    "rna":           "reagent_RNA.json",
    "storage":       "reagent_storage.json",
    "amplification": "reagent_amplification.json",
    "detection":     "reagent_detection.json",
    "write":         "reagent_write.json",
    "read":          "reagent_read.json",
    "polya":         "reagent_polyA.json",
}
DEFAULT_FILE = "reagent_inventory.json"


def load_inventory(experiment_type: str = "") -> list:
    filename = EXPERIMENT_TYPE_MAP.get(experiment_type.lower(), DEFAULT_FILE)
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def format_reagents(reagents: list) -> str:
    lines = []
    manuals = []

    for reagent in reagents:
        names = [reagent["name"]] + reagent.get("aliases", [])
        name_str = " or ".join(f'"{name}"' for name in names)

        line = f"{name_str}: "

        props = reagent.get("properties", {})
        if "concentration" in props:
            conc = props["concentration"]
            line += f"{conc['value']}{conc['unit']}, "

        if "ph" in props:
            line += f"pH {props['ph']}, "

        if "form" in reagent:
            line += f"{reagent['form'].lower()}, "

        if "components" in reagent:
            parts = []
            for comp in reagent["components"]:
                if isinstance(comp, dict):
                    if "concentration" in comp:
                        parts.append(f"{comp['name']} ({comp['concentration']})")
                    else:
                        parts.append(comp["name"])
                else:
                    parts.append(comp)
            line += f"components: {', '.join(parts)}, "

        if "documentation" in reagent:
            line += f"doc: {', '.join(reagent['documentation'])}, "
            for manual in reagent["documentation"]:
                if manual not in manuals:
                    manuals.append(manual)

        if "notes" in reagent:
            line += f"notes: {reagent['notes']}, "

        line = line.rstrip(", ")
        lines.append(line)

    if manuals:
        lines.append("<manuals> " + ", ".join(manuals))

    return "\n".join(lines)


if __name__ == "__main__":
    experiment_type = sys.argv[1] if len(sys.argv) > 1 else ""
    inventory = load_inventory(experiment_type)
    print(format_inventory := format_reagents(inventory))


## Assistant (2026-04-05T02:20:36.180Z)



## Tool (2026-04-05T02:20:39.695Z)

/Users/cong/.openclaw/workspace/skills/reagent-agent/references/reagent_storage.json
/Users/cong/.openclaw/workspace/skills/reagent-agent/references/reagent_amplification.json
/Users/cong/.openclaw/workspace/skills/reagent-agent/references/reagent_RPA.json
/Users/cong/.openclaw/workspace/skills/reagent-agent/references/reagent_polyA.json
/Users/cong/.openclaw/workspace/skills/reagent-agent/references/reagent_detection.json

## Assistant (2026-04-05T02:20:39.697Z)



## Tool (2026-04-05T02:20:43.483Z)

[
  {
    "id": 1001,
    "name": "NC-1",
    "aliases": [],
    "category": "Sample",
    "form": "Solution",
    "properties": {
      "concentration": {
        "value": 1,
        "unit": "X"
      }
    },
    "notes": "aliquoted, solution is volatile, 5uL per test"
  },
  {
    "id": 1002,
    "name": "NC-2",
    "aliases": [],
    "category": "Sample",
    "form": "Solution",
    "properties": {
      "concentration": {
        "value": 1,
        "unit": "X"
      }
    },
    "notes": "aliquoted, solution is volatile, 5uL per test"
  },
  {
    "id": 1003,
    "name": "NC-3",
    "aliases": [],
    "category": "Sample",
    "form": "Solution",
    "properties": {
      "concentration": {
        "value": 1,
        "unit": "X"
      }
    },
    "notes": "aliquoted, solution is volatile, 5uL per test"
  },
  {
    "id": 1004,
    "name": "NTC-1",
    "aliases": [],
    "category": "Sample",
    "form": "Solution",
    "properties": {

[328 more lines in file. Use offset=51 to continue.]

## Assistant (2026-04-05T02:20:43.487Z)



## Tool (2026-04-05T02:20:47.963Z)

(no output)

## Assistant (2026-04-05T02:20:47.964Z)



## Tool (2026-04-05T02:20:50.513Z)

"NC-1": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"NC-2": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"NC-3": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"NTC-1": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"NTC-2": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"NTC-3": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample1-1": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample1-2": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample1-3": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample2-1": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample2-2": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample2-3": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample3-1": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample3-2": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample3-3": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample4-1": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample4-2": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample4-3": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample5-1": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample5-2": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample5-3": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample6-1": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample6-2": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"Sample6-3": 1X, solution, notes: aliquoted, solution is volatile, 5uL per test
"RPA Reagent Buffer": 1X, solution, notes: aliquoted, 42uL per test
"Reaction initiator": 1X, solution, notes: aliquoted, 3uL per test
"Nuclease-Free Water" or "H2O" or "Distilled Water" or "HPLC Water": liquid

## Assistant (2026-04-05T02:20:50.515Z)



## Tool (2026-04-05T02:20:55.235Z)

"Cobalt Chloride" or "CoCl2": 1.25mM, solution
"Nuclease-Free Water" or "H2O" or "Distilled Water" or "HPLC Water": liquid
"Sodium Chloride" or "nacl": 1M, solution
"Phosphate Buffer Stock (Sodium-based)" or "Phosphate Buffer": 10X, pH 6.8, stock solution, notes: Can be used for as phosphate salt.
"Terminal Deoxynucleotidyl Transferase" or "TdT" or "ZaTdT Enzyme" or "ZaTdT-R335L-K337G" or "TdT Series Enzyme Variants": 50mg/mL, solution, notes: Already purified and ready to use in storage buffer stock.
"3'-ONH2-dnTP" or "Untagged Aminoxy Reversible Terminators" or "3-ONH2-dNTP" or "Reversible Terminators": 5mM, solution, doc: 3-ONH2-dnTP-manual, notes: Cleaned, purified, and ready to use.
"Aqueous Sodium Acetate Buffer": pH 5.5, solution
"Tween" or "Tween-20": 1%, solution
"B&W Buffer": 2X, solution, components: Tris-HCl, EDTA, NaCl
"Lysis Buffer": 2X, solution, components: Potassium Phosphate Buffer (50mM), NaCl (100mM)
"Initiator-immobilized magnetic beads" or "beads" or "Washed Dynabeads M-270 Streptavidin" or "Dynabeads M-270 Streptavidin" or "Streptavidin-coated magnetic beads" or "strand" or "oligonucleotide": suspension, doc: beads-manual, notes: Initiators have been immobilized on the beads and washed. Remove storage buffer before use.
"Cleavage/Deblocking Buffer" or "Cleavage reagent" or "Deblocking reagent": 1X, pH 5.5, solution, components: Sodium Nitrite (700mM), Sodium Acetate Buffer (1M)
"Reaction Buffer": 10X, pH 6.8, stock solution, components: NaCl (1M), Phosphate Buffer (0.5M)
"3'-ONH2-dATP" or "3-ONH2-dATP": 5mM, solution, doc: 3-ONH2-dnTP-manual, notes: Cleaned, purified, and ready to use.
"3'-ONH2-dCTP" or "3-ONH2-dCTP": 5mM, solution, doc: 3-ONH2-dnTP-manual, notes: Cleaned, purified, and ready to use.
"3'-ONH2-dGTP" or "3-ONH2-dGTP": 5mM, solution, doc: 3-ONH2-dnTP-manual, notes: Cleaned, purified, and ready to use.
"3'-ONH2-dTTP" or "3-ONH2-dTTP": 5mM, solution, doc: 3-ONH2-dnTP-manual, notes: Cleaned, purified, and ready to use.
<manuals> 3-ONH2-dnTP-manual, beads-manual

## Assistant (2026-04-05T02:20:55.238Z)



## Tool (2026-04-05T02:20:59.762Z)

"polyT primer": solution, notes: The sequence is GTGACTGGAGTTCAGACGTGTGCTCTTCCGATCTTTTTTTTTTTTTTTTTTTTT
"P5 primer": solution, notes: The sequence is AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATC*T
"P7-i23 primer": solution, notes: The sequence is CAAGCAGAAGACGGCATACGAGATATCCACTCGTGACTGGAGTTCAGACGTGTGCTCTTCCGATC-s-T
"B&W Buffer": 2X, solution, components: Tris-HCl, EDTA, NaCl, Tween-20
"Beads-bound iDNA-(N)8 templates": suspension
"dATP" or "Deoxyadenosine triphosphate": solution
"dCTP" or "Deoxycytidine triphosphate": solution
"dGTP" or "Deoxyguanosine triphosphate": solution
"dTTP" or "Deoxythymidine triphosphate": solution
"Ethanol" or "80% ethanol" or "99.5% ethanol" or "ethanol": solution, notes: Used in various concentrations.
"High-Fidelity DNA Polymerase" or "Phanta Max Super-Fidelity DNA Polymerase": solution
"Phanta Max Master Mix (Dye Plus)" or "Phanta Max Master Mix": 2X, solution
"Nuclease-free water" or "H2O" or "ddH2O" or "HPLC Water": liquid
"Sodium Chloride" or "NaCl": solution
"VAHTS DNA Clean Beads" or "Solid Phase Reversible Immobilization Beads" or "SPRI Beads": suspension
"Terminal Deoxynucleotidyl Transferase" or "TdT": solution
"Terminal Deoxynucleotidyl Transferase Reaction Buffer" or "TdT Reaction Buffer": solution
"Tris-HCl": solution
"Cobalt Chloride" or "CoCl2": 2.5mM, solution
"Sodium Chloride" or "nacl": 1M, solution
"Phosphate Buffer Stock (Sodium-based)" or "Phosphate Buffer": 10X, pH 6.8, stock solution, notes: Can be used for as phosphate salt.
"3'-ONH2-dATP" or "Untagged Aminoxy Reversible Terminators": 5mM, solution, notes: Cleaned, purified, and ready to use.
"3'-ONH2-dTTP" or "Untagged Aminoxy Reversible Terminators": 5mM, solution, notes: Cleaned, purified, and ready to use.
"3'-ONH2-dCTP" or "Untagged Aminoxy Reversible Terminators": 5mM, solution, notes: Cleaned, purified, and ready to use.
"3'-ONH2-dGTP" or "Untagged Aminoxy Reversible Terminators": 5mM, solution, notes: Cleaned, purified, and ready to use.
"ZaTdT-R335L-K337G" or "TdT" or "ZaTdT" or "ZaTdT Enzyme" or "TdT Series Enzyme Variants": 50mg/mL, solution, notes: Already purified and ready to use in storage buffer stock.
"Aqueous Sodium Acetate Buffer": solution
"Tween" or "Tween-20": 1%, solution
"Initiator-immobilized magnetic beads" or "beads" or "Washed Dynabeads M-270 Streptavidin" or "Dynabeads M-270 Streptavidin" or "strand" or "oligonucleotide": suspension, notes: Initiators have been immobilized on the beads and washed.
"Deblocking Buffer" or "Deblocking reagent": 1X, pH 5.5, solution, components: Sodium Nitrite (700mM), Sodium Acetate Buffer (1M)
"Reaction Buffer": 10X, pH 6.8, stock solution, components: NaCl (1M), Phosphate Buffer (0.5M)

## Assistant (2026-04-05T02:20:59.764Z)

NC-1: available, 1X
Nuclease-Free Water: available, liquid
EDTA: not available
Tween-20: available, 1%

## You (2026-04-05T02:26:48.229Z)

/new
