import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Command: python3 get_summary.py [partName] [partSN]")
        exit(1)
    else: 
        partName = sys.argv[1]
        partSN = sys.argv[2]


    itemID = dune_ce_hwdb.isPartInHWDB(partName, partSN)
    status_name, status_id, cert_qaqc, is_installed, qc_uploaded = dune_ce_hwdb.GetItemStatus(itemID)

    print("The status for item "+itemID+" is:")
    print("Status: "+status_name)
    if cert_qaqc:
        print("Item IS QAQC certified.")
    else:
        print("Item is NOT QAQC certified.")
    if is_installed:
        print("Item IS Installed.")
    else:
        print("Item is NOT Installed.")
    if qc_uploaded:
        print("QC results are Uploaded.")
    else:
        print("QC results are NOT Uploaded.")




