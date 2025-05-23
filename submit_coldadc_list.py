import os
import dune_ce_hwdb 

def SubmitASICs(csvfile=None):
    if csvfile == None:
        print("Please provide CSV file with ASIC information")
        return 
    ichip =  0
    with open(csvfile) as f:
        for line in f:
            chipinfo = line.strip()
            chipdata = chipinfo.split(',')
            asic_sn = chipdata[5] + "-" + chipdata[4] 
            asic_part = chipdata[2].lower()
            asic_institution  = chipdata[6]
            asic_lotn = chipdata[3]
            if asic_part == "coldadc":
#                ichip = ichip + 1
#                print(ichip, asic_sn, asic_part, asic_institution, asic_lotn)
                
                if chipdata[5] == "2422":
                    asic_part = asic_part + "_p2prep"
                    ichip = ichip + 1
                    print(ichip, asic_sn, asic_part, asic_institution, asic_lotn)
#                    dune_ce_hwdb.EnterItemToHWDB(asic_part, asic_sn, asic_institution, "US", "", "15", asic_lotn, "2024-08-10 00:00:00")

if __name__ == '__main__':


    list_folder = "../temp/DUNE_CE_HWDB/ASIC_lists/LSU"
    filelist = os.popen("ls " + list_folder + "/*.csv")
    filenames = filelist.readlines()
    for fn in filenames:
        file = fn.strip()
        print(file)
        SubmitASICs(file)    


