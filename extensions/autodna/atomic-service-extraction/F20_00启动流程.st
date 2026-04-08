IF G_MasterControl.IN_Trigger_EStop THEN
	FOR i:=1 TO 30 DO
		IF i<>9 AND i<>12 AND i<>13 AND i<>18 AND i<>19 AND i<>20 AND i<>22 AND i<>21 AND i<>25 AND i<>26 THEN
			CONTINUE;
		END_IF
		
		IF G_F20_Start[i] = 0 THEN
			G_F20_Record[i] := 0;
			G_F20_End[i] := 0;
			CONTINUE;
		END_IF
		
		IF G_F20_Start[i] <> G_F20_Record[i] AND 
// 			G_F20_Start[i] <> 0 AND
			G_Module_Process[i].M_Show_Step_AUTO = 100 THEN
			G_F20_Record[i] := G_F20_Start[i];
			IF G_F20_Record[i] = G_F20_Start[i] THEN
				G_Module_Process[i].M_Show_Step_AUTO := 101;
			END_IF
		ELSIF G_Module_Process[i].M_Show_Step_AUTO = 100 THEN
			G_F20_End[i] := G_F20_Record[i];
		END_IF
	END_FOR
END_IF
