# 剩余四个问题的解决方案

基于对 `DNA合成.xml` 中 `B_自动流程` 及相关代码的分析，现给出以下解决方案：

---

## 问题1：`G_Module_Process` 的实际 MW 地址

### 现状
- 当前 ST 代码使用 `G_Module_Process[9]` 作为原子服务的状态变量。
- 原始项目中已存在 `G_Process[9]`（类型为 `G_ProcessInformation` 的数组，大小 20），用于主流程步序控制。
- `G_Process` 未绑定固定地址（无 `address="%MW…"` 属性），由编译器自动分配。

### 解决方案（二选一）

#### 方案 A：直接使用现有的 `G_Process[9]`（推荐）
**优点**：与现有流程变量统一，无需新增全局变量，HMI 和上位机已熟悉该地址布局。  
**缺点**：原子服务与原始 F09 流程共用同一状态变量，不能同时运行。

修改 ST 文件：
- 将所有 `G_Module_Process[9]` 替换为 `G_Process[9]`
- 确保 `G_Process[9].M_Show_Step_AUTO` 和 `G_Process[9].M_Signaling_Completed` 的含义与原子服务一致

#### 方案 B：新建 `G_Module_Process` 并分配固定地址
若希望原子服务与原始流程完全独立，可在 GVL 中声明：

```pascal
VAR_GLOBAL RETAIN PERSISTENT
    G_Module_Process : ARRAY[0..19] OF G_ProcessInformation @ %MW51000;
END_VAR
```

地址选择 `%MW51000` 的原因：
- `%MW50000`–`%MW59999` 区间目前未被占用（见下方已用地址表）
- 为后续其他原子服务预留空间（每个模块可间隔 100 字）

### 已用 MW 地址表（取自 XML）
| 地址 | 变量 | 说明 |
|------|------|------|
| %MW20000 | G_zuobiao | 坐标 |
| %MW21000 | G_baojing | 报警 |
| %MW40000 | Call_Overall | 调用总控 |
| %MW43000 | Call_interactive | 交互调用 |
| %MW60000–%MW63003 | CCD/扫码/反馈 | 外设通信 |
| %MW41330–%MW41343 | PC 界面心跳 | 辅助 |

**结论**：建议采用方案 A（使用 `G_Process[9]`），除非明确需要独立状态变量。

---

## 问题2：PLC IP 地址和 Modbus TCP 端口

### 现状
- XML 中不包含网络配置信息（IP/端口）。
- 需从 PLC 硬件配置或项目设置中获取。

### 解决方案

#### 步骤 1：确认 PLC 的 IP 地址
- 默认静态 IP 可能是 `192.168.1.100`（汇川常用）
- 可通过 PLC 本体网口标签、InoProShop 项目设备配置或路由器 DHCP 列表查找。

#### 步骤 2：确认 Modbus TCP 端口
- 标准 Modbus TCP 端口为 **502**
- 若 PLC 启用了多协议，可能使用其他端口（如 5020、44818），需在 PLC 配置中查看“Modbus TCP 服务器”设置。

#### 步骤 3：C++ 测试代码示例
```cpp
// 使用 libmodbus 或类似库
modbus_t *ctx = modbus_new_tcp("192.168.1.100", 502);
if (modbus_connect(ctx) == -1) {
    fprintf(stderr, "Connection failed: %s\n", modbus_strerror(errno));
    return;
}

// 读取输入参数（假设地址 %MW50900）
uint16_t reg[2];
modbus_read_registers(ctx, 50900, 2, reg);
uint16_t sample_num = reg[0];   // .Sample_Num
int32_t plate_pos = (reg[1] << 16) | reg[2]; // .Plate_Pos（若为 DINT）

// 写入步序触发（假设 G_Process[9].M_Show_Step_AUTO 地址为 %MW50000 + 偏移）
modbus_write_register(ctx, 50000 + offset, 101);
```

#### 步骤 4：获取地址偏移量
若使用 `G_Process[9]`，需计算 `M_Show_Step_AUTO` 在数组中的偏移：
- 编译项目后，在 InoProShop 中打开“映射表”（Cross‑Reference）或“变量监控表”，搜索 `G_Process[9].M_Show_Step_AUTO`，可看到分配的 Modbus 地址（如 `%MW50012`）。

**结论**：IP 地址需现场确认，端口默认为 502；地址偏移需通过编译后的映射表获取。

---

## 问题3：`Synthesis.metal_bath1 / metal_bath2` 是 BOOL 还是 INT

### 现状
从 `G_Synthesis` 数据类型定义（第 4798 行起）中确认：

```xml
<variable name="metal_bath1">
  <type>
    <BOOL />
  </type>
  <documentation>
    <xhtml xmlns="http://www.w3.org/1999/xhtml"> 样品1金属浴1载具有无</xhtml>
  </documentation>
</variable>
<variable name="metal_bath2">
  <type>
    <BOOL />
  </type>
  <documentation>
    <xhtml xmlns="http://www.w3.org/1999/xhtml"> 样品2金属浴2载具有无</xhtml>
  </documentation>
</variable>
```

### 解决方案
- **ST 代码中应使用 `BOOL` 赋值**，与原始数据类型一致。
- 当前 ST 代码使用 `Synthesis.metal_bath1 := TRUE;` 是正确的。
- 原始 F09 流程中出现的 `:=1` 是 CODESYS 允许的隐式转换（整数 1 → BOOL TRUE），但建议保持风格统一，使用 `:= TRUE`。

**无需修改**，当前 ST 代码已正确。

---

## 问题4：夹爪光电传感器检查（原始问题6）

### 现状
原始 F09 流程在夹持完成后、移动至金属浴前，有一步 **“搬运夹爪光电判定”**（Step 210）。  
该步骤使用传感器 `G_Sensor[11].Input`（对应 `X02[15]`，注释为“搬运夹爪感应光电”）确认载具已被可靠夹持。

### 解决方案
在原子服务的步序链中插入光电检查步序，位置：**夹持完成（Step 160）之后，Z轴提升（Step 170）之前**。

#### 修改 ST 代码
1. **新增 Step 165**：
```pascal
(* ── Step 165：搬运夹爪光电判定 ── *)
165:
    (* 等待光电传感器确认载具已夹持 *)
    IF G_Sensor[11].Input THEN  (* 传感器接通表示载具在位 *)
        G_Process[9].M_Show_Step_AUTO := 170;
    END_IF
```

2. **调整 Step 160 的跳转目标**：
```pascal
160:
    ... 
    G_Process[9].M_Show_Step_AUTO := 165;  (* 原为 170 *)
```

3. **传感器极性说明**：
   - 从注释“搬运夹爪感应光电”及报警条目 `ALarm_15(搬运夹爪感应光电)` 推断，传感器**正常时常开，载具到位时闭合**（`G_Sensor[11].Input = TRUE`）。
   - 若实际极性相反，则条件改为 `NOT G_Sensor[11].Input`。

#### 硬件验证
- 半实物测试时，用手遮挡/松开传感器，观察步序是否正常通过。
- 若传感器未安装或暂不可用，可暂时注释此步，但正式运行前必须补回。

**结论**：光电检查是重要的安全互锁，应加入原子服务。

---

## 统一思想后的行动建议

1. **立即执行**：
   - 将 ST 代码中的 `G_Module_Process[9]` 全部改为 `G_Process[9]`（采用方案 A）。
   - 插入 Step 165（光电检查）并调整跳转。
   - 确认 `metal_bath1/2` 赋值使用 `:= TRUE`。

2. **硬件测试前准备**：
   - 联系硬件工程师确认 PLC IP 地址（或通过路由器查看）。
   - 在 InoProShop 中编译项目，打开映射表记录 `G_Process[9].M_Show_Step_AUTO` 和 `G_Process[9].M_Signaling_Completed` 的实际 Modbus 地址。
   - 将地址填入 C++ 测试代码。

3. **后续扩展**：
   - 为其他原子服务预留地址段（如 `%MW51000`–`%MW51999` 用于模块状态，`%MW52000`–`%MW52999` 用于输入参数）。
   - 编写通用的 C++ Modbus 封装类，支持多模块并发通信。

完成以上修改后，原子服务即可进入阶段二（硬件半实物验证）。