# Atomic Service Extraction — DNA Synthesis PLC

> Records the process of extracting atomic services from `total/DNA合成.xml`,
> modeled after the modular architecture in `papers/Synthesis.xml`.

## Background

The AutoDNA project uses an LLM-based upper-layer scheduler that calls bottom-level
**atomic services** (原子服务) to compose complex DNA synthesis workflows. Atomic
services are the smallest, reusable, single-action PLC modules.

**Reference project:** `papers/Synthesis.xml`  
**Target project:** `total/DNA合成.xml`

## Architecture Overview

In the reference project, the pattern is:

```
B自动流程 (PRG)        ← top-level scheduler
  ├── F-series actions ← high-level process flows (unchanged)
  └── F20-series actions (in "模块化" folder) ← atomic services (to be added)

Global variables:
  G_Module_Process[0..30] : ARRAY OF G_ProcessInformation   ← module state tracking
  G_P_F20_XX_Input AT %MW50XX0 : SXX_Module_Input            ← module input params

Data types (in "模块参数" folder):
  SXX_Module_Input : STRUCT { ... }   ← per-module parameter struct
```

## Files in This Folder

| File | Purpose |
|------|---------|
| `README.md` | This overview |
| `01-ide-setup.md` | IDE operations: global vars, data types, folder structure |
| `02-first-atomic-service.md` | Step-by-step for the first module: F20_09进金属浴模块 |
| `03-cpp-testing.md` | C++ / external code testing approach |
| `changelog.md` | Updates and corrections discovered during experiments |
| `04-second-atomic-service.md` | Step-by-step for F20_10出金属浴模块 |

## Extraction Status

| Module | Name | Status | Notes |
|--------|------|--------|-------|
| F20_09 | 进金属浴模块 | ✅ Code complete | ST file created; Z axis M_PT[0]/[19] pending hardware verify |
| F20_10 | 出金属浴模块 | ✅ Code complete | Inverse of F20_09; same Z axis caveats apply |
| F20_13 | 倾斜角度模块 | 🔲 Planned | |
| F20_11 | 倾斜进料模块 | 🔲 Planned | |
| F20_12 | 倾斜出料模块 | 🔲 Planned | |
| F20_01 | 取枪头模块 | 🔲 Planned | |
| F20_02 | 退枪头模块 | 🔲 Planned | |
| F20_03 | 吸液模块 | 🔲 Planned | |
| F20_04 | 排液模块 | 🔲 Planned | |
