import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Command: python3 get_item_location.py [part_name] [SN]")
        exit(1)
    else: 
        partName = sys.argv[1]
        partSN = sys.argv[2]

    itemID = dune_ce_hwdb.isPartInHWDB(partName, partSN)

    itemLoc,locname = dune_ce_hwdb.GetCurrentLocation(itemID)

    if itemLoc != None:
        print(locname)



