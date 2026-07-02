import datetime
import socket
import os
import os.path
import pwd
import sys
import glob
import subprocess
import array
import dune_ce_hwdb


def SubmitCOLDATAtest():
    tests = [
        "Test Date",
        "Test Time",
        "Test Location",
        "Operator Name",
        "Test 0 Time",
        "ASICDAC_CALI_CHK",
        "Test 1 Time",
        "CD0_GPIO",
        "CD1_GPIO",
        "SPI_config",
        "FAST_CMD_Reset",
        "Post-Hard_Reset",
        "Post-Soft_Reset",
        "Test 2 Time",
        "U1_Left_CMOS",
        "U1_Left_LVDS",
        "U2_Right_CMOS",
        "U2_Right_LVDS",
        "ADCs_U1_Left_primary",
        "Data_U1_Left_primary",
        "ADCs_U2_Right_primary",
        "Data_U2_Right_primary",
        "Test 3 Time",
        "PC0_BAND_0x20_PLS",
        "PC1_BAND_0x25_PLS",
        "PC2_BAND_0x26_PLS",
        "PC0_BAND_0x20_Power",
        "PC1_BAND_0x25_Power",
        "PC2_BAND_0x26_Power",
        "PC3_LVDS_CUR_0x0_PLS",
        "PC4_LVDS_CUR_0x2_PLS",
        "PC5_LVDS_CUR_0x7_PLS",
        "PC3_LVDS_CUR_0x0_Power",
        "PC4_LVDS_CUR_0x2_Power",
        "PC5_LVDS_CUR_0x7_Power",
        "Test 4 Time",
        "PLL_Locked",
        "Test 5 Time",
        "FC_ACT_rst_adcs",
        "FC_ACT_CLR_SAVES",
        "FC_ACT_SAVE_STATUS",
        "FC_ACT_Pre_EDGE_SYNC",
        "FC_ACT_Post_EDGE_SYNC",
        "FC_ACT_Post_EDGE_SYNC_IDLE",
        "FC_ACT_RST_LARASIC",
        "Test 6 Time",
        "ADC_pattern_LVDS_CUR_0 Pulse Response",
        "ADC_pattern_LVDS_CUR_1 Pulse Response",
        "ADC_pattern_LVDS_CUR_2 Pulse Response",
        "ADC_pattern_LVDS_CUR_3 Pulse Response",
        "ADC_pattern_LVDS_CUR_4 Pulse Response",
        "ADC_pattern_LVDS_CUR_5 Pulse Response",
        "ADC_pattern_LVDS_CUR_6 Pulse Response",
        "ADC_pattern_LVDS_CUR_7 Pulse Response",
        "ADC_pattern_LVDS_CUR_0 Power Consumption",
        "ADC_pattern_LVDS_CUR_1 Power Consumption",
        "ADC_pattern_LVDS_CUR_2 Power Consumption",
        "ADC_pattern_LVDS_CUR_3 Power Consumption",
        "ADC_pattern_LVDS_CUR_4 Power Consumption",
        "ADC_pattern_LVDS_CUR_5 Power Consumption",
        "ADC_pattern_LVDS_CUR_6 Power Consumption",
        "ADC_pattern_LVDS_CUR_7 Power Consumption",
        "Test 7 Time",
        "U1_CD1",
        "U2_CD2",
        "CD VDDA",
        "CD VDDD",
        "FE VDDA",
        "CD VDDIO (CUR_0)",
        "CD VDDIO (CUR_1)",
        "CD VDDIO (CUR_2)",
        "CD VDDIO (CUR_3)",
        "CD VDDIO (CUR_4)",
        "CD VDDIO (CUR_5)",
        "CD VDDIO (CUR_6)",
        "CD VDDIO (CUR_7)",
        "CD VDDCORE",
        "PLL Lock Range (Lower Bound)",
        "PLL Lock Range (Upper Bound)"
    ]
    
    getnames = os.popen("ls -d /mnt/c/Users/ppd-cap-WD-137552/Tested/*/*")
    filenames = getnames.readlines()
    #print(filenames)
    
    for fn in filenames[len(filenames)-1:]:
        datasheet0 = [[None for _ in range(79)] for _ in range(2)]
        datasheet1 = [[None for _ in range(79)] for _ in range(2)]

        for i in range(len(tests)):
            #print(len(tests))
            datasheet0[0][i] = tests[i]
            datasheet1[0][i] = tests[i]

        #print (fn)
        fn = fn.rstrip()
        sn = fn.split("_")
        #print(sn[1],"\n",sn[2],"\n",sn[3],"\n",sn[4],"\n")
        time = sn[1]
        date = time[0:4]+"/"+time[4:6]+"/"+time[6:8]
        testtime = time[8:10]+":"+time[10:12]
        #print(len(sn[6]))
        if(len(sn[6]) == 9):
            serial0 = sn[6][5:9] + "-" + sn[6][0:5]
            serial1 = sn[7][5:9] + "-" + sn[7][0:5]
        elif(len(sn[6]) == 8):
            serial0 = sn[6][4:8] + "-0" + sn[6][0:4]
            serial1 = sn[7][4:8] + "-0" + sn[7][0:4]
        testtype = sn[4][5:8]
        #print (serial0, serial1, testtime, date, testtype)
        testfilename0 = fn+ "/hwdb_CD0.txt"
        testfilename1 = fn+ "/hwdb_CD1.txt" 
            
        if os.path.exists(testfilename0): # and time.startswith("20250918") :
            
            datasheet0[1][0] = "\""+date+"\""
            datasheet0[1][1] = "\""+testtime+"\""
            datasheet0[1][2] = "\"FNAL\""
            datasheet0[1][3] = "\"jgoudeau\""
            datasheet1[1][0] = "\""+date+"\""
            datasheet1[1][1] = "\""+testtime+"\""
            datasheet1[1][2] = "\"FNAL\""
            datasheet1[1][3] = "\"jgoudeau\""
            
            plotfiles = "ls "+fn+"/*.png"       
            getplotfiles = os.popen(plotfiles)
            filelist = getplotfiles.readlines()
    #        print (testfile)
            
            with open(testfilename0) as f:
                for line in f:
    #                print(line.strip())
                    test = line.strip()
                    #print(test)
                    test1 = test.split(",")
                    #print(test1, test1[0])
                    index = None
                    value = None
                    if test1[0] in tests:
                        index = tests.index(test1[0])
                        value = test1[1].split(" ")
                    test2 = test.split(":")
                    if test2[0] in tests:
                        index = tests.index(test2[0])
                        value = test2[1].split(" ")
                        #print(index, value, test2)
                    if index != None and value != None:
                        if index < 63:
                            if len(test2) == 3:
                                datasheet0[1][index] = "\""+test2[2].lstrip(' ')+"\""
                            elif len(test2) == 4:
                                datasheet0[1][index] = "\""+test2[1].lstrip(' ')+ ":" + test2[2] + ":" + test2[3] + "\""
                            else:
                                datasheet0[1][index] = "\""+value[1]+"\""
    #                    elif index == 6 and datasheet[1][index] == None:
    #                        datasheet[1][index] = str(int(float(value[2])))
                        elif index > 64:
                            datasheet0[1][index] = value[1]
                        elif index > 62:
                            datasheet0[1][index] = "\""+test2[1].lstrip(' ')+"\""

            
            with open(testfilename1) as f:
                for line in f:
    #                print(line.strip())
                    test = line.strip()
                    #print(test)
                    test1 = test.split(",")
                    #print(test1, test1[0])
                    index = None
                    value = None
                    if test1[0] in tests:
                        index = tests.index(test1[0])
                        value = test1[1].split(" ")
                        #print("match" ,test1[0], test1[1])
                    test2 = test.split(":")
                    #print(test2, test2[0])
                    if test2[0] in tests:
                        index = tests.index(test2[0])
                        value = test2[1].split(" ")
                    #print(index, value, test2[0])
                    if index != None and value != None:
                        if index < 63:
                            if len(test2) == 3:
                                datasheet1[1][index] = "\""+test2[2].lstrip(' ')+"\""
                            elif len(test2) == 4:
                                datasheet1[1][index] = "\""+test2[1].lstrip(' ')+ ":" + test2[2] + ":" + test2[3] + "\""
                            else:
                                datasheet1[1][index] = "\""+value[1]+"\""
    #                    elif index == 6 and datasheet[1][index] == None:
    #                        datasheet[1][index] = str(int(float(value[2])))
                        elif index > 64:
                            datasheet1[1][index] = value[1]
                        elif index > 62:
                            datasheet1[1][index] = "\""+test2[1].lstrip(' ')+"\""                            
                        
            if (testtype == "rt") or (testtype == "RT") :
                testname = "\"QC Test (RoomT)\""
                
            #print(testtype, testname)
            if(datasheet0[1][64] != None):
                
                #for test, result in zip(datasheet1[0],datasheet1[1]):
                    #print(test, result)
                    
                dune_ce_hwdb.EnterItemToHWDB("coldata_e4prb2", serial0, "FNAL", "US", "", "59", "", "2023-08-10 12:00:00")
                dune_ce_hwdb.EnterTestToHWDB("coldata_e4prb2", serial0, testname, "No comment", datasheet0)
                dune_ce_hwdb.EnterFileToTest("coldata_e4prb2", serial0, testname, datasheet0, filelist)
                
                dune_ce_hwdb.EnterItemToHWDB("coldata_e4prb2", serial1, "FNAL", "US", "", "59", "", "2023-08-10 12:00:00")
                dune_ce_hwdb.EnterTestToHWDB("coldata_e4prb2", serial1, testname, "No comment", datasheet1)
                dune_ce_hwdb.EnterFileToTest("coldata_e4prb2", serial1, testname, datasheet1, filelist)

if __name__ == '__main__':

    SubmitCOLDATAtest()

