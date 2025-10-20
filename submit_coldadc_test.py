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
        ofs = len(sn)
        timeofs = ofs - 1
        testofs = ofs - 2
        serofs = ofs - 3
        batofs = ofs - 4
        asicofs = ofs - 5

        time = sn[timeofs].split("T")
        asic = sn[asicofs].split("/")
        date = time[0][0:4]+"/"+time[0][4:6]+"/"+time[0][6:8]
        testtime = time[1][0:2]+":"+time[1][2:4]
        if sn[serofs] == "2422" or sn[serofs] == "2502":
            serial = sn[serofs]+"-"+sn[batofs]
        else:
            serial = sn[batofs]+"-"+sn[serofs]
        testtype = sn[testofs]
        testfilename = "ls "+fn+"/*.txt"


#        time = sn[6].split("T")
#        asic = sn[2].split("/")
#        date = time[0][0:4]+"/"+time[0][4:6]+"/"+time[0][6:8]
#        testtime = time[1][0:2]+":"+time[1][2:4]
#        serial = sn[3]+"-"+sn[4]
#        testtype = sn[5]
#        testfilename = "ls "+fn+"/*.txt"
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
 
#        pdf_plot_report_name = fn+"/coldadc_qc_report_"+serial+"_"+testtype+"_"+sn[6]+".pdf"
#        convert_to_pdf_command = "convert "+fn+"/*.png "+pdf_plot_report_name
        plotfiles = "ls "+fn+"/*.png"       
        getplotfiles = os.popen(plotfiles)
        filelist = getplotfiles.readlines()
#        print(len(filelist))
        if len(filelist)<21:
#            print(len(filelist))
#            print(fn)
            continue

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
#        filelist_pdf = [testfile, pdf_plot_report_name]
        if sn[batofs] == "2502":# and testtype =="ln":# and serial == "2502-18611":
            print(asic[1], ", ", serial, ", ", testname, ", ", date, ", ", testtime) 
#            print(datasheet)
#            print(testtype, testname)
#            print(convert_to_pdf_command)
#            os.popen(convert_to_pdf_command)

#            dune_ce_hwdb.EnterItemToHWDB("coldadc_p2prb2", serial, "FNAL", "US", "", "59", "NBMY62.00", "2025-01-10 00:00:00")
            #dune_ce_hwdb.EnterItemToHWDB("coldadc_p2prb2", serial, "LSU", "US", "", "59", "NBMY62.00", "2025-02-27 00:00:00")
            #dune_ce_hwdb.EnterItemToHWDB("coldadc_p2prb2", serial, "BNL", "US", "", "59", "NBMY62.00", "2025-06-04 00:00:00")
#            dune_ce_hwdb.EnterTestToHWDB("coldadc_p2prb2", serial, testname, "No comment", datasheet)
#            dune_ce_hwdb.EnterFileToTest("coldadc_p2prb2", serial, testname, datasheet, filelist)

if __name__ == '__main__':

    SubmitColdADCCTSQCTest()

