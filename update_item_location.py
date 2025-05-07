import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print("Command: python3 get_item_location.py [part_name] [SN] [Instituion Name] [Arrival Date]")
        print("Note: The arrival date is an optional parameter and if not provided, the arrival date will be set to be the curent date and time.")
        exit(1)
    else: 
        partName = sys.argv[1]
        partSN = sys.argv[2]
        institution = sys.argv[3]
        arrivalTime = None
        if len(sys.argv) == 5:
            arrivalTime = sys.argv[4]

    itemID = dune_ce_hwdb.isPartInHWDB(partName, partSN)

    dune_ce_hwdb.UpdateLocation(itemID, institution, "", arrivalTime)




