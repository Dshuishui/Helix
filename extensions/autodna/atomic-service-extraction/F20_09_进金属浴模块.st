VAR_GLOBAL
	G_Servo: ARRAY[0..19] OF Servo_Control;                               // 伺服控制

	{attribute 'ElemComment':='([Input(吸头进料平台接近光电),In_On(吸头进料平台接近光电),In_Off(吸头进料平台接近光电)]),([Input(吸头出料平台接近光电),In_On(吸头出料平台接近光电),In_Off(吸头出料平台接近光电)]),([Input(吸头料仓1接近光电),In_On(吸头料仓1接近光电),In_Off(吸头料仓1接近光电)]),([Input(吸头料仓2接近光电),In_On(吸头料仓2接近光电),In_Off(吸头料仓2接近光电)]),([Input(吸头料仓3接近光电),In_On(吸头料仓3接近光电),In_Off(吸头料仓3接近光电)]),([Input(吸头料仓4接近光电),In_On(吸头料仓4接近光电),In_Off(吸头料仓4接近光电)]),([Input(试剂进料平台接近光电),In_On(试剂进料平台接近光电),In_Off(试剂进料平台接近光电)]),([Input(试剂出料平台接近光电),In_On(试剂出料平台接近光电),In_Off(试剂出料平台接近光电)]),([Input(试剂备用平台接近光电),In_On(试剂备用平台接近光电),In_Off(试剂备用平台接近光电)]),([Input(废液盒1接近光电),In_On(废液盒1接近光电),In_Off(废液盒1接近光电)]),([Input(废液盒2接近光电),In_On(废液盒2接近光电),In_Off(废液盒2接近光电)]),([Input(搬运夹爪感应光电),In_On(搬运夹爪感应光电),In_Off(搬运夹爪感应光电)]),([Input(备用),In_On(备用),In_Off(备用)]),([Input(合成工位1接近光电),In_On(合成工位1接近光电),In_Off(合成工位1接近光电)]),([Input(合成工位2接近光电),In_On(合成工位2接近光电),In_Off(合成工位2接近光电)]),([Input(0度试剂接近光电),In_On(0度试剂接近光电),In_Off(0度试剂接近光电)]),([Input(常温试剂接近光电),In_On(常温试剂接近光电),In_Off(常温试剂接近光电)]),9([Input(备用),In_On(备用),In_Off(备用)]),5()'}
	G_Sensor:ARRAY[0..30] OF Sensor_Control;                              // 传感器控制
	G_Process: ARRAY[0..19] OF G_ProcessInformation;                      // 流程控制
	G_Module_Process: ARRAY[0..30] OF G_ProcessInformation;		          // 流程控制_模块化
	G_MasterControl: G_MasterControl;                                     // 总控
	G_AlarmProcessing: G_AlarmInformation;                                // 报警处理
	G_UploadContent_HMICompile:G_UploadContent_HMICompile;                //G上传内容HMI编辑项
	G_Version:G_Version;                                                  //版本信息
	G_STRESS: STRESS;                                                     //G_温度及压力
	G_CCD_Temp: ARRAY[0..4] OF CCD_Temp;                                  //视觉临时变量
	G_SF_Temp:  ARRAY[0..4] OF SF_Temp;                                   //SF临时变量
	G_Scaner_Temp:  ARRAY[0..4] OF Scaner_Temp;                           //扫码临时变量
	G_SuperSUPro:SuperSUPro;                                              //用户操作

	F00_Temp:F00_Temp;                                                    //F00非保持变量
	{attribute 'ElemComment':='ALarm_1(吸头料仓1接近光电),ALarm_2(吸头料仓2接近光电),ALarm_3(吸头料仓3接近光电),ALarm_4(吸头料仓4接近光电),ALarm_5(0度试剂接近光电),ALarm_6(常温试剂接近光电),ALarm_7(合成工位1接近光电),ALarm_8(合成工位2接近光电 ),ALarm_9(吸头出料平台接近光电),ALarm_10(试剂出料平台接近光电),ALarm_11(吸头进料平台接近光电 ),ALarm_12(试剂进料平台接近光电 ),ALarm_13(废液盒1接近光电 ),ALarm_14(废液盒2接近光电  ),ALarm_15(搬运夹爪感应光电)'}
	F12_Temp:F12_Temp;                                                    //F12非保持变量
	F14_Temp:F14_Temp;                                                    //F14非保持变量
	P_First_Run:BOOL ;
	P_ON:BOOL ;
	G_Hmi_Heartbeat:INT;                                                  //触摸屏心跳
	X00:ARRAY[0..15] OF BOOL ;
	X01:ARRAY[0..15] OF BOOL ;
	X02:ARRAY[0..15] OF BOOL ;
	X03:ARRAY[0..15] OF BOOL ;
	X04:ARRAY[0..15] OF BOOL ;
	X05:ARRAY[0..15] OF BOOL ;
	X06:ARRAY[0..15] OF BOOL ;
	X07:ARRAY[0..15] OF BOOL ;
	X08:ARRAY[0..15] OF BOOL ;
	X09:ARRAY[0..15] OF BOOL ;
	X10:ARRAY[0..15] OF BOOL ;
	X11:ARRAY[0..15] OF BOOL ;
	X12:ARRAY[0..15] OF BOOL ;
	X13:ARRAY[0..15] OF BOOL ;
	X14:ARRAY[0..15] OF BOOL ;
	X15:ARRAY[0..15] OF BOOL ;
	X16:ARRAY[0..15] OF BOOL ;
	X17:ARRAY[0..15] OF BOOL ;
	X18:ARRAY[0..15] OF BOOL ;
	X19:ARRAY[0..15] OF BOOL ;	

	Y00:ARRAY[0..15] OF BOOL ;
	Y01:ARRAY[0..15] OF BOOL ;
	Y02:ARRAY[0..15] OF BOOL ;
	Y03:ARRAY[0..15] OF BOOL ;
	Y04:ARRAY[0..15] OF BOOL ;
	Y05:ARRAY[0..15] OF BOOL ;
	Y06:ARRAY[0..15] OF BOOL ;
	Y07:ARRAY[0..15] OF BOOL ;
	Y08:ARRAY[0..15] OF BOOL ;
	Y09:ARRAY[0..15] OF BOOL ;
	Y10:ARRAY[0..15] OF BOOL ;
	Y11:ARRAY[0..15] OF BOOL ;	
	
END_VAR
VAR_GLOBAL RETAIN PERSISTENT
	G_Servo_Function AT %MB132632 : ARRAY [0..19] OF Servo_Function;// 伺服功能
	G_Function AT %MB147416 : G_FunctionSelection;// 功能
	G_SystemTime AT %MB147608 : G_SystemTime;//系统时间
	G_DeviceStatus AT %MB147724 : ARRAY [0..6] OF G_DeviceStatus;// 设备状态收集
	G_ProductionState AT %MB148368 : ARRAY [0..6] OF G_ProductionState;// 产品状态收集
	MES_DATA_EquipmentStatus AT %MB151728 : MES_DATA_EquipmentStatus;//MES收集-设备状态
	MES_DATA_ProductionState AT %MB151912 : MES_DATA_ProductionState;//MES收集-生产状态
	MES_DATA_ProductStatus AT %MB151940 : ARRAY [0..14] OF MES_DATA_ProductStatus;//MES收集-产品状态
	G_UploadContent_HMICompile_SAVE AT %MB161168 : G_UploadContent_HMICompile_SAVE;//G上传内容HMI编辑项保存
	G_Userinfo AT %MB162932 : Userinfo;                                 //用户存储
    G_CCD_Trigger      AT %MW60000 : ARRAY[0..4] OF CCD_Trigger;       //相机触发
	G_Scaner_Trigger   AT %MW60050 : ARRAY[0..4] OF Scaner_Trigger;    //扫码枪触发
	G_SF_Trigger       AT %MW60080 : ARRAY[0..4] OF SF_Trigger;        //SF触发
	G_PLC_TO_CCD       AT %MW60100 : ARRAY[0..4] OF PLC_TO_CCD;        //CCD控制
	G_Scaner_Control   AT %MW60260 : ARRAY[0..4] OF Scaner_Control;    //扫码枪控制
	G_SF_Control       AT %MW60270 : ARRAY[0..4] OF SF_Control;        //SF控制
	G_CCD_TO_PLC       AT %MW61000 : ARRAY[0..4] OF CCD_TO_PLC;        //相机反馈
	G_Scaner_Feedback  AT %MW61640 : ARRAY[0..4] OF Scaner_Feedback;   //扫码枪反馈
	G_SF_Feedback      AT %MW62740 : ARRAY[0..4] OF SF_Feedback;       //SF反馈
    G_Heartbeat_PC     AT %MW62998 : UINT;//PC整机心跳
	G_ModelSwitching   AT %MW62999 : UINT;//机种切换
    G_PersistentMonthTrans  AT %MW63001 : UINT;//月保持变量中转
	G_PersistentYearTrans  AT %MW63003 : UINT;//年保持变量中转
    F00_RetainVariable AT %MB170296 : F00_RetainVariable;//F00保持变量
	F12_RetainVariable AT %MB170920 : F12_RetainVariable;//F12保持变量
	F14_RetainVariable AT %MB171024 : F14_RetainVariable;//F14保持变量
	G_Speed_staging AT %MB171336 : ARRAY [0..19] OF REAL;
	CCD_Calibration_testing AT %MB171752 : ARRAY [0..4] OF CCD_CAL_TEST;// CCD调试和测试功能
	G_DataAnalysis AT %MB171416 : G_DataAnalysis数据分析;
	G_CCD_Retain AT %MB172072 : ARRAY [0..4] OF CCD_Retain;//CCD保持变量
	G_SF_Retain AT %MB172500 : ARRAY [0..4] OF SF_Retain;//SF保持变量
	G_Scaner_Retain AT %MB172600: ARRAY [0..4] OF Scaner_Retain;//扫码保持变量
	G_Sensor_Function AT %MB173000 : ARRAY [0..19] OF Sensor_Function;// 传感器功能
	G_HC_keep_jaw AT %MB145352 : ARRAY [0..6] OF HC_keep_jaw;// 夹爪控制
END_VAR
VAR_GLOBAL
	G_HC_Notkeep_jaw : ARRAY [0..6] OF HC_Notkeep_jaw;// 夹爪控制（非保持型）
	// 移液枪映射
	Pipette_gun: Pipette_gun;
END_VAR
VAR_GLOBAL RETAIN PERSISTENT
	// 移液枪保持型变量
	Pipette_maintain AT %MB131128 : Pipette_maintain;
END_VAR
VAR_GLOBAL
	// 移液枪非保持型变量
	Pipette_NOmaintain: Pipette_NOmaintain;
END_VAR
VAR_GLOBAL RETAIN PERSISTENT
	// 样品1碱基序列！！！！
	G_BasicGroup1 AT %MB173160 : ARRAY [0..96] OF STRING(19);
END_VAR
VAR_GLOBAL
	// 样品1碱基字符长度
	G_LENGTH1: ARRAY [0..96] OF UINT;
	// 样品1碱基字符长度最大值
	G_Baselength1: UINT;
END_VAR
VAR_GLOBAL RETAIN PERSISTENT
	// 样品2碱基序列！！！！
	G_BasicGroup2 AT %MB181017 : ARRAY [0..96] OF STRING(19);
END_VAR
VAR_GLOBAL
	// 样品2碱基字符长度
	G_LENGTH2: ARRAY [0..96] OF UINT;
	// 样品2碱基字符长度最大值
	G_Baselength2: UINT;
	// 样品碱基字符分隔
	G_separate: ARRAY [0..96] OF G_StringDecomposing;
END_VAR
VAR_GLOBAL RETAIN PERSISTENT
	// 合成数据！！！！
	Synthesis AT %MB188876 : G_Synthesis;
END_VAR
VAR_GLOBAL
	// Z轴阵列
	G_zhenlieZ: HC_zhenlieZ;
	// 96孔板阵列
	G_zhenlie: HC_zhenlie96;
END_VAR
VAR_GLOBAL RETAIN PERSISTENT
	// 1步序(1试剂叫料，2枪头叫料，
	Step_sequence1 AT %MB145828 : UINT;
	// 2步序(1试剂叫料，2枪头叫料，
	Step_sequence2 AT %MB145830 : UINT;
END_VAR
VAR_GLOBAL
	// 带料复位
	FReset_material: BOOL;
	// 无料复位
	FNo_material: BOOL;
END_VAR
VAR_GLOBAL RETAIN PERSISTENT
	// 孵育时间
	Fuyu_Time1 AT %MB131072 : TIME;
	// 孵育计时
	Fuyu_Jishi1 AT %MB131076 : TIME;
	// 孵育剩余时间
	Fuyu_Shengyu1 AT %MB131080 : TIME;
	// 孵育时间(1.3分钟，2.20分钟，3.30分钟）
	Fuyu_ShiJian1 AT %MB131084 : ARRAY [0..3] OF TIME;
	// 孵育时间
	Fuyu_Time2 AT %MB131100 : TIME;
	// 孵育计时
	Fuyu_Jishi2 AT %MB131104 : TIME;
	// 孵育剩余时间
	Fuyu_Shengyu2 AT %MB131108 : TIME;
	// 孵育时间
	Fuyu_ShiJian2 AT %MB131112 : ARRAY [0..3] OF TIME;
	// 数字孪生
	G_zuobiao AT %MW20000: G_shuziluansheng;
	// 数字孪生报警
	{attribute 'ElemComment':='baojing([201()])'}
	G_baojing AT %MW21000: G_LuanShengAlarm;
	// 数字孪生报警
	{attribute 'ElemComment':='baojing([201()])'}
	中转枢纽 AT %MB147382 : BOOL;
	// 数字孪生报警
	{attribute 'ElemComment':='baojing([201()])'}
	紧急通道 AT %MB147383 : BOOL;
	// 总控交互信号
	{attribute 'ElemComment':='baojing([201()])'}
	Call_Overall AT %MW40000: Call_zongkong;
	// 地轨交互信号
	{attribute 'ElemComment':='baojing([201()])'}
	Call_interactive AT %MW43000 : Station_Data_Keep;
	
	G_P_F20_09_Input AT %MW50900 : S09_Module_Input;   // F20_09模块输入参数
END_VAR
VAR_GLOBAL
	// 扫码样品SN
	liuzhuan_SN: ARRAY [0..2] OF STRING(19);
	// 扫码样品SN
	newVarGlobal: ARRAY [0..2] OF STRING(19);
END_VAR
