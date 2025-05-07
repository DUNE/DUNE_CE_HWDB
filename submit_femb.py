import datetime
import socket
import os
import os.path
import pwd
import sys
import glob
import json
import subprocess
import array
import dune_ce_hwdb

def SubmitFEMB(femb_parts, femb_sn, institution, country_code = "US", comments = "No comment", manufact_id = "58"):

    components = []
    for i in range(len(femb_parts)):
        row = []
        part_type = None
        if "coldata" in femb_parts[i][0].lower():
            part_type = "coldata"
        elif "coldadc" in femb_parts[i][0].lower():
            part_type = "coldadc"
        elif "larasic" in femb_parts[i][0].lower():
            part_type = "larasic"

        component_id = EnterItemToHWDB(part_type, femb_parts[i][1], institution, country_code, comments, manufact_id)
        row.append(femb_parts[i][0])
        row.append(femb_parts[i][1])
        row.append(component_id)
        components.append(row)
    dune_ce_hwdb.EnterItemToHWDB("femb", femb_sn, institution, country_code, comments, manufact_id, components)

if __name__ == '__main__':

    femb_parts = [ 
        ["(F) COLDATA 1 SN", "2314-00199"], 
        ["(F) COLDATA 2 SN", "2314-00203"], 
        ["(F) ColdADC 1 SN", "2315-02380"], 
        ["(F) ColdADC 2 SN", "2315-02520"], 
        ["(F) ColdADC 3 SN", "2315-02523"], 
        ["(F) ColdADC 4 SN", "2315-02374"], 
        ["(F) LArASIC 1 SN", "003-04595"], 
        ["(F) LArASIC 2 SN", "003-04594"], 
        ["(F) LArASIC 3 SN", "003-03785"], 
        ["(F) LArASIC 4 SN", "003-04596"], 
        ["(B) ColdADC 1 SN", "2315-02025"], 
        ["(B) ColdADC 2 SN", "2315-02341"], 
        ["(B) ColdADC 3 SN", "2315-02417"], 
        ["(B) ColdADC 4 SN", "2315-01562"], 
        ["(B) LArASIC 1 SN", "003-07400"], 
        ["(B) LArASIC 2 SN", "003-07399"], 
        ["(B) LArASIC 3 SN", "003-07394"], 
        ["(B) LArASIC 4 SN", "003-07393"] ]



    SubmitFEMB(femb_parts, femb_sn, "BNL")
  
