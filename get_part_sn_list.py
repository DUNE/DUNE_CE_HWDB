import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Command: python3 get_summary.py [partid]")
        exit(1)
    else: 
        partName = sys.argv[1]

    part_list = dune_ce_hwdb.GetPartList(partName)
    
    if len(part_list) == 0:
        print("No parts recorded in the HWDB.")
        exit(1)

    with open("parts_list_"+partName+"_sn.csv", "w") as fcsv:
        for part in part_list:
            item_id = part.strip()
            item_id = item_id.strip("\"")
            part_sn   =  dune_ce_hwdb.GetItemSN(item_id)
            print(part_sn+", "+item_id)

            fcsv.write(part_sn+", "+item_id)

          #  if test_values != None:
          #      for i in range(len(test_values)):
          #          fcsv.write(", "+test_values[i])

            fcsv.write("\n")
            #exit()
            

