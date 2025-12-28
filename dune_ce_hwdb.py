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

tokenloc=os.environ.get('TOKENLOC')
hwdbsel=os.environ.get('HWDBSELECT')
commverb=os.environ.get('COMMANDVERB')
siteloc=os.environ.get('SITELOC')

upload_url = "https://dbwebapi2.fnal.gov:8443/cdbdev/api"
if hwdbsel == 'PROD':
    upload_url = "https://dbwebapi2.fnal.gov:8443/cdb/api"

curl_command   = "curl -s --header \"Authorization: Bearer $(cat "+tokenloc+")\""
download_url   = upload_url+"/v1"
upload_command = " -H \"Content-Type: application/json\" -X POST -d @"
file_upload_command = " -F \"image=@"
patch_command  = " -H \"Content-Type: application/json\" -X PATCH -d @"

loc_name_list       = ["FNAL", "BNL", "MSU", "LSU", "LBL", "UCI", "UPENN", "UCINCI"]
loc_id_list         = ["1", "128", "146", "144", "142", "171", "191", "176"]

part_name_list      = ["larasic_p5prep1", "larasic_p5bprep2", "larasic_p5bpr1", "coldadc_p2prep", "coldadc_p2prb1", "coldadc_p2prb2", "coldata_e4prep", "coldata_e4prb1", "coldata_e4prb2", "femb_prep", "wiec", "wib","ptc","ptc_fpga"]
part_id_list        = ["D08100100001", "D08100100003", "D08100100004", "D08100200001", "D08100200002", "D08100200003", "D08100300001", "D08100300002", "D08100300003", "D08100400001", "D08104100001", "D08104200001","D08104300001","D08100800011"]

item_upload_json = "upload_item.json"
add_loc_json     = "add_location.json"
test_upload_json = "upload_test.json"
patch_item_json  = "patch_item.json"

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

def getSummary(item_name, location = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    if item_name in part_name_list:
        item_part_id = part_id_list[part_name_list.index(item_name)]
    else:
        print("Part name is not recognized. Accepted part names are:")
        print(part_name_list)
        exit(1)

    if location != None:
        if location in loc_name_list:
            institution_id = loc_id_list[loc_name_list.index(location)] 
        else:
            print("Location is not recognized. Accepted locations are:")
            print(loc_name_list)
            exit(1)
        get_summary_command = curl_command + " \'" + download_url + "/component-types/" + item_part_id + "/components?location="+institution_id+"\' "+"| jq .pagination.total"    
 
    else:
        get_summary_command = curl_command + " \'" + download_url + "/component-types/" + item_part_id + "/components?\' "+"| jq .pagination.total"

    if commverb == 'VERB1': print(get_summary_command)
    datain = os.popen(get_summary_command)
    numitems = datain.readlines()
    if len(numitems) == 0:
        return None
    else:
        return numitems[0].strip()

def GetItemSN(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    enter_info_download_command = curl_command +" \'" + download_url + "/components/" + item_id + "\' "+" | jq .data.serial_number"
    if commverb == 'VERB1': print(enter_info_download_command)
    
    datain     = os.popen(enter_info_download_command)
    serial  = datain.readlines()
    serial  = serial[0].strip()
    serial  = serial.strip("\"")
#    print(serial)

    return serial

def GetItemName(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    enter_info_download_command = curl_command +" \'" + download_url + "/components/" + item_id + "\' "+" | jq .data.component_type.name"
    if commverb == 'VERB1': print(enter_info_download_command)
    
    datain     = os.popen(enter_info_download_command)
    name  = datain.readlines()
    name  = name[0].strip()
    name  = name.strip("\"")
#    print(name)

    return name


def GetItemLocation(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    enter_info_download_command = curl_command +" \'" + download_url + "/components/" + item_id + "\' "+" | jq .data.location"
    if commverb == 'VERB1': print(enter_info_download_command)
    
    datain     = os.popen(enter_info_download_command)
    loc  = datain.readlines()
    loc  = loc[0].strip()
    loc  = loc.strip("\"")
#    print(name)

    return loc

def GetItemTests(item_id):
    global curl_command, upload_url, download_url
    found_test = False
    found_test_id = 0

    test_time = "No Test" 
    test_date = "No Test"
    get_test_data_command = curl_command + " \'" + download_url + "/components/" + item_id.strip() + "/tests' | jq .data[].test_type"
    if commverb == 'VERB1': print(get_test_data_command)
    command_output = os.popen(get_test_data_command)
    test_type_ids = command_output.readlines()
    print(test_type_ids)

    print(len(test_type_ids))
    if len(test_type_ids)//4 > 0:

        testsList = []
        itest = 0
        test_data = None
        test_name = None
        qc_tid = None
        num_tests = None
        num_fields= None
        for test_tid in test_type_ids:

            qc_tid_line = test_tid.strip()
            qc_tid_line = qc_tid_line.split(":")
            if qc_tid_line[0] == "{":
                itest = itest + 1
            elif qc_tid_line[0] == '\"name\"':
                test_name = qc_tid_line[1].rstrip(",")
            elif qc_tid_line[0] == '\"id\"':
                qc_tid = qc_tid_line[1].rstrip(",")
                qc_tid = qc_tid.lstrip(" ")
            elif qc_tid_line[0] == "}":
                print(itest,test_name,qc_tid)
                for it in range(num_tests):
                    test_data.insert(1+it*num_fields, test_name)
                testsList = testsList + test_data
                test_name = None
                qc_tid = None
                num_tests = None
                num_fields = None

            if qc_tid != None: 
                get_tests_command = curl_command + " \'" + download_url + "/components/" + item_id.strip() + "/tests/" + qc_tid + "?history=True\' " + "| jq .data[].test_data"
                if commverb == 'VERB1': print(get_tests_command)
                command_output = os.popen(get_tests_command)
                test_data = command_output.readlines()
                print(test_data.count("{\n"), len(test_data))
                num_tests = test_data.count("{\n")
                num_fields= int(len(test_data)/num_tests)

        field_list, value_list = FormatInputList(testsList)
        for i in range(len(field_list)):
            print(field_list[i], value_list[i])
        print(field_list.count("\"Test\""))
    if len(test_type_ids)>0:   
        return field_list, value_list
    else:
        return None, None

def FormatInputList(inp_list):

    field_list = []
    value_list = []
    for line in inp_list:
        strline = line.strip()
        strline = strline.rstrip(",")
        strline = strline.lstrip(" ")
        splline = strline.split(":")
        #print(len(splline))
        if len(splline) == 1:
            if splline[0] != "{" and splline[0] != "}":
                value_list.append(splline[0])
                field_list.append("Test")
        elif len(splline) == 2:
            field_list.append(splline[0])
            value_list.append(splline[1])
        elif len(splline) > 2:
            field_list.append(splline[0])
            value_list.append(splline[1]+":"+splline[2])

    return field_list, value_list    

def GetParent(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list
    get_parent_command = curl_command + " \'" + download_url + "/components/" + item_id.strip() + "/container' | jq .data[].container.part_id"
    if commverb == 'VERB1': print(get_parent_command)
    command_output = os.popen(get_parent_command)
    parent = command_output.readlines()
    
    if len(parent)>0:
        parent_id = parent[0].strip()
        parent_id = parent_id.strip("\"")
        return parent_id
    else:
        return None

def GetPartList(item_name):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list
    if item_name in part_name_list:
        item_part_id = part_id_list[part_name_list.index(item_name)]
    else:
        print("Part name is not recognized. Accepted Part names are:")
        print(part_name_list)
        exit(1)
    
    numItems = getSummary(item_name)
    numPages = int(numItems)//100 + 1
    print (numItems, numPages)

    partsList = []
    for i in range(numPages):
        page = str(i+1)
        if commverb == 'VERB1': print(item_name, item_part_id)
        get_partid_command = curl_command + " \'" + download_url + "/component-types/" + item_part_id + "/components?page="+page+"&size=100\' "+" | jq .data[].part_id"
        if commverb == 'VERB1': print(get_partid_command)
 
        datain = os.popen(get_partid_command)
        parts = datain.readlines()
        partsList = partsList + parts
    return partsList

def GetSubcomponents(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list
    get_subcomp_command = curl_command + " \'" + download_url + "/components/" + item_id.strip() + "/subcomponents' | jq .data[] | grep -e 'functional_position' -e 'part_id'"
    if commverb == 'VERB1': print(get_subcomp_command)
    command_output = os.popen(get_subcomp_command)
    subcomps = command_output.readlines()
    #print(subcomps)
    subcomp_pos = []
    subcomp_pid = []
    if len(subcomps)>0:
        field_names, values = FormatInputList(subcomps)
        for i in range(int(len(values)/2)):
            subcomp_pos.append(values[2*i].strip(" "))
            subcomp_pid.append((values[2*i+1].strip(" ")).strip("\""))

    if len(subcomp_pos) > 0:
        return subcomp_pos, subcomp_pid
    else:
        return None, None

def isPartInHWDB(item_name, item_sn):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list
  
    if item_name in part_name_list:
        item_part_id = part_id_list[part_name_list.index(item_name)]
    else:
        print("Part name is not recognized. Accepted Part names are:")
        print(part_name_list)
        exit(1)

    if commverb == 'VERB1': print(item_sn, item_name, item_part_id)

    get_partid_command = curl_command + " \'" + download_url + "/component-types/" + item_part_id + "/components?serial_number="+item_sn+"\' "+" | jq .data[]?.part_id"
    if commverb == 'VERB1': print(get_partid_command)

    datain = os.popen(get_partid_command)
    parts = datain.readlines()
    if commverb == 'VERB1': print(len(parts))
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

def GetTestTypeID(item_name, test_type = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    if test_type == None:
        print("No test type provided.")
        exit(1)
        return None

    if item_name in part_name_list:
        item_part_id = part_id_list[part_name_list.index(item_name)]
    else:
        print("Part name is not recognized. Accepted Part names are:")
        print(part_name_list)
        exit(1)

    item_test_names_command = curl_command + " \'" + download_url + "/component-types/" + item_part_id + "/test-types\'"+"| jq .data[]?.name"
    if commverb == 'VERB1': print(item_test_names_command)

    tnames=os.popen(item_test_names_command)
    test_names = tnames.readlines()

    if len(test_names) == 0:
        print("No tests have been defined for this component type!")
        exit(1)

    item_test_ids_command = curl_command + " \'" + download_url + "/component-types/" + item_part_id + "/test-types\'"+"| jq .data[]?.id"
    if commverb == 'VERB1': print(item_test_ids_command)

    tids=os.popen(item_test_ids_command)
    test_ids = tids.readlines()

    for itest in range(len(test_ids)):
        test_ids[itest]=test_ids[itest].strip()
        test_names[itest]=test_names[itest].strip()
        if commverb == 'VERB1': print(test_ids[itest], test_names[itest])
    
    qc_type = None
    qc_tid = None

    if test_type in test_names:
        qc_type = test_type
    else:
        print("The component "+item_name+" has the following tests:")
        print(test_names)
        exit(1)
        
    if commverb == 'VERB1': print(test_names, test_ids)

    qc_tid = test_ids[test_names.index(qc_type)]
    
    return qc_tid, qc_type

def isTestInHWDB(item_id, qc_tid, qc_date, qc_time):
    global curl_command, upload_url, download_url
    found_test = False
    found_test_id = 0

    test_time = "No Test" 
    test_date = "No Test"
    get_test_data_command = curl_command + " \'" + download_url + "/components/" + item_id.strip() + "/tests/" + qc_tid + "?history=True\' " + "| jq .data[]?.test_data | grep -e 'Test Date' -e 'Test Time'"
    if commverb == 'VERB1': print(get_test_data_command)
    command_output = os.popen(get_test_data_command)
    dates = command_output.readlines()
       
    get_test_ids_command = curl_command + " \'" + download_url + "/components/" + item_id.strip() + "/tests/" + qc_tid + "?history=True\' " + "| jq .data[]?.id"
    if commverb == 'VERB1': print(get_test_ids_command)
    command_output = os.popen(get_test_ids_command)
    tids = command_output.readlines()

    num_tests = int(len(dates))//2
#    print(num_tests)
    if len(dates) != 0:
        for i in range(num_tests):
            date = dates[2*i].split('\"')
            test_date = "\""+date[3]+"\""
            ttime = dates[2*i+1].split('\"')
            test_time = "\""+ttime[3]+"\""
            test_num = tids[i].strip()
            if commverb == 'VERB1': print(i, test_date, test_time, test_num)

            if commverb == 'VERB1': print(qc_date, qc_time)
            if commverb == 'VERB1': print(test_date, test_time)
            if (test_date == qc_date) and (test_time == qc_time):
                found_test = True
                found_test_id = test_num

    if not found_test:
        return None
    else:
        return found_test_id

def EnterItemToHWDB(item_name, item_sn, institution, country_code = "US", comments = "", manufact_id = None, lot_num = None, arrival_date = None, connectors = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    item_id = isPartInHWDB(item_name, item_sn)
    
    if item_id == None:
        item_part_type_id = part_id_list[part_name_list.index(item_name)]
        ItemToUploadJSON(item_sn, item_part_type_id, institution, country_code, comments, manufact_id, lot_num, arrival_date, connectors)

        enter_item_command = curl_command + upload_command + item_upload_json +" \'" + upload_url + "/component-types/" + item_part_type_id + "/components\' " 
        if commverb == 'VERB1': print(enter_item_command)

        upload_result = subprocess.run(enter_item_command, shell=True, text=True).stdout
        item_id = isPartInHWDB(item_name, item_sn)
        if item_id == None:
            print("Item entry for ",item_name, " with SN ", item_sn,  " failed.")
            exit(1)

    UpdateLocation(item_id, institution, comments, arrival_date) 
    
    return item_id


def ItemToUploadJSON(item_sn, part_type_id, institution, country_code = "US", comment = "", manufact_id = "", lot_num = None, arrival_date = None, connectors = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list
    
    institution_id = loc_id_list[loc_name_list.index(institution)]
    
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
#    if part_name_list[part_id_list.index(part_type_id)] == "coldadc": 
#        item_file.write("\t\t\"Documents\": \"Links\",\n")
#        item_file.write("\t\t\"Testing ID\": \"" + item_sn + "\"\n")
    if lot_num != None:
        item_file.write("\t\t\"LOT N\": \""+lot_num+"\"\n")
#    else:
#        item_file.write("\t\t\"LOT N\": \""+""+"\"\n")
#    elif part_name_list[part_id_list.index(part_type_id)] == "coldata":
#        item_file.write("\t\t\"\": \"\"\n")
#    elif part_name_list[part_id_list.index(part_type_id)] == "larasic":
#        item_file.write("\t\t\"\": \"\"\n")
#    elif part_name_list[part_id_list.index(part_type_id)] == "femb":
    if connectors != None:
        for i in range(len(connectors)):
            if i == (len(connectors)-1):
                item_file.write("\t\t\""+connectors[i][0]+"\": \""+ connectors[i][1]+"\"\n")
            else:
                item_file.write("\t\t\""+connectors[i][0]+"\": \""+ connectors[i][1]+"\",\n")

    if lot_num == None and connectors == None:
        item_file.write("\t\t\"\": \"\"\n")
    
    ##### Add Connectors based on item
    if connectors != None:
        item_file.write("\t},\n")
        item_file.write("\t\"subcomponents\": {\n")
        #if "femb" in part_name_list[part_id_list.index(part_type_id)]:    
        for i in range(len(connectors)):
            if i == (len(connectors)-1):
                item_file.write("\t\t\""+connectors[i][0].rstrip(' SN')+"\": \""+ connectors[i][2]+"\"\n")
            else:    
                item_file.write("\t\t\""+connectors[i][0].rstrip(' SN')+"\": \""+ connectors[i][2]+"\",\n")
        item_file.write("\t}\n")
    else:
        item_file.write("\t}\n")
#    item_file.write("\t}\n")
    item_file.write("}\n")
    item_file.close()

def GetCurrentLocation(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    enter_location_download_command = curl_command +" \'" + download_url + "/components/" + item_id + "/locations\' "+" | jq .data[]?.location | grep id"
    if commverb == 'VERB1': print(enter_location_download_command)
    datain     = os.popen(enter_location_download_command)
    locations  = datain.readlines()
    latest_loc = None
    latest_loc_name = None
    if len(locations) != 0:
        latest_loc_id = locations[0].split(':')
        latest_loc = latest_loc_id[1].rstrip(',\n')
        latest_loc = latest_loc.lstrip(' ')
        latest_loc_name = loc_name_list[loc_id_list.index(latest_loc)]
        #print(latest_loc)
    return latest_loc,latest_loc_name    

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
        if commverb == 'VERB1': print(enter_location_upload_command)
        upload_result = subprocess.run(enter_location_upload_command, shell=True, text=True).stdout
    else:
        print("Already at ", latest_loc_name)
        return
      
    updated_location_id, update_location_name = GetCurrentLocation(item_id)
    if updated_location_id != institution_id:
        print("Location update was unsuccessful!")

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

    TestToUploadJSON(qc_type, comment, test_datasheet)
    
    enter_test_upload_command = curl_command + upload_command + test_upload_json +" \'" + download_url + "/components/" + item_id + "/tests\'"" | jq | grep test_id"
    if commverb == 'VERB1': print(enter_test_upload_command)
    upload_result = subprocess.run(enter_test_upload_command, shell=True, text=True).stdout
    this_test_id = isTestInHWDB(item_id, qc_tid, qc_date, qc_time) 
    if commverb == 'VERB1': print(this_test_id)

    if this_test_id == None:
        print("Test upload failed.")
        exit(1)
    else:    
        return this_test_id


def TestToUploadJSON(test_type, comment = "No comment", test_datasheet = None):

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

def GetComponentFilesInHWDB(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    get_images_command = curl_command + " \'" + download_url + "/component-types/" + item_id + "/images\'"+" | jq .data[].image_name"
    if commverb == 'VERB1': print(get_images_command)

    images_in = os.popen(get_images_command)
    images_list = images_in.readlines()

    if(len(images_list) !=0 ):
        for iim in range(len(images_list)):
            images_list[iim] = images_list[iim].strip()
            images_list[iim] = images_list[iim].strip('\"')
#        print(images_list)
        return images_list
    else:
        return None

def EnterFileToType(item_name, filelist = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list
    if item_name in part_name_list:
        component_id = part_id_list[part_name_list.index(item_name)] 
    else:
        print("The part name is not in the list.")
        return None

    if filelist == None:
        print("File list is empty. Please provide at least one file to upload.")
        return None
    else:
        images_list = GetComponentFilesInHWDB(test_id)
        for file in filelist:
            filetoupload = file.strip()
            filetocheck = filetoupload.split("/")
            if (images_list == None) or ((images_list != None) and not(filetocheck[len(filetocheck)-1] in images_list)):
                filetoupload = file.strip()
                upload_file_command =  curl_command + file_upload_command + filetoupload +"\"  \'" + upload_url + "/component-types/" + component_id + "/images\'"
                if commverb == 'VERB1': print(upload_file_command)             
                subprocess.run(upload_file_command, shell=True, text=True).stdout
            else:
                print("File is already in the database.")

def GetItemFilesInHWDB(item_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    get_images_command = curl_command + " \'" + download_url + "/components/" + item_id + "/images\'"+" | jq .data[].image_name"
    if commverb == 'VERB1': print(get_images_command)

    images_in = os.popen(get_images_command)
    images_list = images_in.readlines()

    if(len(images_list) !=0 ):
        for iim in range(len(images_list)):
            images_list[iim] = images_list[iim].strip()
            images_list[iim] = images_list[iim].strip('\"')
#        print(images_list)
        return images_list
    else:
        return None

def EnterFileToItem(item_name, item_sn, filelist = None):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    item_id = isPartInHWDB(item_name, item_sn)
    if item_id == None:
        print("The item ", item_name, "with SN", item_sn, " is not in the database")
        return None
    
    if filelist == None:
        print("File list is empty. Please provide at least one file to upload.")
        return None
    else:
        images_list = GetItemFilesInHWDB(item_id)
        for file in filelist:
            filetoupload = file.strip()
            filetocheck = filetoupload.split("/")
            if (images_list == None) or ((images_list != None) and not(filetocheck[len(filetocheck)-1] in images_list)):
        
                filetoupload = file.strip()
                upload_file_command =  curl_command + file_upload_command + filetoupload +"\"  \'" + upload_url + "/components/" + item_id + "/images\'"
                if commverb == 'VERB1': print(upload_file_command)
                subprocess.run(upload_file_command, shell=True, text=True).stdout
            else:
                print("File is already in the database.")

def GetTestFilesInHWDB(test_id):
    global curl_command, upload_url, download_url, upload_command, loc_name_list, loc_id_list, part_name_list, part_id_list

    get_images_command = curl_command + " \'" + download_url + "/component-tests/" + test_id + "/images\'"+" | jq .data[].image_name"
    if commverb == 'VERB1': print(get_images_command)    

    images_in = os.popen(get_images_command)
    images_list = images_in.readlines()
    
    if(len(images_list) !=0 ):
        for iim in range(len(images_list)):
            images_list[iim] = images_list[iim].strip()
            images_list[iim] = images_list[iim].strip('\"')
#        print(images_list)
        return images_list
    else:
        return None

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

    if filelist == None:
        print("File list is empty. Please provide at least one file to upload.")
        return None
    else:
        images_list = GetTestFilesInHWDB(test_id)
        for file in filelist:
            filetoupload = file.strip()
            filetocheck = filetoupload.split("/")
            if (images_list == None) or ((images_list != None) and not(filetocheck[len(filetocheck)-1] in images_list)):

                upload_file_command =  curl_command + file_upload_command + filetoupload +"\"  \'" + upload_url + "/component-tests/" + test_id + "/images\'"
                if commverb == 'VERB1': print(upload_file_command)
                subprocess.run(upload_file_command, shell=True, text=True).stdout
            else:
                print("File is already in the database.")


#if __name__ == '__main__':

