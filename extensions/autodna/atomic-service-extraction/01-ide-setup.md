# IDE Setup — InoProShop Operations

> These steps create the skeleton infrastructure for all future atomic services.
> Perform once before adding any individual module.

## Step 1 — Add `G_Module_Process` Global Variable

**Location in IDE:**
`Device` → `Plc Logic` → `Application` → `03 程序变量` → `全局变量`
(find the section where `G_Process` is already declared)

**Add this variable next to `G_Process`:**

```
G_Module_Process : ARRAY[0..30] OF G_ProcessInformation;
(* 模块流程控制 — tracks execution state for each atomic service module *)
```

> Uses the exact same `G_ProcessInformation` struct already used by `G_Process`.
> Array size [0..30] accommodates up to 31 modules.

---

## Step 2 — Create `模块参数` Data Type Folder

**Location in IDE:**
`03 程序变量` → `数据类型` → right-click → New Folder → name it `模块参数`

This folder will hold one DUT (Data Unit Type) per atomic service module.

---

## Step 3 — Add Module Input Global Variables

**Location:** same global variable file as Step 1

For each module, add one global variable with a fixed MW address.
The address scheme mirrors the reference project: module N uses `%MW50N00`.

```
(* === Atomic Service Module Input Parameters === *)
G_P_F20_09_Input AT %MW50900 : S09_Module_Input;
G_P_F20_10_Input AT %MW51000 : S10_Module_Input;
(* add more here as new modules are created *)
```

> The fixed MW address is what allows external C++ code to write input parameters
> directly to hardware memory before triggering the module.

---

## Step 4 — Create `模块化` Action Folder under B自动流程

**Location in IDE:**
`01 应用程序` → `B_自动流程` → right-click on `B自动流程` POU
→ New Folder → name it `模块化`

All F20-series actions (atomic service modules) go inside this folder.

---

## Step 5 — Add Module Calls to B自动流程 Body

Open `B自动流程` PRG body (ST language section at the bottom).

Append at the end, after all existing F-series calls:

```st
(* === Atomic Service Modules === *)
F20_09进金属浴模块();
F20_10出金属浴模块();
(* add more calls as new modules are created *)
```

> The modules run every PLC scan cycle. Each module's internal step-machine
> only executes logic when its `G_Module_Process[N].M_Show_Step_AUTO` is non-zero,
> so idle modules have negligible CPU cost.

---

## Verification

After completing all steps, compile (`Build` → `Build Project`).
Expected result: **0 errors, 0 warnings** (new variables and empty actions compile clean).

If compile errors appear, check:
- `G_ProcessInformation` type exists (should already be in the project)
- MW address `%MW50900` does not conflict with existing variable addresses
  (search existing global vars for `%MW509`)
