# First Atomic Service — F20_09 进金属浴模块

> **Why this one first:**  
> Single observable physical action (move a sample carrier into the metal bath heating block),
> minimal input parameters, easy to visually verify success/failure on hardware.

---

## 1. Define the Parameter Struct

**In IDE:** `模块参数` folder → New DUT → name `S09_Module_Input`

```
TYPE S09_Module_Input :
STRUCT
    Sample_Num : UINT;   (* 样品编号: 1 = sample 1, 2 = sample 2 *)
    Plate_Pos  : DINT;   (* M_PT index for target metal bath position *)
END_STRUCT
END_TYPE
```

**Hardware address:** `G_P_F20_09_Input AT %MW50900 : S09_Module_Input;`

Memory layout at `%MW50900`:
| Offset | Modbus Register | Size | Field |
|--------|----------------|------|-------|
| +0 (MW50900) | 50901 | 1 word (UINT) | Sample_Num |
| +1 (MW50901) | 50902 | 2 words (DINT) | Plate_Pos |

---

## 2. Language Choice: ST (Structured Text)

Use **ST** (not LD) for this action. Reasons:
- State machine logic is cleaner and more readable in ST
- Easier to generate, verify and debug as text
- Compiles to identical bytecode as LD on hardware
- Consistent with how external schedulers (LLM) reason about the code

---

## 3. Create the Action

**In IDE:** `模块化` folder → right-click `B自动流程` → Add Action
→ language: **ST** → name: `F20_09进金属浴模块`

---

## 4. ST Code (copy-paste ready)

Key hardware variables confirmed from `DNA合成.xml` analysis:
- `Synthesis.station_plate1/2` — sample carrier presence sensor
- `Synthesis.metal_bath1/2` — metal bath occupancy flag
- `Synthesis.Handing_types` — gripper payload type (0=empty, 5=96-well plate)
- `G_Servo[搬运X轴/Y轴/Z轴]` — transport servo axes
- `G_Servo_Function[轴].M_PT[N]` — position point table
- `G_HC_Notkeep_jaw[搬运夹爪]` — gripper actuator
- `G_HC_keep_jaw[搬运夹爪].M_PT[N]` — gripper position points

```pascal
(* ============================================================
   F20_09进金属浴模块
   Atomic service: move sample carrier from sample station into metal bath
   Input:  G_P_F20_09_Input @ %MW50900
             .Sample_Num  UINT   sample number (1 or 2)
             .Plate_Pos   DINT   M_PT index for metal bath slot position
   State:  G_Module_Process[9].M_Show_Step_AUTO
   ============================================================ *)

CASE G_Module_Process[9].M_Show_Step_AUTO OF

(* Step 0: initialization / idle *)
0:
    IF NOT G_Module_Process[9].M_Trigger_Pause THEN
        G_Module_Process[9].M_Show_Step_AUTO := 100;
    END_IF

(* Step 100: entry condition check *)
100:
    IF NOT G_MasterControl.IN_Trigger_EStop
       AND NOT G_Module_Process[9].M_Trigger_Pause THEN
        IF G_P_F20_09_Input.Sample_Num = 1 THEN
            IF Synthesis.station_plate1
               AND NOT Synthesis.metal_bath1
               AND Synthesis.Handing_types = 0 THEN
                G_Module_Process[9].M_Show_Step_AUTO := 110;
            END_IF
        ELSIF G_P_F20_09_Input.Sample_Num = 2 THEN
            IF Synthesis.station_plate2
               AND NOT Synthesis.metal_bath2
               AND Synthesis.Handing_types = 0 THEN
                G_Module_Process[9].M_Show_Step_AUTO := 110;
            END_IF
        END_IF
    END_IF

(* Step 110: clear XY axis trigger flags *)
110:
    G_Servo[搬运X轴].M_Trigger_DRVA := FALSE;
    G_Servo[搬运X轴].M_Show_DrvaOK  := FALSE;
    G_Servo[搬运Y轴].M_Trigger_DRVA := FALSE;
    G_Servo[搬运Y轴].M_Show_DrvaOK  := FALSE;
    IF NOT G_Servo[搬运X轴].M_Trigger_DRVA
       AND NOT G_Servo[搬运Y轴].M_Trigger_DRVA THEN
        G_Module_Process[9].M_Show_Step_AUTO := 120;
    END_IF

(* Step 120: move XY to sample station
   ⚠️ M_PT index must be verified against servo position table in IDE *)
120:
    IF NOT G_Module_Process[9].M_Trigger_Pause THEN
        IF G_P_F20_09_Input.Sample_Num = 1 THEN
            G_Servo[搬运X轴].M_TargetLocation_DRVA :=
                G_Servo_Function[搬运X轴].M_PT[14]; (* sample 1 station X ⚠️ verify *)
            G_Servo[搬运Y轴].M_TargetLocation_DRVA :=
                G_Servo_Function[搬运Y轴].M_PT[14]; (* sample 1 station Y ⚠️ verify *)
        ELSE
            G_Servo[搬运X轴].M_TargetLocation_DRVA :=
                G_Servo_Function[搬运X轴].M_PT[24]; (* sample 2 station X ⚠️ verify *)
            G_Servo[搬运Y轴].M_TargetLocation_DRVA :=
                G_Servo_Function[搬运Y轴].M_PT[24]; (* sample 2 station Y ⚠️ verify *)
        END_IF
        IF G_Servo[搬运X轴].M_TargetLocation_DRVA_Feedback
               = G_Servo[搬运X轴].M_TargetLocation_DRVA
           AND G_Servo[搬运Y轴].M_TargetLocation_DRVA_Feedback
               = G_Servo[搬运Y轴].M_TargetLocation_DRVA THEN
            G_Module_Process[9].M_Show_Step_AUTO := 130;
        END_IF
    END_IF

(* Step 130: clear Z axis trigger flags *)
130:
    G_Servo[搬运Z轴].M_Trigger_DRVA := FALSE;
    G_Servo[搬运Z轴].M_Show_DrvaOK  := FALSE;
    IF NOT G_Servo[搬运Z轴].M_Trigger_DRVA THEN
        G_Module_Process[9].M_Show_Step_AUTO := 140;
    END_IF

(* Step 140: Z down to pick height
   ⚠️ M_PT[18] confirmed from F09流程 comment "96孔板取料位" *)
140:
    G_Servo[搬运Z轴].M_TargetLocation_DRVA :=
        G_Servo_Function[搬运Z轴].M_PT[18];
    IF G_Servo[搬运Z轴].M_TargetLocation_DRVA_Feedback
           = G_Servo_Function[搬运Z轴].M_PT[18] THEN
        G_Module_Process[9].M_Show_Step_AUTO := 150;
    END_IF

(* Step 150: clear gripper trigger flags *)
150:
    G_HC_Notkeep_jaw[搬运夹爪].M_Trigger_DRVA := FALSE;
    G_HC_Notkeep_jaw[搬运夹爪].M_Show_DrvaOK  := FALSE;
    IF NOT G_HC_Notkeep_jaw[搬运夹爪].M_Trigger_DRVA THEN
        G_Module_Process[9].M_Show_Step_AUTO := 160;
    END_IF

(* Step 160: close gripper to grip carrier
   ⚠️ M_PT[3] = grip position, confirmed from F09流程 *)
160:
    G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA :=
        G_HC_keep_jaw[搬运夹爪].M_PT[3];
    IF G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA
           = G_HC_keep_jaw[搬运夹爪].M_PT[3] THEN
        Synthesis.Handing_types := 5; (* carrying 96-well plate *)
        G_Module_Process[9].M_Show_Step_AUTO := 170;
    END_IF

(* Step 170: Z up to safe travel height *)
170:
    G_Servo[搬运Z轴].M_Trigger_DRVA := FALSE;
    G_Servo[搬运Z轴].M_Show_DrvaOK  := FALSE;
    G_Servo[搬运Z轴].M_TargetLocation_DRVA :=
        G_Servo_Function[搬运Z轴].M_PT[0]; (* safe height ⚠️ verify index *)
    IF G_Servo[搬运Z轴].M_TargetLocation_DRVA_Feedback
           = G_Servo_Function[搬运Z轴].M_PT[0] THEN
        G_Module_Process[9].M_Show_Step_AUTO := 180;
    END_IF

(* Step 180: move XY to metal bath position (from input parameter) *)
180:
    G_Servo[搬运X轴].M_Trigger_DRVA := FALSE;
    G_Servo[搬运X轴].M_Show_DrvaOK  := FALSE;
    G_Servo[搬运Y轴].M_Trigger_DRVA := FALSE;
    G_Servo[搬运Y轴].M_Show_DrvaOK  := FALSE;
    G_Servo[搬运X轴].M_TargetLocation_DRVA :=
        G_Servo_Function[搬运X轴].M_PT[G_P_F20_09_Input.Plate_Pos];
    G_Servo[搬运Y轴].M_TargetLocation_DRVA :=
        G_Servo_Function[搬运Y轴].M_PT[G_P_F20_09_Input.Plate_Pos];
    IF G_Servo[搬运X轴].M_TargetLocation_DRVA_Feedback
           = G_Servo[搬运X轴].M_TargetLocation_DRVA
       AND G_Servo[搬运Y轴].M_TargetLocation_DRVA_Feedback
           = G_Servo[搬运Y轴].M_TargetLocation_DRVA THEN
        G_Module_Process[9].M_Show_Step_AUTO := 190;
    END_IF

(* Step 190: Z down to metal bath drop height
   ⚠️ M_PT[19] assumed; must verify against position table *)
190:
    G_Servo[搬运Z轴].M_Trigger_DRVA := FALSE;
    G_Servo[搬运Z轴].M_Show_DrvaOK  := FALSE;
    G_Servo[搬运Z轴].M_TargetLocation_DRVA :=
        G_Servo_Function[搬运Z轴].M_PT[19]; (* metal bath drop Z ⚠️ verify *)
    IF G_Servo[搬运Z轴].M_TargetLocation_DRVA_Feedback
           = G_Servo_Function[搬运Z轴].M_PT[19] THEN
        G_Module_Process[9].M_Show_Step_AUTO := 200;
    END_IF

(* Step 200: open gripper to release carrier *)
200:
    G_HC_Notkeep_jaw[搬运夹爪].M_Trigger_DRVA := FALSE;
    G_HC_Notkeep_jaw[搬运夹爪].M_Show_DrvaOK  := FALSE;
    G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA :=
        G_HC_keep_jaw[搬运夹爪].M_PT[2]; (* release position ⚠️ verify index *)
    IF G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA
           = G_HC_keep_jaw[搬运夹爪].M_PT[2] THEN
        Synthesis.Handing_types := 0; (* gripper empty *)
        IF G_P_F20_09_Input.Sample_Num = 1 THEN
            Synthesis.metal_bath1 := TRUE;
        ELSE
            Synthesis.metal_bath2 := TRUE;
        END_IF
        G_Module_Process[9].M_Show_Step_AUTO := 210;
    END_IF

(* Step 210: Z up to safe height after release *)
210:
    G_Servo[搬运Z轴].M_Trigger_DRVA := FALSE;
    G_Servo[搬运Z轴].M_Show_DrvaOK  := FALSE;
    G_Servo[搬运Z轴].M_TargetLocation_DRVA :=
        G_Servo_Function[搬运Z轴].M_PT[0]; (* safe height *)
    IF G_Servo[搬运Z轴].M_TargetLocation_DRVA_Feedback
           = G_Servo_Function[搬运Z轴].M_PT[0] THEN
        G_Module_Process[9].M_Show_Step_AUTO := 900;
    END_IF

(* Step 900: signal completion *)
900:
    G_Module_Process[9].M_Signaling_Completed := TRUE;
    G_Module_Process[9].M_Show_Step_AUTO      := 1000;

(* Step 1000: standby — wait for external reset *)
1000:
    ;

END_CASE
```

---

## 5. M_PT Index Verification Table

X/Y axis indices confirmed by hardware engineer. Z axis indices partially confirmed.

### X/Y axis (same index scheme, different coordinate values)

| Index | Meaning | Status |
|-------|---------|--------|
| M_PT[0]  | 初始位 | ✅ Confirmed |
| M_PT[11] | 样品载具1位 (sample 1 station) | ✅ Confirmed |
| M_PT[12] | 样品载具2位 (sample 2 station) | ✅ Confirmed |
| M_PT[13] | 金属浴1位（小板）| ✅ Confirmed |
| M_PT[14] | 金属浴2位（小板）| ✅ Confirmed |

### Z axis

| Variable | Index | Source | Status |
|----------|-------|--------|--------|
| `G_Servo_Function[搬运Z轴].M_PT[18]` | 18 | F09 code comment "96孔板取料位" | ✅ Confirmed |
| `G_Servo_Function[搬运Z轴].M_PT[0]`  | 0  | Assumed safe travel height | ⚠️ Verify Z axis PT table |
| `G_Servo_Function[搬运Z轴].M_PT[19]` | 19 | Assumed metal bath drop height | ⚠️ Verify Z axis PT table |

### Gripper

| Variable | Index | Source | Status |
|----------|-------|--------|--------|
| `G_HC_keep_jaw[搬运夹爪].M_PT[3]` | 3 | F09 gripper close step | ✅ Confirmed |
| `G_HC_keep_jaw[搬运夹爪].M_PT[2]` | 2 | F09 gripper open step | ✅ Confirmed |

### Additional uncertainty: gripper completion signal

The F09 code checks `M_TargetLocation_DRVA = M_PT[N]` (command equals target, always true after assignment).
If the gripper has a physical completion signal (e.g., `M_Show_DrvaOK = TRUE`), that should be used instead.
**Verify:** does `G_HC_Notkeep_jaw[搬运夹爪].M_Show_DrvaOK` indicate physical grip completion?

---

## 6. Add Call to B自动流程

In `B自动流程` ST body, append:
```st
F20_09进金属浴模块();
```

---

## 7. Compile and Flash

1. `Build` → `Build Project` — 0 errors required
2. `Online` → `Login` → `Download` → flash
3. RUN mode
