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


def SubmitPTCQCTest():
    tests = [
    "Test Date",
    "Test Time",
    "Test Location",
    "Operator Name",
    ]

#    datasheet = [["" for _ in range(10)] for _ in range(2)]

#    for i in range(len(tests)):
#        datasheet[0][i] = tests[i]


    getnames = os.popen("ls -d  examples/ptc/PTC_QC_report_*")
    filenames = getnames.readlines()
    prev = 0
    som_serial = None
    for fn in filenames:
        datasheet = [[None for _ in range(118)] for _ in range(2)]

        for i in range(len(tests)):
            datasheet[0][i] = tests[i]

        print (fn)
        fn = fn.rstrip()
        sn = fn.split("/")
        print(fn, sn[len(sn)-1])
        reportfile_name = fn+"/qc_data.txt"
        datasheet[1][2] = "\"UPENN\""
        parameter = 0
        with open(reportfile_name) as f:
            for line in f:
                if line[0] == "#" or line[0] == "\n":
                    continue
                line_cont = line.strip()
                #print(line_cont)

                line_cont = line_cont.split(":")
                if len(line_cont)>1:
                    if line_cont[0] == 'Operator Name':
                        datasheet[1][3] = "\""+line_cont[1].strip()+"\""
                    elif line_cont[0] == 'Test Date':
                        datasheet[1][0] = "\""+line_cont[1].strip()+"\""
                    elif line_cont[0] == 'Test Time':    
                        datasheet[1][1] = "\""+line_cont[1].strip()+":"+line_cont[2].strip()+"\""
                    elif line_cont[0] == 'PTC_SERIAL':
                        serial = line_cont[1].strip()
                    elif line_cont[0] == 'SOM_SERIAL':
                        som_serial = line_cont[1].strip()
                    else:
#                        print(parameter+4)
                        datasheet[0][parameter+4] = line_cont[0].strip()
                        datasheet[1][parameter+4] = "\""+line_cont[1].strip()+"\""
                        #print(parameter+4, line_cont[0].strip(), "\""+line_cont[1].strip()+"\"")
                        parameter = parameter + 1

#        print(datasheet)

        pdf_plot_report_name = "ls "+reportfile_name
        getreportfiles = os.popen(pdf_plot_report_name)
        report_list = getreportfiles.readlines()
        print(report_list)

        plotfiles = "ls "+fn+"/qc*.png "
        getplotfiles = os.popen(plotfiles)
        filelist = getplotfiles.readlines()
        print(filelist)

        ptc_photo_name = "ls "+fn+"/assembled*.png"
        getphotofiles = os.popen(ptc_photo_name)
        ptc_photo_file = getphotofiles.readlines()
        print(ptc_photo_file)
        testname = "\"QC Test\""
            
            #print(filelist)
        print(serial)    
        print(datasheet)
        print(testname)
        print(serial, som_serial)

        components = []
        row = []
        #component_id = dune_ce_hwdb.EnterItemToHWDB("ptc_fpga", som_serial, "UPENN", "US", "", "65")
        row.append("SoM Board")
        row.append(som_serial)
        row.append(component_id)
        components.append(row)

        print(components)
#        exit()
        #dune_ce_hwdb.EnterItemToHWDB("ptc", serial, "UPENN", "US", "", "66", None, None, components)
        #dune_ce_hwdb.EnterFileToItem("ptc", serial, ptc_photo_file)
        #dune_ce_hwdb.EnterTestToHWDB("ptc", serial, testname, "No comment", datasheet)
        #dune_ce_hwdb.EnterFileToTest("ptc", serial, testname, datasheet, filelist)

if __name__ == '__main__':

    SubmitPTCQCTest()

