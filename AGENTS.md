# Repository Guidelines

This is a personal fork of openclaw/openclaw, used for AutoDNA Skills migration.
Original upstream guidelines preserved in `CLAUDE-upstream.md`.

- Repo: https://github.com/Dshuishui/Helix (fork of https://github.com/openclaw/openclaw)
- In chat replies, file references must be repo-root relative only (e.g., `extensions/autodna/skills/reagent-agent/SKILL.md`); never absolute paths or `~/...`.

## AutoDNA Extension Work

Primary ongoing work: migrating AutoDNA (LangChain/LangGraph multi-agent lab automation) to OpenClaw Skills.

- Migration plan and progress: `extensions/autodna/PLAN.md`
- Skill registration guide: `extensions/autodna/SKILL-REGISTRATION-GUIDE.md`
- Skills directory: `extensions/autodna/skills/`
- Original AutoDNA project: `../AutoDNA/AutoDNA-python/scientist/`

### Skill Registration Quick Reference

```bash
# Package
python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  extensions/autodna/skills/<skill-name> /tmp/autodna-skills

# Install (both steps required)
openclaw plugins install /tmp/autodna-skills/<skill-name>.skill
cd ~/.openclaw/workspace/skills && unzip -o /tmp/autodna-skills/<skill-name>.skill

# Restart + new session
openclaw gateway restart
# Then send /new or /reset in Feishu
```

Key rules:
- Script paths in SKILL.md: relative to `~/.openclaw/workspace/` (e.g., `skills/<name>/scripts/script.py`)
- Script internal paths: use `os.path.dirname(__file__)` for data file references
- Use `python3` not `python` on macOS

## Project Structure

- OpenClaw source: `src/` (CLI in `src/cli`, commands in `src/commands`)
- Extensions: `extensions/` (AutoDNA in `extensions/autodna/`)
- Tests: colocated `*.test.ts`
- Built output: `dist/`

## Build & Dev Commands

- Install deps: `pnpm install`
- Run CLI in dev: `pnpm openclaw ...`
- Type-check/build: `pnpm build`
- Lint/format: `pnpm check`
- Tests: `pnpm test`
- Pre-commit hooks: `prek install`

## Git Guidelines

- Commit messages: concise, action-oriented (e.g., `feat(autodna): add protocol-agent skill`)
- No merge commits on `main`; rebase instead
- Do not switch branches unless explicitly requested
- Do not create/apply/drop `git stash` entries unless explicitly requested

## Collaboration / Safety

- Answer with high confidence only; verify in code before stating facts
- Do not guess file contents — read them first
- Never commit real API keys, phone numbers, or credentials
- Before taking irreversible actions (delete files, force push), confirm with user
