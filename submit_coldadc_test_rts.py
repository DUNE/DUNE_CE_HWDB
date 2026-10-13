import socket
import os
import os.path
import pwd
import sys
import glob
import subprocess
import array
import dune_ce_hwdb
from datetime import datetime, date, time, timezone

def SubmitColdADCRTSQCTest(start):
    tests = [
        "Test Date",
        "Test Time",
        "Test Location",
        "Operator Name",
        "ENOB FREQ",
        "ENOB",
        "DACDIFF",
        "DACSE",
        "VDDA2P5",
        "VDDD1P2",
        "VDDD2P5",
        "VDDIO",
        "Overall QC Result"
    ]

    getnames = os.popen("ls -d /mnt/f/coldadc_qc_results/DUNE_CE/TestData/Time*")
    test_folders = getnames.readlines()
    folders_list = []
    for test_sub in test_folders:
        test_folder = test_sub.strip()
        getfolder = os.popen(f"ls -d {test_folder}/*")
        res = getfolder.readline()
        res_folder = res.strip()
        getbinfiles = os.popen(f"ls -d {res_folder}/*.bin | wc -l")
        numbinfiles = getbinfiles.readlines()
        binfiles = numbinfiles[0].strip()
        if binfiles == "10":
            folders_list.append(res_folder)

    num_chips = 0
    folder_num = 0
    print(start, len(folders_list))
    for fold_ind in range(start, len(folders_list)):
        folder = folders_list[fold_ind]
        print(fold_ind, folder)
        folder_num = folder_num + 1
        getchips = os.popen(f"ls -d {folder}/*/")
        chipfolders = getchips.readlines()

        file_list = []
        for chipfolder in chipfolders:
            chip_qc_done = False

            chip_folder = chipfolder.strip()
            getchiplogs = os.popen(f"ls -d {chip_folder}/*.csv")
            chiplogs = getchiplogs.readlines()
            if len(chiplogs) < 3:
                continue
            chip = (chipfolder.strip()).split("/")
            serial = chip[len(chip)-2]
            testenv = chip[len(chip)-3].split("_")
            testtype = testenv[0]
            
#            if "2422-" not in serial:
#                continue

            print(num_chips, serial, testtype)
            num_chips = num_chips + 1         
            test_data = {}
            datasheet = [[None for _ in range(13)] for _ in range(2)]
            chipcommand = f"ls {chipfolder.strip()}/*.png {folder}/*.log"
            getpngfiles = os.popen(chipcommand)
            filelist = getpngfiles.readlines()
            logfile_list = []
            logfile_list.append(f"{chipfolder.strip()}/ColdADC_hwdb_log.txt")
            logfile_list.append(f"{chipfolder.strip()}/enob.csv")
            logfile_list.append(f"{chipfolder.strip()}/noise.csv")
            logfile_list.append(f"{chipfolder.strip()}/power.csv")
            for logfile in logfile_list:
                with open(logfile) as f:
                    for line in f:
                        logline = line.strip()
                        logentry = logline.split(":")
                        if "PASS" in logentry[1]:
                            chip_qc_done = True


                        if logentry[0] in tests:
                            index = tests.index(logentry[0])
                            datasheet[0][index] = logentry[0]
                            if logentry[0] == "Test Time":
                                test_data[logentry[0]] = logentry[1].strip()+":"+logentry[2].strip()
                                datasheet[1][index] = logentry[1].strip()+":"+logentry[2].strip()
                            elif logentry[0] == "Test Date":
                                test_data[logentry[0]] = (logentry[1].strip()).replace("/", "-")
                                datasheet[1][index] = (logentry[1].strip()).replace("/", "-")
                            else:    
                                test_data[logentry[0]] = logentry[1].strip()
                                datasheet[1][index] = logentry[1].strip()

    
            if testtype.lower() == "rt":
                testname = "RoomT QC Test"
            elif testtype.lower() == "ln":
                testname = "CryoT QC Test"            

            mannuf = None
            if dune_ce_hwdb.hwdbsel == "PROD":
                manuf = "15"
            if dune_ce_hwdb.hwdbsel == "DEV":
                manuf = "59"
            
            if "2502-" in serial:
                waferID = "NBMY62.00"
            elif "2422-" in serial:
                waferID = "NBNA38.00"
            else:
                exit()

#            dune_ce_hwdb.EnterItemToHWDB("coldadc_p2prb1", serial, "FNAL", "US", "", manuf, waferID, "2025-01-10 00:00:00")
            dune_ce_hwdb.EnterItemToHWDB("coldadc_p2prb1", serial, "LSU", "US", "", manuf, waferID, "2025-11-01 00:00:00")
            dune_ce_hwdb.EnterTestToHWDB("coldadc_p2prb1", serial, testname, "No comment", datasheet)
            dune_ce_hwdb.EnterFileToTest("coldadc_p2prb1", serial, testname, datasheet, filelist)
            itemID = dune_ce_hwdb.isPartInHWDB("coldadc_p2prb1", serial)
            dune_ce_hwdb.PatchItem(itemID, 120, chip_qc_done, None, True, None, None, None)


if __name__ == '__main__':

    start_folder = int(sys.argv[1])
    SubmitColdADCRTSQCTest(start_folder)
