import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Command: python3 get_summary.py [partid] [location]")
        print("If [location] is not provided the total number of components are reported.")
        exit(1)
    else: 
        partName = sys.argv[1]
        location = None
        if len(sys.argv) == 3:
            location = sys.argv[2]

    number_items = dune_ce_hwdb.getSummary(partName, location)
    if number_items != None:
        print(number_items)



