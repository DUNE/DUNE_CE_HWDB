import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Command: python3 get_details.py [partID]")
        exit(1)
    else: 
        itemID = sys.argv[1]

    serial = dune_ce_hwdb.GetItemSN(itemID)
    print(serial)



