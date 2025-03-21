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

certpwd=os.environ.get('HWDBPASSWD')
certpath=os.environ.get('HWDBCERTPATH')
hwdbsel=os.environ.get('HWDBSELECT')

upload_url = "https://dbwebapi2.fnal.gov:8443/cdbdev/api"
if hwdbsel == 'PROD':
    upload_url = "https://dbwebapi2.fnal.gov:8443/cdb/api"

curl_command   = "curl --cert "+certpath+" --pass "+certpwd
download_url   = upload_url+"/v1"
upload_command = " -H \"Content-Type: application/json\" -X POST -d @"

loc_name       = ["FNAL", "BNL", "MSU", "LSU", "LBL", "UCI", "UPENN", "UCINCI"]
loc_id         = ["1", "128", "146", "144", "142", "171", "191", "176"]

part_name      = ["larasic", "coldadc", "coldata", "femb"]
part_id        = ["D08100100001", "D08100200001", "D08100300001", "D08100400001"]

item_upload_json = "item_to_upload.json"
add_loc_json     = "add_location.json"
test_upload_json = "test_upload_1.json"

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


def isPartInHWDB(item_sn, item_type):
    global curl_command, upload_url, download_url, upload_command, loc_name, loc_id, part_name, part_id
  
    item_part_id = part_id[part_name.index(item_type)]
    print(item_sn, item_type, item_part_id)
    get_partid_command = curl_command + " \'" + download_url + "/component-types/" + item_part_id + "/components?serial_number="+item_sn+"\' "+" | jq .data[]?.part_id"
    print(get_partid_command)
    datain = os.popen(get_partid_command)
    parts = datain.readlines()
    print(len(parts))
    if len(parts) == 0:
        return None
    elif len(parts) == 1:
        part = parts[0].rstrip()
        part = part.split('\"')
        item_id = part[1]
        return item_id
    else:
        part = parts[len(parts)-1].rstrip()
        part = part.split('\"')
        item_id = part[1]
        return item_id


def isTestInHWDB(item_id, qc_tid, qc_date, qc_time):
    global curl_command, upload_url, download_url
    found_test = False
    found_test_id = 0

    get_tests_command = curl_command + " \'" + download_url + "/components/" + item_id.strip() + "/tests\' " + "| jq .data[]?.test_type | grep id"
    print(get_tests_command)   
    tests = os.popen(get_tests_command)
    test_types = tests.readlines()

#    print(test_types)
#    print(len(test_types))
    if len(test_types) == 0:
        return None
    for test in test_types:
#        print(test)
        test_name = "No Test"
        test_time = "No Test" 
        test_id = "No Test"
        test_set = test.rstrip(',\n')
        test_set = test_set.split(': ')
#        print(test_set[1])
        test_id = test_set[1]
#        print(test_id)
        get_test_data_command = curl_command + " \'" + download_url + "/components/" + item_id.strip() + "/tests/" + test_id + "?history=True\' " + "| jq .data[]?.test_data | grep -i -e date -e time"
        print(get_test_data_command)
        command_output = os.popen(get_test_data_command)
        dates = command_output.readlines()
       
        get_test_ids_command = curl_command + " \'" + download_url + "/components/" + item_id.strip() + "/tests/" + test_id + "?history=True\' " + "| jq .data[]?.id"
        print(get_test_ids_command)
        command_output = os.popen(get_test_ids_command)
        tids = command_output.readlines()

        num_tests = int(len(dates))//2
#        print(num_tests)
        if len(dates) != 0:
            for i in range(num_tests):
                date = dates[2*i].split('\"')
                test_date = "\""+date[3]+"\""
                ttime = dates[2*i+1].split('\"')
                test_time = "\""+ttime[3]+"\""
                test_num = tids[i].strip()
#                print(i, test_date, test_time, test_num)

#                print(qc_tid, qc_date, qc_time)
#                print(test_id, test_date, test_time)
                if (test_date == qc_date) and (test_time == qc_time) and (test_id == qc_tid):
                    found_test = True
                    found_test_id = test_num

    if not found_test:
        return None
    else:
        return found_test_id

def EnterItemToHWDB(item_sn, item_type, institution, country_code = "US", comments = "", manufact_id = None, lot_num = None, arrival_date = None, connectors = None):
    global curl_command, upload_url, download_url, upload_command, loc_name, loc_id, part_name, part_id

    item_id = isPartInHWDB(item_sn, item_type)
    
    if item_id == None:
        item_part_type_id = part_id[part_name.index(item_type)]
        ItemToUploadJSON(item_sn, item_part_type_id, institution, country_code, comments, manufact_id, lot_num, arrival_date, connectors)

#        exit(0)

        enter_item_command = curl_command + upload_command + item_upload_json +" \'" + upload_url + "/component-types/" + item_part_type_id + "/components\' " 
        print(enter_item_command)

        upload_result = subprocess.run(enter_item_command, shell=True, text=True).stdout
        item_id = isPartInHWDB(item_sn, item_type)

    AddLocation(item_id, institution, comments, arrival_date) 
    
    return item_id

def ItemToUploadJSON(item_sn, part_type_id, institution, country_code = "US", comment = "", manufact_id = "", lot_num = None, arrival_date = None, connectors = None):
    global curl_command, upload_url, download_url, upload_command, loc_name, loc_id, part_name, part_id
    
    institution_id = loc_id[loc_name.index(institution)]
    
    item_file  = open(item_upload_json,"w") 
    item_file.write("{\n")
    item_file.write("\t\"component_type\":{\n")
    item_file.write("\t\t\"part_type_id\": \"" + part_type_id + "\"\n")
    item_file.write("\t},\n")
    item_file.write("\t\"serial_number\": \"" + item_sn +"\",\n")
    item_file.write("\t\"country_code\": \""+ country_code + "\",\n")
    item_file.write("\t\"comments\": \"" + comment + "\",\n")
    item_file.write("\t\"institution\": {\n")
    item_file.write("\t\t\"id\": " + institution_id  +"\n")
    item_file.write("\t},\n")
    item_file.write("\t\"manufacturer\": {\n")
    item_file.write("\t\t\"id\": " + manufact_id +"\n")
    item_file.write("\t},\n")
    item_file.write("\t\"specifications\": {\n")
    #####  Modify Specifications based on item
    if part_name[part_id.index(part_type_id)] == "coldadc": 
#        item_file.write("\t\t\"Documents\": \"Links\",\n")
#        item_file.write("\t\t\"Testing ID\": \"" + item_sn + "\"\n")
        if lot_num != None:
            item_file.write("\t\t\"LOT N\": \""+lot_num+"\"\n")
        else:
            item_file.write("\t\t\"LOT N\": \""+""+"\"\n")
    elif part_name[part_id.index(part_type_id)] == "coldata":
        item_file.write("\t\t\"\": \"\"\n")
    elif part_name[part_id.index(part_type_id)] == "larasic":
        item_file.write("\t\t\"\": \"\"\n")
    elif part_name[part_id.index(part_type_id)] == "femb":
        if connectors != None:
            for i in range(len(connectors)):
                if i == (len(connectors)-1):
                    item_file.write("\t\t\""+connectors[i][0]+"\": \""+ connectors[i][1]+"\"\n")
                else:
                    item_file.write("\t\t\""+connectors[i][0]+"\": \""+ connectors[i][1]+"\",\n")
    
    ##### Add Connectors based on item
    if connectors != None:
        item_file.write("\t},\n")
        item_file.write("\t\"subcomponents\": {\n")
        if part_name[part_id.index(part_type_id)] == "femb":    
            for i in range(len(connectors)):
                if i == (len(connectors)-1):
                    item_file.write("\t\t\""+connectors[i][0].rstrip(' SN')+"\": \""+ connectors[i][2]+"\"\n")
                else:    
                    item_file.write("\t\t\""+connectors[i][0].rstrip(' SN')+"\": \""+ connectors[i][2]+"\",\n")
            item_file.write("\t}\n")
    else:
        item_file.write("\t}\n")
    item_file.write("}\n")
    item_file.close()

def AddLocation(item_id, institution, comments = "", arrival_date = None):
    global curl_command, upload_url, download_url, upload_command, loc_name, loc_id, part_name, part_id
    institution_id = loc_id[loc_name.index(institution)]

    enter_location_download_command = curl_command +" \'" + download_url + "/components/" + item_id + "/locations\' "+" | jq .data[]?.location | grep id"
    print(enter_location_download_command)
    datain     = os.popen(enter_location_download_command)
    locations  = datain.readlines()
    latest_loc = None 
    if len(locations) != 0:
        latest_loc_id = locations[0].split(':')
        latest_loc = latest_loc_id[1].rstrip(',\n')
        latest_loc = latest_loc.lstrip(' ')
        #print(latest_loc) 
        
    if (latest_loc == None) or (latest_loc != institution_id):
        arrival_time = arrival_date
        if arrival_date == None:
            arrival_time = "{}".format(datetime.datetime.now().replace(microsecond=0))

        loc_file = open(add_loc_json,"w")
        loc_file.write("{\n")
        loc_file.write("\t\"arrived\": \"" + arrival_time + "\",\n")
        loc_file.write("\t\"comments\": \"" + comments + "\",\n")
        loc_file.write("\t\"location\": {\n")
        loc_file.write("\t\t\"id\": " + institution_id +"\n")
        loc_file.write("\t}\n")
        loc_file.write("}\n")
        loc_file.close()

        enter_location_upload_command = curl_command + upload_command + add_loc_json +" \'" + download_url + "/components/" + item_id + "/locations\'" 
        print(enter_location_upload_command)
        upload_result = subprocess.run(enter_location_upload_command, shell=True, text=True).stdout

def EnterTestToHWDB(item_sn, item_type, test_type, comment = "No comment", test_datasheet = None):
    global curl_command, upload_url, download_url, upload_command, loc_name, loc_id, part_name, part_id

    if test_datasheet == None:
        print("No datasheet provided.")
        return None

    item_id = isPartInHWDB(item_sn, item_type)
    print(item_id)
    if item_id == None:
        print("This item is not in the database")
        return None
    
    item_part_id = part_id[part_name.index(item_type)]
    item_test_names_command = curl_command + " \'" + download_url + "/component-types/" + item_part_id + "/test-types\'"+"| jq .data[]?.name" 
    print(item_test_names_command)
#    names = subprocess.run(item_test_names_command, shell=True, text=True).stdout
    tnames=os.popen(item_test_names_command)
    test_names = tnames.readlines()

    if len(test_names) == 0:
        print("No tests have been defined for this component type!")
        return None

    item_test_ids_command = curl_command + " \'" + download_url + "/component-types/" + item_part_id + "/test-types\'"+"| jq .data[]?.id"
    print(item_test_ids_command)
    tids=os.popen(item_test_ids_command) 
    test_ids = tids.readlines()

    for itest in range(len(test_ids)):
        test_ids[itest]=test_ids[itest].strip()
        test_names[itest]=test_names[itest].strip()
#        print(test_ids[itest], test_names[itest])


    if item_type == "coldadc":
        if test_type == "rt":
            qc_type = "\"RoomT QC Test\""
        elif test_type == "ln":
            qc_type = "\"CryoT QC Test\""

    qc_tid = test_ids[test_names.index(qc_type)]
    qc_date = test_datasheet[1][0]
    qc_time = test_datasheet[1][1]
    
    checkTest = isTestInHWDB(item_id, qc_tid, qc_date, qc_time)
    if checkTest != None:
        print("This test is already in the database")
        print("Test ID = ", checkTest)
        return checkTest

    TestToUploadJSON(qc_type, comment, test_datasheet)
    
    enter_test_upload_command = curl_command + upload_command + test_upload_json +" \'" + download_url + "/components/" + item_id + "/tests\'"" | jq | grep test_id"
    print(enter_test_upload_command)
#    upload_result = subprocess.run(enter_test_upload_command, shell=True, text=True).stdout
    this_test_id = isTestInHWDB(item_id, qc_tid, qc_date, qc_time) 
    print(this_test_id)

    if this_test_id == None:
        print("Test upload failed.")
        exit(1)
    else:    
        return this_test_id


def TestToUploadJSON(test_type, comment = "No comment", test_datasheet = None):

    if test_datasheet == None:
        print("No datasheet provided.")
        return None

    item_file  = open(test_upload_json,"w")
    item_file.write("{\n")
    item_file.write("\t\"test_type\":" + test_type + ",\n")
    item_file.write("\t\"comments\": \"" + comment + "\",\n")
    item_file.write("\t\"test_data\":{\n")
    num_data = len(test_datasheet[0])
    for i in range(num_data):
        if i < (num_data - 1):
            item_file.write("\t\t\"" + test_datasheet[0][i] + "\": " + test_datasheet[1][i]  + ",\n")
        elif i == (num_data - 1):
            item_file.write("\t\t\"" + test_datasheet[0][i] + "\": " + test_datasheet[1][i]  + "\n")
    item_file.write("\t}\n")
    item_file.write("}\n")
    item_file.close()


#if __name__ == '__main__':

