import os
import sys
import dune_ce_hwdb 

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Command: python3 update_item_status.py [partName] [partSN]")
        exit(1)
    else: 
        partName = sys.argv[1]
        partSN   = sys.argv[2]

    itemID = dune_ce_hwdb.isPartInHWDB(partName, partSN)
    print(itemID)
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

    change = input("Would you like to change the status? (Y/N):")
    if change == "N":
        exit(0)
    print("The accepted status names and IDs are:")
    for i in dune_ce_hwdb.status_ids:
        print(str(i)+": "+dune_ce_hwdb.status_names[dune_ce_hwdb.status_ids.index(i)])

    new_status = input("Please enter the status ID:")
    if int(new_status) in dune_ce_hwdb.status_ids:
        new_status = int(new_status)
    else:
        new_status = None

    q_cert   = input("The item is QAQC Certified?(Y/N)")
    if q_cert == "Y":
        new_cert = True
    elif q_cert == "N":
        new_cert = False
    else:
        new_cert = None

    q_inst   = input("The item is installed?(Y/N)")
    if q_inst == "Y":
        new_inst = True
    elif q_inst == "N":
        new_inst = False
    else:
        new_inst = None 

    q_upload   = input("Is the QC data uploaded?(Y/N)")
    if q_upload == "Y":
        new_upload = True
    elif q_upload == "N":
        new_upload = False
    else:
        new_upload = None    

    dune_ce_hwdb.PatchItem(itemID, new_status, new_cert, new_inst, new_upload)

