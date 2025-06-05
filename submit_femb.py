import datetime
import socket
import os
import os.path
import pwd
import sys
import glob
import json
import subprocess
import array
import csv
import dune_ce_hwdb

def SubmitFEMB(femb_parts, femb_sn, institution, country_code = "US", comments = "No comment", manufact_id = "", filelist = None):

    part_name_mapping = {"coldata":"coldata_e4prep", "coldadc":"coldadc_p2prep", "larasic":"larasic_p5prep1"}

    components = []
    for i in range(len(femb_parts)):
        row = []
        part_type = None
        if "coldata" in femb_parts[i][0].lower():
            part_type = "coldata"
        elif "coldadc" in femb_parts[i][0].lower():
            part_type = "coldadc"
        elif "larasic" in femb_parts[i][0].lower():
            part_type = "larasic"

        if part_type is None:
            raise ValueError(f"Unknown part type for {femb_parts[i][0]}")
        part_type = part_name_mapping[part_type]
#    components = []
#    for i in range(len(femb_parts)):
#        row = []
#        part_type = None
#        if "coldata" in femb_parts[i][0].lower():
#            part_type = "coldata"
#        elif "coldadc" in femb_parts[i][0].lower():
#            part_type = "coldadc"
#        elif "larasic" in femb_parts[i][0].lower():
#            part_type = "larasic"

        

        component_id = dune_ce_hwdb.EnterItemToHWDB(part_type, femb_parts[i][1], institution, country_code, comments, "59")
        row.append(femb_parts[i][0])
        row.append(femb_parts[i][1])
        row.append(component_id)
        components.append(row)
    dune_ce_hwdb.EnterItemToHWDB("femb_prep", femb_sn, institution, country_code, comments, manufact_id, None, None, components)
    dune_ce_hwdb.EnterFileToItem("femb_prep", femb_sn, filelist)

if __name__ == '__main__':

    femb_num = "00053"
    femb_path = "examples/femb/"
    femb_parts_file = femb_path+"femb_parts_"+femb_num+".txt"
    femb_parts = [[0 for x in range(2)] for y in range(18)]
    femb_sn = None
    i=0
    with open(femb_parts_file, mode='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
#            print(lines[0], lines[1])
            if 'femb' in lines[0].lower():
                femb_sn = lines[1].strip()
                femb_sn = femb_sn.strip('\"')
                print("FEMB SN:", femb_sn)
            else:
                femb_parts[i][0] = lines[0].strip()
                femb_parts[i][1] = lines[1].strip()
                femb_parts[i][1] = femb_parts[i][1].strip('\"')
                print(femb_parts[i][0],  femb_parts[i][1])
                i = i+1


    plotfiles = "ls examples/femb/"+"femb_"+femb_num+"*.png"
    getplotfiles = os.popen(plotfiles)
    filelist = getplotfiles.readlines()
    print(len(filelist))
    print(filelist)

    SubmitFEMB(femb_parts, femb_sn, "UCINCI", "US", "", "58", filelist)
  
