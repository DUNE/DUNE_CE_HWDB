import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Command: python3 get_qrcode.py [partName] [partSN]")
        exit(1)
    else: 
        partName = sys.argv[1]
        partSN   = sys.argv[2]

    itemID = dune_ce_hwdb.isPartInHWDB(partName, partSN)
    dune_ce_hwdb.GetQRCode(itemID)




