# Changelog — Corrections and Updates

> Record all discoveries, errors found during experiments, and corrections here.
> Format: date · what was wrong · what the correct approach is.

---

## 2026-04-07 — Initial documentation created

- Created skeleton documentation based on analysis of `papers/Synthesis.xml` and
  `total/DNA合成.xml` (no hardware testing done yet).
- PDF paper `2507.02379v1.pdf` could not be read (missing `pdftotext` / `pdfminer`).
  Architecture was derived entirely from XML analysis.

### Decisions made

- Language for atomic service actions: **ST** (not LD) — simpler to generate and debug
- MW address scheme: `%MW50900` for module 09, follows `50 + NN + 00` pattern, confirmed safe
  (existing addresses are %MW20000, 21000, 40000, 43000, 60000-63003 — %MW50xxx is free)
- `Synthesis` global variable type is `G_Synthesis` at `%MB188876`
- Key confirmed servo variables: `G_Servo[搬运X/Y/Z轴]`, `G_HC_Notkeep_jaw[搬运夹爪]`
- `Synthesis.Handing_types`: 0=empty, 5=96-well plate (confirmed from code comments)

### Open questions (to be resolved during hardware testing)

- [ ] Actual MW address of `G_Module_Process[9].M_Show_Step_AUTO`
      (depends on where `G_Module_Process` lands in global memory after adding it)
- [ ] Correct sensor variable name for "metal bath slot empty"
      (assumed `Synthesis.metal_bath1 = 0` based on F09流程 code, needs confirmation)
- [ ] Whether `Synthesis.Handing_types = 0` correctly means "gripper at safe home position"
- [ ] Whether `%MW50900` conflicts with any existing variable
      (search `DNA合成.xml` global vars for `%MW509` before flashing)
- [ ] PLC IP address and communication port for C++ testing
- [ ] Confirm Modbus TCP is enabled on the PLC runtime

---

---

## 2026-04-07 — M_PT index table confirmed by hardware engineer

All X/Y axis M_PT indices now confirmed. ST code corrected accordingly.

**Corrections made to ST code:**
- Sample 1 pickup: was `M_PT[14]` (wrong) → corrected to `M_PT[11]` (样品载具1位)
- Sample 2 pickup: was `M_PT[24]` (guessed) → corrected to `M_PT[12]` (样品载具2位)
- Metal bath 1 target: `M_PT[13]` (金属浴1位小板) — now confirmed
- Metal bath 2 target: `M_PT[14]` (金属浴2位小板) — now confirmed
- Logic simplified: Plate_Pos parameter removed from internal routing; target now determined from Sample_Num directly

**Still unresolved:**
- [ ] Z axis M_PT[0] = safe travel height? (assumed, not confirmed from Z axis PT table)
- [ ] Z axis M_PT[19] = metal bath drop height? (assumed, not confirmed)
- [ ] Gripper completion signal: does `M_Show_DrvaOK` fire on physical grip? Or is command-equals-target the intended check?

<!-- Add new entries below as experiments reveal corrections -->
