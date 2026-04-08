# Second Atomic Service — F20_10 出金属浴模块

> **Inverse of F20_09.**  
> Moves a sample carrier from the metal bath heating block back to the sample station.
> Same hardware path, reversed direction.

---

## 1. Define the Parameter Struct

**In IDE:** `模块参数` folder → New DUT → name `S10_Module_Input`

```
TYPE S10_Module_Input :
STRUCT
    Sample_Num : UINT;   (* 样品编号: 1 = sample 1, 2 = sample 2 *)
END_STRUCT
END_TYPE
```

**Hardware address:** `G_P_F20_10_Input AT %MW51000 : S10_Module_Input;`

Memory layout at `%MW51000`:
| Offset | Modbus Register | Size | Field |
|--------|----------------|------|-------|
| +0 (MW51000) | 51001 | 1 word (UINT) | Sample_Num |

> Note: No `Plate_Pos` field needed. Target is always the matching sample station
> (sample 1 → M_PT[11], sample 2 → M_PT[12]).

---

## 2. Create the Action

**In IDE:** `模块化` folder → right-click `B自动流程` → Add Action  
→ language: **ST** → name: `F20_10出金属浴模块`

---

## 3. ST Code

See `F20_10_出金属浴模块.st` in this folder.

---

## 4. Step Sequence

| Step | Action |
|------|--------|
| 0    | Initialize, reset completion flag |
| 100  | Entry check: metal_bathN=TRUE, station_plateN=FALSE, Handing_types=0 |
| 110  | Clear XY trigger flags |
| 120  | XY → metal bath position (M_PT[13] or [14]) |
| 130  | Clear Z trigger flags |
| 140  | Z down to metal bath pick height (M_PT[19] ⚠️) |
| 150  | Clear gripper trigger flags |
| 160  | Close gripper (M_PT[3]); set Handing_types := 5 |
| 170  | Z up to safe height (M_PT[0] ⚠️) |
| 180  | XY → sample station (M_PT[11] or [12]) |
| 190  | Z down to sample station release height (M_PT[18] ✅) |
| 200  | Open gripper (M_PT[2]); set metal_bathN := FALSE, station_plateN := TRUE, Handing_types := 0 |
| 210  | Z up to safe height (M_PT[0] ⚠️) |
| 900  | M_Signaling_Completed := TRUE |
| 1000 | Standby |

---

## 5. Entry / Exit State Summary

| Variable | Entry condition | After completion |
|----------|----------------|-----------------|
| `Synthesis.metal_bath1` (or 2) | TRUE (occupied) | FALSE (cleared) |
| `Synthesis.station_plate1` (or 2) | FALSE (empty) | TRUE (has carrier) |
| `Synthesis.Handing_types` | 0 (gripper empty) | 0 (gripper empty) |

---

## 6. Add Call to B自动流程

```st
F20_10出金属浴模块();
```

---

## 7. Unresolved Items (same as F20_09)

- [ ] Z axis M_PT[0] = safe travel height? (assumed, not confirmed)
- [ ] Z axis M_PT[19] = metal bath pick/drop height? (assumed, not confirmed)
- [ ] Gripper completion signal: does M_Show_DrvaOK fire on physical grip?

These will be resolved during the same hardware test session as F20_09.
