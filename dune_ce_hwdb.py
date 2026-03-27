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
import requests
import mimetypes
from pathlib import Path
from reportlab.pdfgen import canvas

tokenloc=os.environ.get('TOKENLOC')
hwdbsel=os.environ.get('HWDBSELECT')
commverb=os.environ.get('COMMANDVERB')
siteloc=os.environ.get('SITELOC')

token = None
with open(tokenloc, 'r') as ft:
    token = ft.read().strip()
headers = {'Authorization': f'Bearer {token}'}


if hwdbsel == "PROD":
    conf = input("You will be submitting to the PRODUCTION HWDB. Please confirm byt typing YES: ")
    if conf != "YES":
        exit(0)
elif hwdbsel != "DEV":
    print("Please set the HWDB version environment variable in setup_hwdb.sh.")

upload_url = "https://dbwebapi2.fnal.gov:8443/cdbdev/api"
if hwdbsel == 'PROD':
    upload_url = "https://dbwebapi2.fnal.gov:8443/cdb/api"

download_url   = upload_url+"/v1"

locations           =   {
                        "INTRANSIT" : 0, 
                        "FNAL"      : 1, 
                        "CERN"      : 2, 
                        "BNL"       : 128, 
                        "MSU"       : 146, 
                        "LSU"       : 144, 
                        "LBL"       : 142, 
                        "UCI"       : 171, 
                        "UPENN"     : 191, 
                        "UCINCI"    : 176
                        }
inv_locations = {value: key for key, value in locations.items()}

parts               =   {
                        "larasic_p5prep1"       : "D08100100001", 
                        "larasic_p5bprep2"      : "D08100100002", 
                        "larasic_p5bpr1"        : "D08100100003", 
                        "coldadc_p2prep"        : "D08100200001", 
                        "coldadc_p2prb1"        : "D08100200002", 
                        "coldadc_p2prb2"        : "D08100200003", 
                        "coldata_e4prep"        : "D08100300001", 
                        "coldata_e4prb1"        : "D08100300002", 
                        "coldata_e4prb2"        : "D08100300003", 
                        "femb_prep"             : "D08100400001",
                        "femb_prod_hd"          : "D08101100031",
                        "femb_prod_vd"          : "D08101100041",
                        "fpga_ptc"              : "D08100800011",
                        "cable_sig_long_vd"     : "D08102100012",
                        "cable_sig_msas_vd"     : "D08102100021",
                        "wiec"                  : "D08104100001", 
                        "wib"                   : "D08104200001",
                        "ptc"                   : "D08104300001",
                        "compbox_larasic"       : "D08120100001",
                        "compbox_coldadc"       : "D08120100002",
                        "compbox_coldata"       : "D08120100003",
                        "ce_shipbox"            : "D08120200001" 
                        }
inv_parts = {value: key for key, value in parts.items()}


part_status =           {
                        "Unknown"                       : 0, 
                        "In Fabrication"                : 100, 
                        "Waiting on QA/QC Tests"        : 110, 
                        "QA/QC Tests - Passed All"      : 120, 
                        "QA/QC Tests - Non-conforming"  : 130, 
                        "QA/QC Tests - Use As Is"       : 140, 
                        "In Rewor"                      : 150, 
                        "In Repair"                     : 160, 
                        "Permanently Unavailable"       : 170, 
                        "Broken or Needs Repair"        : 180    
                        }
inv_part_status = {value: key for key, value in part_status.items()}

loc_name_list       = list(locations.keys())
loc_id_list         = list(locations.values())

part_name_list      = list(parts.keys()) 
part_id_list        = list(parts.values())

status_names        = list(part_status.keys())
status_ids          = list(part_status.values())

#class DUNECE_HWDB:


#    def __init__(self, master=None,forceQuick=False,forceLong=False):
#        Frame.__init__(self,master)
#        self.pack()
#
#        if forceQuick and forceLong:
#            raise Exception("Can't forceQuick and forceLong at the same time")
#        self.forceQuick = forceQuick
#        self.forceLong = forceLong
#
#        self.timestamp = None
#        self.result_labels = []
#        self.display_procs = []
#        #Define general commands column
#        self.define_test_details_column()
#        self.reset()
#
#        self.master.protocol("WM_DELETE_WINDOW", self.exit)
#
#        self.data_base_dir = "/home/dune/ColdADC/test_results"
#        check_folder = os.path.isdir(self.data_base_dir)
#        if not check_folder: os.makedirs(self.data_base_dir)
#
#        self.soft_dir = os.environ["PWD"]

def checkTimeFormat(date_time):
    date_time_format = "%Y-%m-%d %H:%M:%S"
    try:
        datetime.datetime.strptime(date_time, date_time_format)
        return True
    except ValueError:
        return False

def ConvertToJSON(data):
    json_data = ""
    for line in data:
        line_val = line.strip()
        json_data = json_data + line_val

    return json.loads(json_data)

def printJSON(data):

    print(json.dumps(data, indent = 4))

def GetComponentID(item_name):
    global part_name_list, part_id_list

    if item_name in part_name_list:
        item_part_id = part_id_list[part_name_list.index(item_name)]
    else:
        print("Part name is not recognized. Accepted part names are:")
        print(part_name_list)
        exit(1)

    if hwdbsel == "PROD":
        if item_name[0:8] == "larasic_":
            item_part_id = part_id_list[part_name_list.index("larasic_p5bpr1")]
        elif item_name[0:8] == "coldadc_":
            item_part_id = part_id_list[part_name_list.index("coldadc_p2prb1")]
        elif item_name[0:8] == "coldata_":
            item_part_id = part_id_list[part_name_list.index("coldata_e4prb2")]
        elif item_name[0:7] == "fembvd_":
            item_part_id = part_id_list[part_name_list.index("fembvd_prod")]
        elif item_name[0:7] == "fembhd_":
            item_part_id = part_id_list[part_name_list.index("fembhd_prod")]    
        else:
            exit(1)
    print(item_part_id)
    return item_part_id

def GetSummary(item_name, location = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list

    item_part_id = GetComponentID(item_name)

    if location != None:
        if location in loc_name_list:
            institution_id = loc_id_list[loc_name_list.index(location)] 
        else:
            print("Location is not recognized. Accepted locations are:")
            print(loc_name_list)
            exit(1)

        url = download_url + "/component-types/" + item_part_id + "/components?location=" + str(institution_id)
        print(url)
    else:
        url = download_url + "/component-types/" + item_part_id + "/components?"

    datain = requests.get(url, headers=headers)
    summary  = datain.json()["pagination"]
    printJSON(summary)
    
    if summary["total"] == 0:
        return None
    else:
        return summary["total"]

def GetItemDetails(item_id):
    global curl_command, upload_url, download_url, upload_command

    if item_id == None:
        print("No part ID has been provided.")
        exit(1)
        return

    url = download_url + "/components/" + item_id
    datain = requests.get(url, headers=headers)

    details = datain.json()["data"]

    if len(detail) == 0:
        return [None, None, None, None, None, None, None, None, None]

    #printJSON(details)

    comp_name       = details['component_type']['name']
    serial          = details['serial_number']
    resp_inst       = details['institution']['name']
    resp_inst_id    = details['institution']['id']
    location        = details['location']
    if details['manufacturer'] != None:
        manuf       = details['manufacturer']['id']
    else:
        manuf       = None
    if details['status'] != None:
        item_stat   = details['status']['id']
    else:
        item_stat   = None
    qaqc_cert       = details['certified_qaqc']
    installed       = details['is_installed']
    qc_upload       = details['qaqc_uploaded']

    return [comp_name, serial, resp_inst, resp_inst_id, location, manuf, item_stat, qaqc_cert, installed, qc_upload]

def GetItemSN(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list

    dummy, serial, dummy, dummy, dummy, dummy, dummy, dummy, dummy, dummy = GetItemDetails(item_id)
    return serial

def GetQRCode(item_id):
    global curl_command, upload_url, download_url, upload_command
 
    if item_id == None:
        print("No part ID has been provided.")
        exit(1)
        return


    file_name = "QR_"+item_id+".png"
    url = download_url + "/get-qrcode/" + item_id 
    datain = requests.get(url, headers=headers)

    if datain.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(datain.content)
        print(f"File '{file_name}' downloaded successfully!")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def GetBarCode(item_id):
    global curl_command, upload_url, download_url, upload_command

    if item_id == None:
        print("No part ID has been provided.")
        exit(1)
        return

    file_name = "BC_"+item_id+".png"
    url = download_url + "/get-barcode/" + item_id
    datain = requests.get(url, headers=headers)

    if datain.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(datain.content)
        print(f"File '{file_name}' downloaded successfully!")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def GetItemName(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list

    name, dummy, dummy, dummy, dummy, dummy, dummy, dummy, dummy, dummy = GetItemDetails(item_id)
    return name


def GetItemLocation(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list

    return GetCurrentLocation(item_id)

def GetItemStatus(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list

    if item_id == None:
        print("No part ID has been provided.")
        exit(1)
        return

    url = download_url + "/components/" + item_id + "/status"
    datain = requests.get(url, headers=headers)
    status = datain.json()['data']
    return status['status']['name'], status['status']['id'], status['certified_qaqc'], status['is_installed'], status['qaqc_uploaded']

def GetItemTests(item_id):
    global curl_command, upload_url, download_url

    url = download_url + "/components/" + item_id + "/tests"
    datain = requests.get(url, headers=headers)
    test_types = datain.json()["data"]
    test_type_ids = []
    test_type_names = []
    if len(test_types) > 0:
        for test_type in test_types:
            test_type_ids.append(test_type["test_type"]["id"])
            test_type_names.append(test_type["test_type"]["name"])
    else:
        return None, None, None, None, None

    testsIDsList    = []
    testsTypesList  = []
    testsFieldsList = []
    testsValuesList = []
    testsImagesList = [] 
    for test_tid in test_type_ids:
        url = download_url + "/components/"+item_id+"/tests/"+str(test_tid)+"?history=True"
        testsin = requests.get(url, headers=headers)
        tests = testsin.json()["data"]
        #printJSON(tests)
        for test in tests:
            testsIDsList.append(test["id"])
            testsTypesList.append(test["test_type"]["name"])
            testsFieldsList.append(list(test["test_data"].keys()))
            testsValuesList.append(list(test["test_data"].values()))
            testsImagesList.append(test["images"])

    if len(testsIDsList)>0:   
        return testsIDsList, testsTypesList, testsFieldsList, testsValuesList, testsImagesList
    else:
        return None, None, None, None, None

def GetParent(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list

    url = download_url + "/components/" + item_id + "/container"
    datain = requests.get(url, headers=headers)
    cont = datain.json()["data"]
    if len(cont) > 0:
        parent_id = (cont[0])["container"]["part_id"]
        return parent_id
    else:
        return None

def GetPartList(item_name):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list
   
    item_part_id = GetComponentID(item_name)

    numItems = GetSummary(item_name)
    numPages = int(numItems)//100 + 1
    print (numItems, numPages)

    partsList = []
    for i in range(numPages):
        page = str(i+1)
        url = download_url + "/component-types/" + item_part_id + "/components?page=" + page + "&size=100"
        datain = requests.get(url, headers=headers)
        plist = datain.json()["data"]
        for part in plist:
            partsList.append(part["part_id"])
    return partsList

def GetSubcomponents(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list

    url = download_url + "/components/" + item_id + "/subcomponents"
    subcomp = requests.get(url, headers=headers)
    subcomponents       = subcomp.json()["data"]
    subcomponent_pids   = []
    subcomponent_fpos   = []
    if len(subcomponents) != 0:
        for subc in subcomponents:
            subcomponent_pids.append(subc["part_id"])
            subcomponent_fpos.append(subc["functional_position"])
        return subcomponent_fpos, subcomponent_pids
    else:
        return None, None
    

def GetSystemName(item_id):
    global curl_command, upload_url, download_url, upload_command

    hwdb_exp_id = item_id[0:1]
    hwdb_sys_id = item_id[1:4]
    hwdb_sub_id = item_id[4:7]
    hwdb_com_id = item_id[0:12]

    url = download_url + "/systems/" + hwdb_exp_id + "/" + hwdb_sys_id
    datain = requests.get(url, headers=headers)
    sys = datain.json()["data"]
    if len(sys) > 0:
        return sys['name']
    else:
        return None

def GetSubsystemName(item_id):
    global curl_command, upload_url, download_url, upload_command

    hwdb_exp_id = item_id[0:1]
    hwdb_sys_id = item_id[1:4]
    hwdb_sub_id = item_id[4:7]
    hwdb_com_id = item_id[0:12]

    url = download_url + "/subsystems/" + hwdb_exp_id + "/" + hwdb_sys_id + "/" + hwdb_sub_id
    datain = requests.get(url, headers=headers)
    sys = datain.json()["data"]
    if len(sys) > 0:
        return sys['subsystem_name']
    else:
        return None

def GetComponentName(item_id):
    global curl_command, upload_url, download_url, upload_command

    url = download_url + "/components/" + item_id
    datain = requests.get(url, headers=headers)
    comp = datain.json()["data"]
    if len(comp) > 0:
        return comp['component_type']['name']
    else:
        return None

def isPartInHWDB(item_name, item_sn):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list
  
    item_part_id = GetComponentID(item_name)

    url = download_url + "/component-types/" + item_part_id + "/components?serial_number="+item_sn
    datain = requests.get(url, headers=headers)
    parts = datain.json()["data"]
    if len(parts) == 0:
        return None
    elif len(parts) == 1:
        return (parts[0])["part_id"]

def isPartIDInHWDB(part_id):
    global curl_command, upload_url, download_url, upload_command

    url = download_url + "/components/" + part_id
    datain = requests.get(url, headers=headers)
    parts = datain.json()

    if parts["status"] == "ERROR":
        return False
    else:
        return True
     
def GetTestTypeID(item_name, test_type = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    if test_type == None:
        print("No test type provided.")
        exit(1)
        return None

    item_part_id = GetComponentID(item_name)

    url = download_url + "/component-types/" + item_part_id + "/test-types"
    datain = requests.get(url, headers=headers)
    test_types = datain.json()["data"]

    qc_names    = []
    qc_tids     = []
    if len(test_types) == 0:
        print("This Part ID doesn't have any tests defined.")
        exit(1)
        return None, None
    else:
        for t in test_types:
            qc_names.append(t["name"])
            qc_tids.append(t["id"])

    if test_type in qc_names:
        return qc_tids[qc_names.index(test_type)], test_type
    else:
        print("The component "+item_name+" has the following tests:")
        print(qc_names)
        exit(1)
        return None, None

def isTestInHWDB(item_id, qc_tid, qc_date, qc_time):
    global curl_command, upload_url, download_url

    found_test = False
    found_test_id = 0

    test_time = None 
    test_date = None
    
    testsIDsList, testsTypesList, testsFieldsList, testsValuesList, testsImagesList = GetItemTests(item_id)

    if commverb == 'VERB1': print(qc_date, qc_time)
    if testsIDsList != None:
        for i in range(len(testsIDsList)):
            test_date   = testsValuesList[i][testsFieldsList[i].index("Test Date")]
            test_time   = testsValuesList[i][testsFieldsList[i].index("Test Time")]
            test_num    = testsIDsList[i]

            if commverb == 'VERB1': print(test_date, test_time ,test_num)
            if (test_date == qc_date) and (test_time == qc_time):
                found_test = True
                found_test_id = test_num

    if not found_test:
        return None
    else:
        return found_test_id

def EnterItemToHWDB(item_name, item_sn, institution, country_code = "US", comments = "", manufact_id = None, lot_num = None, arrival_date = None, connectors = None, specification = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    item_id = None
    if item_sn != None:
        item_id = isPartInHWDB(item_name, item_sn)
    
    if item_id == None:
        item_part_id = GetComponentID(item_name)

        item_data = ItemToUploadJSON(item_sn, item_part_id, institution, country_code, comments, manufact_id, lot_num, arrival_date, connectors, specification)
        if commverb == 'VERB1': printJSON(item_data)

        url = download_url + "/component-types/" + item_part_id + "/components"
        upload = requests.post(url, json=item_data, headers=headers)
        upload_result = upload.json()

        if upload_result["status"] == "OK":
            item_id = upload_result["part_id"]
            print("Item ",item_name," entry has been created with item ID: ", item_id)
        else:
            print("Item entry for ",item_name, " failed.")
            exit(1)

    UpdateLocation(item_id, institution, comments, arrival_date) 
    
    return item_id


def ItemToUploadJSON(item_sn, part_type_id, institution, country_code = "US", comment = None, manufact_id = None, lot_num = None, arrival_date = None, connectors = None, specification = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list
    
    institution_id = loc_id_list[loc_name_list.index(institution)]

    item_data = {}
    item_comp_id = {}
    item_comp_id["part_type_id"] = part_type_id
    item_data["component_type"] = item_comp_id
    item_data["serial_number"] = item_sn
    item_data["country_code"] = country_code
    item_data["comments"] = comment
    item_inst = {}
    item_inst["id"] = institution_id
    item_data["institution"] = item_inst

    if manufact_id != None:
        item_manu = {}
        item_manu["id"] = int(manufact_id)
        item_data["manufacturer"] = item_manu
    else:
        item_data["manufacturer"] = None

    item_data["specifications"] = {}
    item_spec = {}
    if specification != None:
        for i in range(len(specification)):
            item_spec[specification[i][0]] = specification[i][1]
    if lot_num != None:
        item_spec["LOT N"] = lot_num        
    if len(item_spec) > 0:        
        item_data["specifications"] = item_spec
    
    if connectors != None:
        item_data["subcomponents"] = {}
        item_subc = {}
        for i in range(len(connectors)):
            item_subc[connectors[i][0]] = connectors[i][2]
        item_data["subcomponents"] = item_subc    

    return item_data


def GetCurrentLocation(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    url = download_url + "/components/" + item_id + "/locations"
    datain = requests.get(url, headers=headers)
    loc_data = datain.json()["data"]

    if len(loc_data) == 0:
        return None, None
    else:
        latest_loc_id   = (loc_data[0])["location"]["id"]
        latest_loc_name = (loc_data[0])["location"]["name"]

    return latest_loc_id, latest_loc_name

def UpdateLocation(item_id, institution = siteloc, comments = "", arrival_date = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    if arrival_date != None and not(checkTimeFormat(arrival_date)):
        print("Please correct the arrival date format.")
        print("Expected format is '%Y-%m-%d %H:%M:%S'")
        exit(1)

    if institution in loc_name_list:
        institution_id = loc_id_list[loc_name_list.index(institution)]
    else:
        print("The institution is not in the list.")
        exit(1)

    latest_loc_id,latest_loc_name = GetCurrentLocation(item_id) 

    if (latest_loc_id == None) or (latest_loc_id != institution_id):
        arrival_time = arrival_date
        if arrival_date == None:
            arrival_time = "{}".format(datetime.datetime.now().replace(microsecond=0))

        loc_data = {}
        loc_data["arrived"] = arrival_time
        loc_data["comments"] = comments
        loc_data["location"] = {}
        loc_id = {}
        loc_id["id"] = institution_id
        loc_data["location"] = loc_id

        print(json.dumps(loc_data, indent = 4))

        url = download_url + "/components/" + item_id + "/locations"
        update_loc = requests.post(url, json=loc_data, headers=headers)
        if update_loc.json()["status"] == "OK":
            print("Location has been successfully updated to ", institution)
        else:
            print("Location update has failed.")
            exit(1)

    else:
        print("Already at ", latest_loc_name)
        return
      
    return


def EnterTestToHWDB(item_name, item_sn, test_type = None, comment = "No comment", test_datasheet = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    qc_tid, qc_type = GetTestTypeID(item_name, test_type)
   
    if test_datasheet == None:
        print("Test data not provided!")
        exit(1)

    if test_datasheet[0][0] != "Test Date" or test_datasheet[0][1] != "Test Time":
        print("Test data does not have the date and time as first items in the list!", test_datasheet[0][0], test_datasheet[0][1])
        exit(1)

    qc_date = test_datasheet[1][0]
    qc_time = test_datasheet[1][1]

    item_id = isPartInHWDB(item_name, item_sn)
    if item_id == None:
        print("The item ", item_name, "with SN", item_sn, " is not in the database")
        return None 

    checkTest = isTestInHWDB(item_id, qc_tid, qc_date, qc_time)
    if checkTest != None:
        print("This test is already in the database")
        print("Test ID = ", checkTest)
        return checkTest

    item_test = TestToUploadJSON(qc_type, comment, test_datasheet)
    if commverb == 'VERB1': printJSON(item_test)

    url = download_url + "/components/" + item_id + "/tests"
    print(url)

    upload_test = requests.post(url, json=item_test, headers=headers)
    print(upload_test)
    upload_result = upload_test.json()
    printJSON(upload_result)
    
    if upload_result["status"] == "OK":
        return upload_result["test_id"]
    else:
        print("Test upload failed.")
        exit(1)


def TestToUploadJSON(test_type, comment = "No comment", test_datasheet = None):

    item_test = {}
    item_test["test_type"] = test_type
    item_test["comments"] = comment
    
    item_test_data = {}
    num_data = len(test_datasheet[0])
    for i in range(num_data):
        item_test_data[test_datasheet[0][i]] = test_datasheet[1][i]
    item_test["test_data"] = item_test_data    

    return item_test


def PatchItem(item_id, item_status = None, cert_qc = None, is_installed = None, qc_uploaded = None, item_newsn = None, manufact_id = None, lot_num = None, connectors = None, specification = None):
    global curl_command, upload_url, download_url, upload_command, status_names, status_ids

    print(item_status)
    item_status_id = None
    if int(item_status) in status_ids:
        item_status_id = item_status
    elif item_status in status_names:
        item_status_id = status_ids[status_names.index(item_status)]
    else:
        print("Status unrecognized! The following status names or IDs are accepted:\n")
        print(status_names)
        print(status_ids)

    if cert_qc != None and not isinstance(cert_qc, bool):
        cert_qc_val = None
        print("Accepted values for the \"QCQA Certificate\" flag are boolean.")
        exit(1)

    if is_installed != None and not isinstance(is_installed, bool):
        is_installed_val = None
        print("Accepted values for the \"Is Installed\" flag are boolean.")
        exit(1)    

    if qc_uploaded != None and not isinstance(qc_uploaded, bool):
        qc_uploaded_val = None
        print("Accepted values for the \"Is Installed\" flag are boolean.")
        exit(1)    


    if not isPartIDInHWDB(item_id):
        print("Item doesn't exist for PATCHing!")
        return None
    else:
        patch_data, patch_subcomp = ItemToPatchJSON(item_id, item_status_id, cert_qc, is_installed, qc_uploaded, item_newsn, lot_num, connectors, specification)

        if commverb == 'VERB1': printJSON(patch_data)

        if len(patch_data) > 0:
            url = download_url + "/components/" + item_id 
            upload_patch = requests.patch(url, json=patch_data, headers=headers)
            if commverb == 'VERB1': printJSON(upload_patch.json())

        if len(patch_subcomp) > 0:
            url = download_url + "/components/" + item_id + "/subcomponents"
            upload_subcomp = requests.patch(url, json=patch_subcomp, headers=headers)
            if commverb == 'VERB1': printJSON(upload_subcomp.json())



def ItemToPatchJSON(item_id, item_status_id = None, cert_qc = None, is_installed = None, qc_uploaded = None, item_newsn = None, manufact_id = None, lot_num = None, connectors = None, specification = None):

    status_last, cert_last, installed_last, uploaded_last, newsn_last, manufact_last, lot_last, connector_last = False, False, False, False, False, False, False, False 

    item_patch = {}
    item_patch["part_id"] = item_id
    if item_status_id != None:
        status_patch = {}
        status_patch["id"] = item_status_id
        item_patch["status"] = status_patch
    if cert_qc != None:
        item_patch["certified_qaqc"] = cert_qc
    if is_installed != None:
        item_patch["is_installed"] = is_installed     
    if qc_uploaded != None:
        item_patch["qaqc_uploaded"] = qc_uploaded
    if item_newsn != None:
        item_patch["serial_number"] = item_newsn
    if manufact_id != None:
        manuf_patch = {}
        manuf_patch["id"] = manufact_id
        item_patch["manufacturer"] = manuf_patch

    if specification != None or lot_num != None:
        item_spec = {}
        if specification != None:
            for i in range(len(specification)):
                item_spec[specification[i][0]] = specification[i][1]
        if lot_num != None:
            item_spec["LOT N"] = lot_num
        if len(item_spec) > 0:
            item_spec["specifications"] = item_spec

    subcomp_patch = {}
    if connectors != None:
        subcomp_patch["component"] = {}
        part_id  = {}
        part_id["part_id"] = item_id
        subcomp_patch["component"] = part_id
        subcomp_patch["subcomponents"] = {}
        item_subc = {}
        for i in range(len(connectors)):
            item_subc[connectors[i][0]] = connectors[i][2]
        subcomp_patch["subcomponents"] = item_subc

    return item_patch, subcomp_patch

def GetComponentFilesInHWDB(item_par_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    url = download_url + "/component-types/" + item_part_id +"/images"
    datain = requests.get(url, headers=headers)
    images = datain.json()["data"]

    image_list = []
    for image in images:
        image_list.append(image["image_name"])

    return images_list

def EnterFileToType(item_name, filelist = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    item_part_id = GetComponentID(item_name)

    file_ids = []
    if filelist == None:
        print("File list is empty. Please provide at least one file to upload.")
        return None
    else:
        images_list = GetComponentFilesInHWDB(item_part_id)
        for file in filelist:
            filetoupload = file.strip()
            filename = Path(filetoupload).name
            if (len(images_list) == 0) or ((len(images_list) != 0) and not(filename in images_list)):
                url = download_url + "/component-types/" + item_id +"/images"
#                print(file, type(filename))
                mime_type, encoding = mimetypes.guess_type(filetoupload)
#                print(mime_type)

                with open(filetoupload, 'rb') as fp:
#                    if data !=None:
#                        files = {
#                            **{key: (None, value) for key, value in data.items()},
#                            'image':(filename, fp, mime_type)}
#                    else:
                    files = {'image':(filename, fp, mime_type)}
                    upload = requests.post(url, files=files, headers=headers)
                    file_ids.append((upload.json())["image_id"])

    return file_ids

def GetItemFilesInHWDB(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    if not isPartIDInHWDB(item_id):
        print("The item ", item_id, " is not in the database")
        return None

    url = download_url + "/components/" + item_id +"/images"
    datain = requests.get(url, headers=headers)
    images = datain.json()["data"]

    image_list = []
    for image in images:
        image_list.append(image["image_name"])

    return images_list

def EnterFileToItem(item_id, filelist = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

#    item_id = isPartInHWDB(item_name, item_sn)
    if not isPartIDInHWDB(item_id):
        print("The item ", item_id, " is not in the database")
        return None

    file_ids = []
    if filelist == None:
        print("File list is empty. Please provide at least one file to upload.")
        return None
    else:
        images_list = GetItemFilesInHWDB(item_id)
        for file in filelist:
            filetoupload = file.strip()
            filename = Path(filetoupload).name
            if (len(images_list) == 0) or ((len(images_list) != 0) and not(filename in images_list)):
                url = download_url + "/components/" + item_id +"/images"
#                print(file, type(filename))
                mime_type, encoding = mimetypes.guess_type(filetoupload)
#                print(mime_type)

                with open(filetoupload, 'rb') as fp:
#                    if data !=None:
#                        files = {
#                            **{key: (None, value) for key, value in data.items()},
#                            'image':(filename, fp, mime_type)}
#                    else:
                    files = {'image':(filename, fp, mime_type)}
                    upload = requests.post(url, files=files, headers=headers)
                    file_ids.append((upload.json())["image_id"])

    return file_ids

def GetTestFilesInHWDB(test_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    url = download_url + "/component-tests/" + str(test_id) +"/images"
    datain = requests.get(url, headers=headers)
    images = datain.json()["data"]

    image_list = []
    for image in images:
        image_list.append(image["image_name"])

    return image_list

def EnterFileToTest(item_name, item_sn, test_type, test_datasheet = None, filelist = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list
    
    qc_tid, qc_type = GetTestTypeID(item_name, test_type)

    if test_datasheet == None:
        print("Test data not provided!")
        exit(1)
    print(test_datasheet[0][0], test_datasheet[0][1]) 
    if test_datasheet[0][0] != 'Test Date' or test_datasheet[0][1] != 'Test Time':
        print("Test data does not have the date and time as first items in the list!")
        exit(1)

    qc_date = test_datasheet[1][0]
    qc_time = test_datasheet[1][1]

    item_id = isPartInHWDB(item_name, item_sn)
    if item_id == None:
        print("The item ", item_name, "with SN", item_sn," is not in the database")
        return None

    test_id = isTestInHWDB(item_id, qc_tid, qc_date, qc_time)
    if test_id == None:
        print("The ", test_type, qc_date, qc_time, " test for ", item_name, "with SN", item_sn," is not in the database")
        return None

    file_ids = []
    if filelist == None:
        print("File list is empty. Please provide at least one file to upload.")
        return None
    else:
        images_list = GetTestFilesInHWDB(test_id)
        for file in filelist:
            filetoupload = file.strip() 
            filename = Path(filetoupload).name
            if (len(images_list) == 0) or ((len(images_list) != 0) and not(filename in images_list)):
                url = download_url + "/component-tests/" + str(test_id) +"/images"
#                print(file, type(filename))
                mime_type, encoding = mimetypes.guess_type(filetoupload)
#                print(mime_type)

                with open(filetoupload, 'rb') as fp:
#                    if data !=None:
#                        files = {
#                            **{key: (None, value) for key, value in data.items()},
#                            'image':(filename, fp, mime_type)}
#                    else:
                    files = {'image':(filename, fp, mime_type)}
                    upload = requests.post(url, files=files, headers=headers)
                    file_ids.append((upload.json())["image_id"])
    return file_ids

#if __name__ == '__main__':

