import datetime
import socket
import os
import os.path
import pwd
import sys
import glob
import subprocess
import array
import dune_ce_hwdb


if __name__ == '__main__':
    scan = True
    while(scan):
        os.system('clear')
        val = input("Scan item or enter \"N\" to end:\n")
        if val == "N":
            scan = False
            break
        scanned = val.strip()
        item = scanned.split("/")
        item_id = item[len(item)-1]
        part_name =  dune_ce_hwdb.GetItemName(item_id)
        part_sn   =  dune_ce_hwdb.GetItemSN(item_id)
        part_loc  =  dune_ce_hwdb.GetItemLocation(item_id)
        print("Current location for part \'"+part_name+"\' with SN \'"+part_sn+"\' is "+part_loc)
#        print("Confirm with \"Y\" location change for item: "+part_name+" with SN "+part_sn)
        
        conf = input("Please confirm with \"Y\" the change of location.\n")
        if conf == "Y":
            dune_ce_hwdb.UpdateLocation(item_id)

