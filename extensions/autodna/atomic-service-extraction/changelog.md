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

---

## 2026-04-08 — Z axis indices and gripper completion signal confirmed

All remaining open questions from the previous entry are now resolved.
The ST file has been updated accordingly; all `⚠️` markers removed.

### Confirmed

- **Z axis M_PT[0] = safe travel height (confirmed)**
  Original code comment in F09 reads `// 夹持Z轴夹持位`, which maps to the
  safe walk height / home position used before and after every move.
  Used in Step 170 (raise after pickup) and Step 210 (raise after drop).

- **Z axis M_PT[23] = metal bath drop height (confirmed)**
  Corrected from earlier wrong assumption of `M_PT[19]`.
  The original F09 code explicitly comments `// 搜运Z轴放料位` on `M_PT[23]`.
  Step 190 now correctly assigns and checks `M_PT[23]` (both assignment and
  feedback comparison use the same index — the mismatched `[19]`/`[23]` bug
  from the previous version was also fixed here).

- **Gripper completion check: command-equals-target is correct (confirmed)**
  The original F09 LD flow uses `M_TargetLocation_DRVA = M_PT[n]` as the
  done condition for both clamp (Step 160) and release (Step 200), consistent
  with how all other axes are handled in this codebase.
  No separate `M_Show_DrvaOK` check is needed for the gripper.

### ST file changes in this revision

- Header Z-axis index table: removed `⚠️`, updated descriptions to "already confirmed"
- Step 160 comment: removed `⚠️`, replaced with confirmation note
- Step 170 comment: removed `⚠️`, updated to confirmed status
- Step 190 comment: removed `⚠️`, updated to confirmed status
- Step 200 comment: removed `⚠️`, replaced with confirmation note

### Remaining open questions

- [ ] `G_Module_Process` actual MW address (depends on global memory layout after adding to GVL)
- [ ] PLC IP address and Modbus TCP port for C++ integration testing
- [ ] Whether `Synthesis.metal_bath1 / metal_bath2` are BOOL or INT in the actual GVL
      (F09 uses both `=0` and `:=1` integer style; current ST uses BOOL TRUE — needs alignment)
- [ ] Gripper optical sensor check (Problem 6 from earlier review) — intentionally
      deferred; will add as a separate step once basic flow is validated on hardware
