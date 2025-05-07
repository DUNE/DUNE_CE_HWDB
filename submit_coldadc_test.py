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


def SubmitColdADCCTSQCTest():
    tests = [
    "Test Date",
    "Test Time",
    "Test Location",
    "Operator Name",
    "Registers Read Test",
    "Soft Reset Test",
    "Average ADC Noise (uV)",
    "External VDDA Voltage",
    "External VDDA Power DIFF",
    "External VDDA Power SE mode"
    ]

#    datasheet = [["" for _ in range(10)] for _ in range(2)]

#    for i in range(len(tests)):
#        datasheet[0][i] = tests[i]


    getnames = os.popen("ls -d  /scratch/mtzanov/DUNE_CE/ColdADC/test_results/*")
    filenames = getnames.readlines()
    prev = 0
    for fn in filenames:
        datasheet = [[None for _ in range(10)] for _ in range(2)]

        for i in range(len(tests)):
            datasheet[0][i] = tests[i]

#        print (fn)
        fn = fn.rstrip()
        sn = fn.split("_")
#        print(sn[1],"\n",sn[2],"\n",sn[3],"\n",sn[4],"\n",sn[5],"\n",sn[6])
        time = sn[6].split("T")
        asic = sn[2].split("/")
        date = time[0][0:4]+"/"+time[0][4:6]+"/"+time[0][6:8]
        testtime = time[1][0:2]+":"+time[1][2:4]
        serial = sn[3]+"-"+sn[4]
        testtype = sn[5]
        testfilename = "ls "+fn+"/*.txt"
    #if(prev != sn[3]):
#        print (asic[1],", ",serial, ", ", sn[4], ", ", date, ", ", testtime)
    #prev = sn[3]
        datasheet[1][0] = "\""+date+"\""
        datasheet[1][1] = "\""+testtime+"\""
        datasheet[1][2] = "\"LSU\""
        getfile = os.popen(testfilename)
        testfile = getfile.readlines()
        testfile = testfile[0].rstrip()
#        print (testfile)
        
        plotfiles = "ls "+fn+"/*.png"       
        getplotfiles = os.popen(plotfiles)
        filelist = getplotfiles.readlines()

        with open(testfile) as f:
            for line in f:
#                print(line.strip())
                test = line.strip()
                test1 = test.split(":")
                index = None
                value = None
                if test1[0] in tests:
                    index = tests.index(test1[0])
                    value = test1[1].split(" ")
#                    print(test1[0], test1[1])
                test2 = test.split("=")
                if test2[0] in tests:
                    index = tests.index(test2[0])
                    value = test2[1].split(" ")
#                print(index, value)
                if index != None and value != None:
                    if index < 6:
                        datasheet[1][index] = "\""+value[1]+"\""
                    elif index == 6 and datasheet[1][index] == None:
                        datasheet[1][index] = str(int(float(value[2])))
                    elif index > 6:
                        datasheet[1][index] = value[1]
                    
        if testtype == "rt":
            testname = "\"RoomT QC Test\""
        elif testtype == "ln":
            testname = "\"CryoT QC Test\""

        if serial == "2315-02186" or serial == "2315-02159":
            
            #print(filelist)
            print(datasheet)
            print(testtype, testname)

            dune_ce_hwdb.EnterItemToHWDB("coldadc_p2prep", serial, "LSU", "US", "", "59", "", "2023-08-10 00:00:00")
            dune_ce_hwdb.EnterTestToHWDB("coldadc_p2prep", serial, testname, "No comment", datasheet)
            dune_ce_hwdb.EnterFileToTest("coldadc_p2prep", serial, testname, datasheet, filelist)

if __name__ == '__main__':

    SubmitColdADCCTSQCTest()

