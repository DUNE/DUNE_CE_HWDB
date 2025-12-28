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


if __name__ == '__main__':
    entry = True
    testname = "\"Reception Checkout\""

    tests = [
    "Test Date",
    "Test Time",
    "Test Location",
    "Operator Name",
    "Certificate of Quality Compliance supplied",
    "Overall PCB appearance and cleanliness",  
    "Surface quality: existence of pit, scratch or pin holes on printing traces or pad.",
    "Inspect PCB edges for possible defects",
    "Inspect both sides of PCB",
    "Check for any other noticeable defects, damages, irregularities, etc.",
    ]

    datasheet = [[None for _ in range(10)] for _ in range(2)]
    for i in range(len(tests)):
        datasheet[0][i] = tests[i]

    while(entry):
        os.system('clear')
        val = input("Enter PTC reception checkout? Press \"Y\" to continue:\n")
        if val != "Y":
            scan = False
            break
        val = input("Enter Tester Name:\n")
        datasheet[1][3] = val.strip() 
        status  = True
        while(status):
            status = False
            val = input("Enter Test Location:\n")
            if val in dune_ce_hwdb.loc_name_list:        
                datasheet[1][2] = val.strip()
            else:
                print("Location not in the list of test sites shown below.\n")
                print(dune_ce_hwdb.loc_name_list)
                status = True

        arrival_time = "{}".format(datetime.datetime.now().replace(microsecond=0))
        status = True
        date_time = None
        while(status):
            status = False
            val = input("The current time is "+arrival_time+". Press \"Y\" to use it as a Reception Checkout time or enter time in the format YYYY-MM-DD HH:MM:SS :\n")
            
            if val == "Y":
                date_time = arrival_time
            elif dune_ce_hwdb.checkTimeFormat(val):
                date_time = val.strip()
            else:    
                print("Please enter time with valid format\n")
                status = True

        date_time = date_time.split(" ")
        datasheet[1][0] = date_time[0]
        datasheet[1][1] = date_time[1]

        val = input("Enter PTC board serial number:\n")
        serial = val

        for i in range(4, 10):
            status = True
            while(status):
                status = False
                val = input("Check for "+datasheet[0][i]+" and select \"T\" for TRUE and \"F\" for FALSE:\n")
                if val == "T":
                    datasheet[1][i] = "TRUE"
                elif val == "F":
                    datasheet[1][i] = "FALSE" 
                else:
                    print("Wrong entry.\n")
                    status = True

        os.system('clear')
        print("Please check if all etries below are correct:\n")
        for i in range(0, 10):
            print(datasheet[0][i]+": ", datasheet[1][i])
            datasheet[1][i] = "\""+datasheet[1][i]+"\""
        conf = input("\n If the data is correct press \"Y\" to enter the Reception Checkout in the HWDB:\n")

        if conf == "Y":
            dune_ce_hwdb.EnterItemToHWDB("ptc", serial, "UPENN", "US", "", "66")
            dune_ce_hwdb.EnterTestToHWDB("ptc", serial, testname, "", datasheet)

