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
    ]

#    datasheet = [["" for _ in range(10)] for _ in range(2)]

#    for i in range(len(tests)):
#        datasheet[0][i] = tests[i]


    getnames = os.popen("ls -d  examples/wib/*")
    filenames = getnames.readlines()
    prev = 0
    for fn in filenames:
        datasheet = [[None for _ in range(4)] for _ in range(2)]

        for i in range(len(tests)):
            datasheet[0][i] = tests[i]

#        print (fn)
        fn = fn.rstrip()
        sn = fn.split("/")
        print(fn, sn[len(sn)-1])
        reportfile_name = fn+"/final_report.md"
        datasheet[1][2] = "\"BNL\""
        with open(reportfile_name) as f:
            for line in f:
                line_cont = line.strip()
                line_cont = line_cont.split(":")
                if line_cont[0] == '#### Tester Name':
                    value = line_cont[1].split(";")
                    datasheet[1][3] = "\""+value[len(value)-1]+"\""
                elif line_cont[0] == '#### Date':
                    value = line_cont[1].split(";")
                    testdate = value[len(value)-1].split(" ")
                    datasheet[1][0] = "\""+testdate[0]+"\""
                    datasheet[1][1] = "\""+testdate[1]+":"+line_cont[2]+"\""
                    
        print(datasheet)
        serial = sn[len(sn)-1]
        pdf_plot_report_name = "ls "+fn+"/*/*.pdf"
        getreportfiles = os.popen(pdf_plot_report_name)
        report_list = getreportfiles.readlines()
        print(report_list)

        plotfiles = "ls "+fn+"/*.png "+fn+"/*/*.png"
        getplotfiles = os.popen(plotfiles)
        filelist = getplotfiles.readlines()
        print(filelist)

        testname = "\"QC Test\""
            
            #print(filelist)
        print(serial)    
        print(datasheet)
        print(testname)

#        dune_ce_hwdb.EnterItemToHWDB("wib", serial, "BNL", "US", "", "58")
#        dune_ce_hwdb.EnterTestToHWDB("wib", serial, testname, "No comment", datasheet)
        dune_ce_hwdb.EnterFileToTest("wib", serial, testname, datasheet, filelist)

if __name__ == '__main__':

    SubmitColdADCCTSQCTest()

