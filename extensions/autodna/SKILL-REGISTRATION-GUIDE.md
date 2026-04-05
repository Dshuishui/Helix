# AutoDNA Skill 注册标准流程

本文档记录将一个 Agent 迁移并注册为 OpenClaw Skill 的完整流程，供后续迁移其他 Agent 时参考。

---

## 目录结构规范

每个 Skill 必须遵循以下结构：

```
skills/<skill-name>/
├── SKILL.md          ← 必须，Skill 的核心定义文件
├── scripts/          ← 可选，确定性 Python/Bash 脚本
├── references/       ← 可选，数据文件、文档、JSON 等参考资料
└── assets/           ← 可选，模板、图片等输出用文件
```

**注意：** 不要创建 README.md、CHANGELOG.md 等辅助文档，只放 Skill 运行所需的文件。

---

## SKILL.md 格式规范

```markdown
---
name: skill-name
description: |
  一句话说清楚这个 Skill 做什么，以及什么情况下触发。
  description 是触发机制，必须清晰完整。
---

# Skill 标题

正文：给 AI 看的操作说明，包含步骤、规则、输出格式等。
```

**关键原则：**
- `description` 决定 Skill 何时被触发，写清楚触发场景
- 正文保持在 500 行以内
- 脚本路径必须相对于 workspace 根目录（`~/.openclaw/workspace/`）

---

## 完整注册流程

### Step 1：创建 Skill 文件

在 `extensions/autodna/skills/<skill-name>/` 下创建：
- `SKILL.md`：提示词 + 规则 + 输出格式
- `scripts/`：Python 脚本（路径写法见下方注意事项）
- `references/`：JSON 数据文件等

**脚本路径注意事项：**

Skill 安装后，agent 的工作目录是 `~/.openclaw/workspace/`，脚本路径必须相对于此：

```bash
# ✅ 正确：相对于 workspace
python3 skills/<skill-name>/scripts/your_script.py

# ❌ 错误：使用了 repo 的绝对路径
python3 extensions/autodna/skills/<skill-name>/scripts/your_script.py
```

**脚本内部路径注意事项：**

脚本内引用同级目录下的数据文件，使用 `__file__` 相对路径：

```python
# ✅ 正确：相对于脚本自身位置
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "references")

# ❌ 错误：引用了旧的 data/ 目录名
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
```

### Step 2：本地验证脚本

打包前先在本地运行脚本确认无报错：

```bash
python3 extensions/autodna/skills/<skill-name>/scripts/your_script.py [args]
```

### Step 3：打包成 .skill 文件

```bash
python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  extensions/autodna/skills/<skill-name> \
  /tmp/autodna-skills
```

打包脚本会自动验证结构和格式，输出 `/tmp/autodna-skills/<skill-name>.skill`。

### Step 4：安装到 workspace

```bash
# 安装到 OpenClaw extensions 目录
openclaw plugins install /tmp/autodna-skills/<skill-name>.skill

# 解压到 workspace skills 目录（使其生效）
cd ~/.openclaw/workspace/skills
unzip -o /tmp/autodna-skills/<skill-name>.skill
```

### Step 5：确认注册成功

```bash
openclaw skills list | grep <skill-name>
# 应看到：✓ ready  |  <skill-name>  |  ...  |  openclaw-workspace
```

### Step 6：重启 gateway 并开启新会话

```bash
openclaw gateway restart
```

重启后，**必须在飞书开启一个新会话**（发送 `/new` 或 `/reset`），新 Skill 才会被加载到上下文中。已有的旧会话不会自动感知新注册的 Skill。

---

## 更新已注册的 Skill

修改源文件后，重新打包并覆盖 workspace：

```bash
# 1. 重新打包
python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  extensions/autodna/skills/<skill-name> /tmp/autodna-skills

# 2. 覆盖 workspace 中的旧版本
cd ~/.openclaw/workspace/skills
rm -rf <skill-name>
unzip -o /tmp/autodna-skills/<skill-name>.skill

# 3. 同步更新 extensions 目录
cp /tmp/autodna-skills/<skill-name>.skill ~/.openclaw/extensions/<skill-name>.skill
```

更新后同样需要在飞书开启新会话（`/new` 或 `/reset`）才能加载最新版本。

---

## 已注册的 AutoDNA Skills

| Skill | 状态 | 对应 AutoDNA Agent |
|-------|------|-------------------|
| `reagent-agent` | ✅ ready | `agents/Reagent.py` |
| `literature-agent` | 待迁移 | `agents/Literature.py` |
| `protocol-agent` | 待迁移 | `agents/Protocol.py` |
| `code-agent` | 待迁移 | `agents/Code.py` |
| `hardware-agent` | 待迁移 | `agents/Hardware.py` |
| `hypothesis-agent` | 待迁移 | `agents/Hypothesis.py` |

---

## 常见问题

**Q: Skill 列表里看不到新 Skill？**  
检查是否完成了 Step 4 的 `unzip` 步骤，仅 `plugins install` 不够。

**Q: 脚本找不到文件（FileNotFoundError）？**  
检查脚本内的 `DATA_DIR` 路径，确保指向 `references/` 而非 `data/`。

**Q: 打包时提示 stale config entry？**  
运行 `openclaw config unset plugins.entries.<skill-name>` 清理遗留配置。

**Q: Skill 已注册但飞书里触发不了？**  
必须在飞书发送 `/new` 或 `/reset` 开启新会话，旧会话不会自动加载新注册的 Skill。
