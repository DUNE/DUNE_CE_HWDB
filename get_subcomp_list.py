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

    with open("subcomponent_list_"+partName+".csv", "w") as fcsv:
        for part in part_list:

            item_id = part.strip()
            item_id = item_id.strip("\"")
            part_name =  dune_ce_hwdb.GetItemName(item_id)
            part_sn   =  dune_ce_hwdb.GetItemSN(item_id)
            part_loc  =  dune_ce_hwdb.GetItemLocation(item_id)
            subcomp_pos, subcomp_ids =  dune_ce_hwdb.GetSubcomponents(item_id)
            #print(item_id, part_name, part_sn, part_loc)
            print(item_id, part_sn)
            fcsv.write(item_id+", "+part_sn)
            if subcomp_ids != None:
                for i in range(len(subcomp_ids)):
#                    print(subcomp_pos[i], subcomp_ids[i])
                    fcsv.write(", "+subcomp_ids[i])
            fcsv.write("\n")
