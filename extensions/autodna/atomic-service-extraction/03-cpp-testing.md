# C++ Testing — Triggering Atomic Services from External Code

> After flashing the PLC, use external code to write parameter values into
> the module's input variable and trigger execution by setting the step register.

---

## How It Works

Each atomic service module has:
1. An input parameter variable at a **fixed MW address** (e.g., `%MW50900`)
2. A step register `G_Module_Process[N].M_Show_Step_AUTO`

External code (C++, Python, etc.) communicates with the PLC over:
- **InoProShop runtime API** (汇川 Inovance SDK)
- **Modbus TCP** (if enabled on the PLC)
- **OPC UA** (if configured)

The test sequence is always:
```
1. Write input parameters to %MW50XX0
2. Write step value 100 to G_Module_Process[N].M_Show_Step_AUTO  ← triggers module
3. Poll M_Show_Step_AUTO until it reaches 1000                    ← module done
4. Read M_Signaling_Completed to confirm success
```

---

## F20_09 进金属浴模块 — Test Sequence

### Memory Map

| PLC Variable | MW Address | Type | Description |
|---|---|---|---|
| `G_P_F20_09_Input.Sample_Num` | `%MW50900` | UINT (1 word) | Sample number (1 or 2) |
| `G_P_F20_09_Input.Plate_Pos` | `%MW50901` | DINT (2 words) | Target position index |
| `G_Module_Process[9].M_Show_Step_AUTO` | TBD* | INT | Step register (write 100 to trigger) |
| `G_Module_Process[9].M_Signaling_Completed` | TBD* | BOOL | Done flag |

> *The MW address of `G_Module_Process[9]` depends on where `G_Module_Process`
> is placed in global memory. Check in InoProShop: right-click variable → Properties → Address.
> Record the actual address in `changelog.md` after confirming.

---

## C++ Pseudocode (Inovance SDK)

```cpp
#include "inovance_plc_sdk.h"  // replace with actual SDK header

int main() {
    PlcConnection plc;
    plc.connect("192.168.1.100", 502);  // PLC IP, Modbus port

    // --- Step 1: Write input parameters ---
    uint16_t sample_num = 1;          // sample 1
    int32_t  plate_pos  = 100;        // position index 100

    plc.writeWord(0xC714, sample_num);            // %MW50900 in hex
    plc.writeDWord(0xC716, (uint32_t)plate_pos);  // %MW50901 (DINT = 2 words)

    // --- Step 2: Trigger module ---
    // Write 100 to G_Module_Process[9].M_Show_Step_AUTO
    plc.writeWord(MODULE_PROC_9_STEP_ADDR, 100);

    // --- Step 3: Poll for completion ---
    int timeout_ms = 10000;
    int elapsed = 0;
    while (elapsed < timeout_ms) {
        int16_t step = plc.readWord(MODULE_PROC_9_STEP_ADDR);
        if (step == 1000) {
            printf("Module F20_09 completed successfully.\n");
            break;
        }
        if (step < 100) {
            printf("Module reset or error at step %d\n", step);
            break;
        }
        sleep_ms(100);
        elapsed += 100;
    }

    plc.disconnect();
    return 0;
}
```

---

## Modbus TCP Address Calculation

InoProShop maps `%MW` addresses to Modbus holding registers as:

```
Modbus register = MW_address + 1  (1-indexed in Modbus protocol)
```

Example:
- `%MW50900` → Modbus register **50901** (0xC715 in hex)
- `%MW50901` → Modbus register **50902** (0xC716 in hex)

Use a tool like **Modbus Poll** or **Simply Modbus** to verify connectivity
before writing C++ code.

---

## Observation Checklist

After triggering the module, verify on hardware:

- [ ] Step register advances: 100 → 110 → 120 → 130 → 140 → 900 → 1000
- [ ] Carrier/gripper moves toward sample station
- [ ] Gripper closes, picks up sample plate
- [ ] Arm moves to metal bath position
- [ ] Carrier is placed into metal bath slot
- [ ] `M_Signaling_Completed` becomes TRUE at step 1000
- [ ] After reset (write 0 to step), module returns to idle

## Troubleshooting

| Symptom | Likely Cause |
|---------|-------------|
| Step stays at 100, never advances | Condition check failing — check sensor states (`Synthesis.metal_bath1`, `Synthesis.Handing_types`) |
| Step jumps back to 0 | E-Stop triggered (`G_MasterControl.IN_Trigger_EStop`) or PLC in non-AUTO mode |
| Servo moves but stops mid-way | Position constant incorrect or axis alarm |
| Step reaches 900 but `M_Signaling_Completed` stays FALSE | Logic error in completion network — check LD rungs |
