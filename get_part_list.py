import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    partSN = None
    part_list = []

    if len(sys.argv) < 2 and len(sys.argv) > 3:
        print("Command: python3 get_summary.py [partName] [partSN]")
        print("If you ommit the serial number a list of all parts with [part Name will be listed.]")
        exit(1)
    else:
        partName = sys.argv[1]
        if len(sys.argv) == 3:
            partSN = sys.argv[2]
            part_list.append(dune_ce_hwdb.isPartInHWDB(partName, partSN))
        else:
            part_list = dune_ce_hwdb.GetPartList(partName)
            if len(part_list) == 0:
                print("No parts recorded in the HWDB.")
                exit(1)


    with open("parts_list_"+partName+".csv", "w") as fcsv:
        for part in part_list:

            item_id = part.strip()
            item_id = item_id.strip("\"")
            values = dune_ce_hwdb.GetItemDetails(item_id)
            #comp_name, serial, resp_inst, resp_inst_id, location, manuf, item_stat, qaqc_cert, installed, qc_upload = dune_ce_hwdb.GetItemDetails(item_id) 
            latest_loc,latest_loc_name = dune_ce_hwdb.GetCurrentLocation(item_id)
            testsIDsList, testsTypesList, testsFieldsList, testsValuesList, testsImagesList = dune_ce_hwdb.GetItemTests(item_id)
        
            #fcsv.write(item_id+", "+comp_name+", "+serial+", "+str(resp_inst_id)+", "+str(manuf)+", "+latest_loc_name+", "+str(latest_loc)+", "+str(item_stat)+", "+str(qaqc_cert))
            fcsv.write(item_id)
            for i in range(len(values)):
                fcsv.write(", ")
                if isinstance(values[i], int):    
                    fcsv.write(str(values[i]))
                elif values[i] == None:
                    fcsv.write(" ")
                else:
                    fcsv.write(values[i])



            if testsIDsList != None:
                for i in range(len(testsIDsList)):
                    fcsv.write(", "+testsTypesList[i])
                    for j in range(len(testsValuesList[i])):
                        fcsv.write(", "+ str(testsValuesList[i][j]))

            fcsv.write("\n")
            #exit()
            

