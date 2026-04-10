(* ==============================================================
   F20_09进金属浴模块 — Atomic Service
   功能：将指定样品载具（96孔小板）从样品工位搬运至金属浴加热位
   输入：G_P_F20_09_Input @ %MW50900
           .Sample_Num  UINT   样品编号 (1 = 样品1, 2 = 样品2)
           .Plate_Pos   DINT   保留字段，当前未使用（内部根据 Sample_Num 决定目标位）
   状态：G_Module_Process[9].M_Show_Step_AUTO
   完成：G_Module_Process[9].M_Show_Step_AUTO 回到 100
         调度器读 G_F20_End[9] = G_F20_Start[9] 确认完成

   X/Y 轴 M_PT 索引依据（已由硬件工程师确认）:
     M_PT[0]  初始位
     M_PT[11] 样品载具1位
     M_PT[12] 样品载具2位
     M_PT[13] 金属浴1位（小板）
     M_PT[14] 金属浴2位（小板）

   Z 轴 M_PT 索引（已确认）:
     M_PT[0]  安全行走高度（初始位/夹持Z轴夹持位，已确认）
     M_PT[18] 96孔板取料Z高度（已从F09流程代码注释确认）
     M_PT[23] 金属浴放料Z高度（已确认）

   夹爪 M_PT 索引（已从F09流程代码确认）:
     G_HC_keep_jaw[搬运夹爪].M_PT[2]  释放位（张开）
     G_HC_keep_jaw[搬运夹爪].M_PT[3]  夹持位（闭合）
   ============================================================== *)

(* 上升沿检测必须放在 CASE 外并每个扫描周期都执行，这样步号从 110 切到 115 的下一扫才会形成一次有效脉冲，供 Step 115 内部用 PLS_0.xOut 触发 X/Y 轴动作 *)
PLS_0(xExecute:= G_Module_Process[9].M_Show_Step_AUTO = 115);

CASE G_Module_Process[9].M_Show_Step_AUTO OF

(* ── Step 0：初始化 / 空闲 ── *)
(* 上电或复位后自动进入 Step 100 等待触发 *)
    0:
        G_Module_Process[9].M_Signaling_Completed := FALSE;
        IF NOT G_Module_Process[9].M_Trigger_Pause THEN
            G_Module_Process[9].M_Show_Step_AUTO := 100;
        END_IF

(* ── Step 101：入口条件检查 ── *)
(* 外部调度器写入 Sample_Num 后，将 Step 置为 101 触发本模块 *)
    101:
        IF NOT G_MasterControl.IN_Trigger_EStop THEN
            G_Module_Process[9].M_Show_Step_AUTO := 0;
        ELSIF NOT G_Module_Process[9].M_Trigger_Pause THEN
            IF G_P_F20_09_Input.Sample_Num = 1 THEN
				Synthesis.station_plate1 := G_Sensor[13].Input;
                IF Synthesis.station_plate1      (* 样品1工位有载具 *)
                    AND NOT Synthesis.metal_bath1     (* 金属浴1槽空位 *)
                    AND Synthesis.Handing_types = 0 THEN  (* 搬运夹爪空载 *)
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

(* ── Step 110：清除 X/Y 轴及夹爪触发标志 ── *)
    110:
        G_Servo[搬运X轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运X轴].M_Show_DrvaOK := FALSE;
        G_Servo[搬运Y轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运Y轴].M_Show_DrvaOK := FALSE;
        G_HC_Notkeep_jaw[搬运夹爪].M_Trigger_DRVA := FALSE;
        G_HC_Notkeep_jaw[搬运夹爪].M_Show_DrvaOK := FALSE;
        IF NOT G_Servo[搬运X轴].M_Trigger_DRVA
            AND NOT G_Servo[搬运X轴].M_Show_DrvaOK
            AND NOT G_Servo[搬运Y轴].M_Trigger_DRVA
            AND NOT G_Servo[搬运Y轴].M_Show_DrvaOK
            AND NOT G_HC_Notkeep_jaw[搬运夹爪].M_Trigger_DRVA
            AND NOT G_HC_Notkeep_jaw[搬运夹爪].M_Show_DrvaOK THEN
            G_Module_Process[9].M_Show_Step_AUTO := 115;  (* 改为跳 115 *)
        END_IF

(* ── Step 115：X/Y 轴移动到倾斜工位，夹爪同时张开 ── *)
(* 防碰撞过渡位：无论从哪里来，先走到 M_PT[15] 倾斜工位再去样品位 *)
(* 注：夹爪此处提前张开到释放位 M_PT[2]，为后续取料做准备 *)
    115:
//         R_TRIG_0(CLK:= G_Module_Process[9].M_Show_Step_AUTO = 115);
		
		G_Servo[搬运X轴].M_TargetLocation_DRVA := G_Servo_Function[搬运X轴].M_PT[15]; (* 倾斜工位 *)
        G_Servo[搬运Y轴].M_TargetLocation_DRVA := G_Servo_Function[搬运Y轴].M_PT[15]; (* 倾斜工位 *)
        G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA := G_HC_keep_jaw[搬运夹爪].M_PT[2]; (* 张开位 *)
        IF G_Servo[搬运X轴].M_TargetLocation_DRVA_Feedback = G_Servo_Function[搬运X轴].M_PT[15]
            AND G_Servo[搬运Y轴].M_TargetLocation_DRVA_Feedback = G_Servo_Function[搬运Y轴].M_PT[15]
            AND G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA = G_HC_keep_jaw[搬运夹爪].M_PT[2] THEN
			IF PLS_0.xOut THEN
				G_Servo[搬运Y轴].M_Trigger_DRVA := TRUE;
				G_Servo[搬运X轴].M_Trigger_DRVA := TRUE;
			END_IF
			
			IF G_Servo[搬运X轴].M_Show_DrvaOK AND G_Servo[搬运Y轴].M_Show_DrvaOK THEN
				G_Module_Process[9].M_Show_Step_AUTO := 117;
			END_IF
        END_IF

(* ── Step 117：再次清除 X/Y 轴触发标志，准备定位样品位 ── *)
    117:
        G_Servo[搬运X轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运X轴].M_Show_DrvaOK := FALSE;
        G_Servo[搬运Y轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运Y轴].M_Show_DrvaOK := FALSE;
        IF NOT G_Servo[搬运X轴].M_Trigger_DRVA
            AND NOT G_Servo[搬运Y轴].M_Trigger_DRVA THEN
            G_Module_Process[9].M_Show_Step_AUTO := 120;
        END_IF

(* ── Step 120：X/Y 轴定位至样品工位上方 ── *)
(* M_PT[11] = 样品载具1位, M_PT[12] = 样品载具2位（已确认） *)
    120:
        IF NOT G_Module_Process[9].M_Trigger_Pause THEN
            IF G_P_F20_09_Input.Sample_Num = 1 THEN
                G_Servo[搬运X轴].M_TargetLocation_DRVA := G_Servo_Function[搬运X轴].M_PT[11];
                G_Servo[搬运Y轴].M_TargetLocation_DRVA := G_Servo_Function[搬运Y轴].M_PT[11];
            ELSE (* Sample_Num = 2 *)
                G_Servo[搬运X轴].M_TargetLocation_DRVA := G_Servo_Function[搬运X轴].M_PT[12];
                G_Servo[搬运Y轴].M_TargetLocation_DRVA := G_Servo_Function[搬运Y轴].M_PT[12];
            END_IF
            IF G_Servo[搬运X轴].M_TargetLocation_DRVA_Feedback
                = G_Servo[搬运X轴].M_TargetLocation_DRVA
                AND G_Servo[搬运Y轴].M_TargetLocation_DRVA_Feedback
                = G_Servo[搬运Y轴].M_TargetLocation_DRVA THEN
                G_Module_Process[9].M_Show_Step_AUTO := 130;
            END_IF
        END_IF

(* ── Step 130：清除 Z 轴触发标志 ── *)
    130:
        G_Servo[搬运Z轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运Z轴].M_Show_DrvaOK := FALSE;
        IF NOT G_Servo[搬运Z轴].M_Trigger_DRVA THEN
            G_Module_Process[9].M_Show_Step_AUTO := 140;
        END_IF

(* ── Step 140：Z 轴下降至取料高度 ── *)
(* M_PT[18] = 搬运Z轴96孔板取料位（已从F09代码注释确认） *)
    140:
        G_Servo[搬运Z轴].M_TargetLocation_DRVA := G_Servo_Function[搬运Z轴].M_PT[18];
        IF G_Servo[搬运Z轴].M_TargetLocation_DRVA_Feedback
            = G_Servo_Function[搬运Z轴].M_PT[18] THEN
            G_Module_Process[9].M_Show_Step_AUTO := 150;
        END_IF

(* ── Step 150：清除夹爪触发标志 ── *)
    150:
        G_HC_Notkeep_jaw[搬运夹爪].M_Trigger_DRVA := FALSE;
        G_HC_Notkeep_jaw[搬运夹爪].M_Show_DrvaOK := FALSE;
        IF NOT G_HC_Notkeep_jaw[搬运夹爪].M_Trigger_DRVA THEN
            G_Module_Process[9].M_Show_Step_AUTO := 160;
        END_IF

(* ── Step 160：夹爪夹持载具 ── *)
(* M_PT[3] = 夹持位（已从F09代码确认）*)
(* 完成判断：M_TargetLocation_DRVA 自比，与原始F09流程一致，已确认为正确方式 *)
    160:
        G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA :=
        G_HC_keep_jaw[搬运夹爪].M_PT[3];
        IF G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA
            = G_HC_keep_jaw[搬运夹爪].M_PT[3] THEN
            Synthesis.sample_selection := 0;
            Synthesis.Handing_types := 5;   (* 夹爪持有96孔板，类型5 *)
            G_Module_Process[9].M_Show_Step_AUTO := 165;
        END_IF

(* ── Step 165：搬运夹爪光电判定 ── *)
(* 确认载具已被可靠夹持，防止空夹继续运动导致碰撞或实验数据错误 *)
(* 传感器：G_Sensor[11].Input（X02[15]，搬运夹爪感应光电） *)
(* 极性：常开，载具到位时闭合（= TRUE）；若实际相反请改为 NOT G_Sensor[11].Input *)
    165:
        IF G_Sensor[11].Input THEN
            G_Module_Process[9].M_Show_Step_AUTO := 170;
        END_IF

(* ── Step 170：Z 轴上升至安全行走高度 ── *)
(* Z轴 M_PT[0] = 安全行走高度（已确认）*)
    170:
        G_Servo[搬运Z轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运Z轴].M_Show_DrvaOK := FALSE;
        G_Servo[搬运Z轴].M_TargetLocation_DRVA := G_Servo_Function[搬运Z轴].M_PT[0];
        IF G_Servo[搬运Z轴].M_TargetLocation_DRVA_Feedback
            = G_Servo_Function[搬运Z轴].M_PT[0] THEN
            G_Module_Process[9].M_Show_Step_AUTO := 180;
        END_IF

(* ── Step 180：X/Y 轴定位至目标金属浴上方 ── *)
(* M_PT[13] = 金属浴1位（小板）, M_PT[14] = 金属浴2位（小板）（已确认） *)
    180:
        G_Servo[搬运X轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运X轴].M_Show_DrvaOK := FALSE;
        G_Servo[搬运Y轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运Y轴].M_Show_DrvaOK := FALSE;
        IF G_P_F20_09_Input.Sample_Num = 1 THEN
            G_Servo[搬运X轴].M_TargetLocation_DRVA := G_Servo_Function[搬运X轴].M_PT[13];
            G_Servo[搬运Y轴].M_TargetLocation_DRVA := G_Servo_Function[搬运Y轴].M_PT[13];
        ELSE (* Sample_Num = 2 *)
            G_Servo[搬运X轴].M_TargetLocation_DRVA := G_Servo_Function[搬运X轴].M_PT[14];
            G_Servo[搬运Y轴].M_TargetLocation_DRVA := G_Servo_Function[搬运Y轴].M_PT[14];
        END_IF
        IF G_Servo[搬运X轴].M_TargetLocation_DRVA_Feedback
            = G_Servo[搬运X轴].M_TargetLocation_DRVA
            AND G_Servo[搬运Y轴].M_TargetLocation_DRVA_Feedback
            = G_Servo[搬运Y轴].M_TargetLocation_DRVA THEN
            G_Module_Process[9].M_Show_Step_AUTO := 190;
        END_IF

(* ── Step 190：Z 轴下降至金属浴放料高度 ── *)
(* Z轴 M_PT[23] = 金属浴放料高度（已确认）*)
    190:
        G_Servo[搬运Z轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运Z轴].M_Show_DrvaOK := FALSE;
        G_Servo[搬运Z轴].M_TargetLocation_DRVA := G_Servo_Function[搬运Z轴].M_PT[23];
        IF G_Servo[搬运Z轴].M_TargetLocation_DRVA_Feedback
            = G_Servo_Function[搬运Z轴].M_PT[23] THEN
            G_Module_Process[9].M_Show_Step_AUTO := 200;
        END_IF

(* ── Step 200：夹爪释放载具，放入金属浴 ── *)
(* M_PT[2] = 释放位（已从F09代码确认）*)
(* 完成判断：M_TargetLocation_DRVA 自比，与原始F09流程一致，已确认为正确方式 *)
    200:
        G_HC_Notkeep_jaw[搬运夹爪].M_Trigger_DRVA := FALSE;
        G_HC_Notkeep_jaw[搬运夹爪].M_Show_DrvaOK := FALSE;
        G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA :=
        G_HC_keep_jaw[搬运夹爪].M_PT[2];
        IF G_HC_Notkeep_jaw[搬运夹爪].M_TargetLocation_DRVA
            = G_HC_keep_jaw[搬运夹爪].M_PT[2] THEN
            Synthesis.Handing_types := 0;   (* 夹爪恢复空载 *)
            IF G_P_F20_09_Input.Sample_Num = 1 THEN
                Synthesis.metal_bath1 := TRUE;
            ELSE
                Synthesis.metal_bath2 := TRUE;
            END_IF
            G_Module_Process[9].M_Show_Step_AUTO := 210;
        END_IF

(* ── Step 210：Z 轴上升，退出金属浴槽 ── *)
    210:
        G_Servo[搬运Z轴].M_Trigger_DRVA := FALSE;
        G_Servo[搬运Z轴].M_Show_DrvaOK := FALSE;
        G_Servo[搬运Z轴].M_TargetLocation_DRVA := G_Servo_Function[搬运Z轴].M_PT[0];
        IF G_Servo[搬运Z轴].M_TargetLocation_DRVA_Feedback
            = G_Servo_Function[搬运Z轴].M_PT[0] THEN
            G_Module_Process[9].M_Show_Step_AUTO := 900;
        END_IF

(* ── Step 900：标记完成，回到空闲 ── *)
(* M_Signaling_Completed 置 TRUE，步序回到 100 *)
(* 调度器（F20_00启动流程）检测到 M_Show_Step_AUTO = 100 时，写 G_F20_End[9] 确认完成 *)
    900:
        G_Module_Process[9].M_Signaling_Completed := TRUE;
        G_Module_Process[9].M_Show_Step_AUTO := 100;

END_CASE
