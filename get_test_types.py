import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Command: python get_test_types.py [part_name]")
        exit(1)
    else: 
        partName = sys.argv[1]

    qc_tid, qc_type = dune_ce_hwdb.GetTestTypeID(partName, "Blah")




