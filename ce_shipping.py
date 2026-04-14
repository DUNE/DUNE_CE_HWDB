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
import json
import requests
import mimetypes
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
import cv2
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

poc_names = []
poc_emails = []

ce_shipbox_field  = [
                "System Name (ID)",
                "Subsystem Name (ID)",
                "Component Type Name (ID)",
                "DUNE PID"
                ]

ce_shipbox_values = [None for _ in range(4)]


preshipping_name  = [
                "HTS Code",
                "Origin of this shipment",
                "Destination of this shipment",
                "Dimension of this shipment",
	            "Weight of this shipment",
	            "Freight Forwarder name",
	            "Mode of Transportation",
	            "Expected Arrival Date (CT)",
	            "FD Logistics team acknoledgement (name)",
	            "FD Logistics team acknoledgement (date in CT)", 
                "Visual Inspection (YES = no damage)",
                "Visual Inspection Damage",
                "Image ID for this Shipping Sheet"
              ]
shipping_name     = [
                "Image ID for BoL",
	            "Image ID for Proforma Invoice",
	            "Image ID for the Final approval message",
	            "FD Logistics team Final approval (name)",
	            "FD Logistics team Final approval (date in CST)",
	            "DUNE Shipping Sheet has been attached",
	            "This shipment has been adequately insured for transit"
              ]

preshipping_value   = [None for _ in range(13)]
shipping_value      = [None for _ in range(7)]

specification       =[[None for _ in range(2)] for _ in range(1)]
specification[0][0] = "DATA"
specification[0][1] = ""

subcomponents = []
subcomp_names = []

preship_block = []
subids_block = []
ship_block = []

preship_upload, ship_upload, subpids_upload = False, False, False

def itemID(prompt):
    id_val = input(prompt)
    scanned = id_val.strip()
    item = scanned.split("/")
    value = (item[len(item)-1])[0:18]
    return value

def GetItem(item_id):
    
    token = None
    with open(dune_ce_hwdb.tokenloc, 'r') as ft:
        token = ft.read().strip()

    headers = {'Authorization': f'Bearer {token}'}
    url = dune_ce_hwdb.download_url + "/components/" + item_id
    
    item_data = requests.get(url, headers=headers)

    return item_data


def UploadShipping(item_id, data = None, filelist = None, subcomp = None):

    token = None
    with open(dune_ce_hwdb.tokenloc, 'r') as ft:
        token = ft.read().strip()
    headers = {'Authorization': f'Bearer {token}'}

    file_ids = []
    if filelist != None:
        url = dune_ce_hwdb.download_url + "/components/" + item_id +"/images"
        for file in filelist:
            filename = Path(file).name

            print(file, type(filename))
            mime_type, encoding = mimetypes.guess_type(file)
            print(mime_type)

            with open(file, 'rb') as fp:
                if data !=None:
                    files = {
                        **{key: (None, value) for key, value in data.items()},
                        'image':(filename, fp, mime_type)}
                else:
                    files = {
                        'image':(filename, fp, mime_type)}
                upload = requests.post(url, files=files, headers=headers)
                file_ids.append((upload.json())["image_id"])

    elif data != None:
        url = dune_ce_hwdb.download_url + "/components/" + item_id
        upload = requests.patch(url, json=data, headers=headers)

    elif subcomp != None:
        url = dune_ce_hwdb.download_url + "/components/" + item_id + "/subcomponents"
        upload = requests.patch(url, json=subcomp, headers=headers)

    return upload, file_ids

def GetItemFiles(item_id):
    token = None
    with open(dune_ce_hwdb.tokenloc, 'r') as ft:
        token = ft.read().strip()
    headers = {'Authorization': f'Bearer {token}'}

    url = dune_ce_hwdb.download_url + "/components/" + item_id +"/images"

    file_list = None
    get_resp = requests.get(url, headers=headers)
    resp_data = (get_resp.json())["data"]

    file_list = {}
    for i in range(len(resp_data)):
        file = resp_data[i]
        file_list[file["image_id"]] = file["image_name"]

    return file_list


def EnterPreshippingInfo(ce_shipbox_ID):
    global preshipping_names, preshipping_value, specification, poc_names, poc_emails

    os.system('clear')
    print("Please enter the preshipping information below or NA if no information is available.")

    info_loop = True
    while(info_loop):
        poc_name_val = input("Please enter the name of the person(s) of contact (POC) separated by comma: ")
        poc_mail_val = input("Please enter the e-mail(s) of the POCs separated by comma: ")

        poc_name = poc_name_val.strip()
        poc_name = poc_name.split(",")
        if len(poc_name) > 0:
            for name in poc_name:
                poc_names.append(name.strip())
                
        poc_email = poc_mail_val.strip()
        poc_email = poc_email.split(",")
        if len(poc_email) > 0:
            for email in poc_email:
                poc_emails.append(email.strip())        
            
        for i in range(len(preshipping_value)-1):
            preship_val = input(preshipping_name[i]+" :")
            scanned = preship_val.strip()
            scanned = scanned.split("/")
            if scanned[len(scanned)-1] != "NA" and scanned[len(scanned)-1] != "":
                preshipping_value[i] = scanned[len(scanned)-1]
        os.system('clear')
        print("Please verify the information:")
        print("POC names: ",poc_names)
        print("POC emails: ", poc_emails)
        for i in range(len(preshipping_value)-1):
            print(preshipping_name[i]+": ",preshipping_value[i])
        preship_check = input("\n Please verify the information is correct and enter Y to confirm.")
        if preship_check == "Y":
            info_loop = False

def EnterShippingInfo(ce_shipbox_ID):
    global shipping_names, shipping_value
    os.system('clear')
    print("Please enter the shipping information below or NA if no information is available.")

    info_loop = True
    while(info_loop):
        for i in range(len(shipping_value)):
            value = None
            if i<3:
                ship_val = input("File location for the " + shipping_name[i]+" :")
                if len(ship_val)>2:
                    filename = ship_val.strip()
                    status, ids = UploadShipping(ce_shipbox_ID, None, filename)
                    if len(ids) == 1:
                        value = ids[0]

            else:    
                ship_val = input(shipping_name[i]+" :")
                value = ship_val.strip()

            if value != "NA" and value != "":
                shipping_value[i] = value

        os.system('clear')
        print("Please verify the information:")
        for i in range(len(shipping_value)):
            print(shipping_name[i]+": ",shipping_value[i])
        ship_check = input("\n Please verify the information is correct and enter Y to confirm.")
        if ship_check == "Y":
            info_loop = False

    
def EnterComponents():
    global subcomponents

    subcom_loop = True
    while(subcom_loop):
#        subcom_val = input("Please enter subcomponents or enter D for done: ")
#        subcom = subcom_val.strip()
#        subcom = subcom.split("/")
#        subcom_ID = subcom[len(subcom)-1]
        subcom_ID = itemID("Please enter subcomponents or enter D for done: ")
        if subcom_ID != "D":
            if subcom_ID in subcomponents:
                print("Item with ID ", subcom_ID, " is already on the list.")
                continue
            comp_name, serial, resp_inst, resp_inst_id, location, manuf, item_stat, qaqc_cert, installed, qc_upload = dune_ce_hwdb.GetItemDetails(subcom_ID)
            if comp_name == None:
                print("This component doesn't exist in the HWDB.")
                continue
            
            print("You have entered part with:")
            print("Part Name: ", comp_name)
            print("Part SN: ", serial)
            print("Current Location: ", location)
            print("Part Status: ", item_stat)
            print("Part QAQC Cert: ", qaqc_cert)
            conf_val = input("Please confirm by entering Y: ")
            os.system('clear')
            if conf_val == "Y":
                print("Part "+subcom_ID+" is added.")
                subcomp_names.append(comp_name)
                subcomponents.append(subcom_ID)
            else:
                print("Part "+subcom_ID+" is skipped.")
        else:    
            subcom_loop = False

def PreparePreshippingChecklist(ce_shipbox_ID):
    global poc_names, poc_emails, ce_shipbox_values, preshipping_value
   
    sys_name = dune_ce_hwdb.GetSystemName(ce_shipbox_ID)
    sub_name = dune_ce_hwdb.GetSubsystemName(ce_shipbox_ID)
    com_name = dune_ce_hwdb.GetComponentName(ce_shipbox_ID)
    ce_shipbox_values[0] = sys_name
    ce_shipbox_values[1] = sub_name
    ce_shipbox_values[2] = com_name
    ce_shipbox_values[3] = ce_shipbox_ID

    filename = "DUNEShippingSheet_"+ce_shipbox_ID+".pdf"

    c = canvas.Canvas(filename, pagesize = letter)
    width, height = letter
    c.setFont("Times-Roman", 18) 
    c.drawCentredString(0.5*width, 0.95*height, "DUNE Shipping Sheet")
    c.drawImage("QR_"+ce_shipbox_ID+".png",0.1*width,0.55*height, width=0.25*width, preserveAspectRatio=True)
    c.drawImage("BC_"+ce_shipbox_ID+".png",0.5*width,0.65*height, width=0.4*width, preserveAspectRatio=True)
   
    c.setFont("Times-Roman", 16)
    c.drawCentredString(0.5*width, 0.72*height, "dev")
    c.drawCentredString(0.5*width, 0.70*height, com_name)
    c.drawCentredString(0.5*width, 0.68*height, ce_shipbox_ID)
    
    names = ""
    for i in range(len(poc_names)):
        if i != 0:
            names = names + ", " + poc_names[i]
        else:
            names = poc_names[i]

    c.setFont("Times-Roman", 14)
    c.drawCentredString(0.5*width, 0.65*height, "Responsible Person's Name")
    c.rect(0.015*width,0.62*height,.97*width,0.25*inch)
    c.drawCentredString(0.5*width, 0.627*height, names)

    emails = ""
    for i in range(len(poc_emails)):
        if i != 0:
            emails = emails + ", " + poc_emails[i]
        else:
            emails = poc_emails[i]
    
    c.drawCentredString(0.5*width, 0.60*height, "E-mail Adress(es)")
    c.rect(0.015*width,0.57*height,.97*width,0.25*inch)
    c.drawCentredString(0.5*width, 0.577*height, emails)

    c.drawCentredString(0.25*width, 0.55*height, "System Name")
    c.drawCentredString(0.75*width, 0.55*height, "Subsystem Name")
    c.rect(0.015*width,0.52*height,.47*width,0.25*inch)
    c.rect(0.515*width,0.52*height,.47*width,0.25*inch)
    c.drawCentredString(0.25*width, 0.527*height, sys_name)
    c.drawCentredString(0.75*width, 0.527*height, sub_name)

    c.rect(0.015*width,0.48*height,.32*width,0.25*inch)
    c.rect(0.335*width,0.48*height,.32*width,0.25*inch)
    c.rect(0.655*width,0.48*height,.32*width,0.25*inch)
    c.drawCentredString(0.175*width, 0.487*height, "Sub-component PID")
    c.drawCentredString(0.5*width, 0.487*height, "Component Type Name")
    c.drawCentredString(0.815*width, 0.487*height, "Func. Pos. Name")

    box_y = 0.4573*height
    text_y = 0.4643*height
    box_top_y = 0.95*height
    text_top_y = 0.957*height
    delta_y = 0.0227*height

    for i in range(len(subcomponents)):
        comp_name, serial, resp_inst, resp_inst_id, curr_loc, manuf, item_stat, qaqc_cert, installed, qc_upload = dune_ce_hwdb.GetItemDetails(subcomponents[i])
        if i<20:
            box_orig_y  = (box_y - i*delta_y)
            text_orig_y = (text_y - i*delta_y)

            c.rect(0.015*width, box_orig_y,.32*width,0.25*inch)
            c.rect(0.335*width, box_orig_y,.32*width,0.25*inch)
            c.rect(0.655*width, box_orig_y,.32*width,0.25*inch)
            c.drawCentredString(0.175*width, text_orig_y, subcomponents[i])
            c.drawCentredString(0.5*width, text_orig_y, comp_name)
            c.drawCentredString(0.815*width, text_orig_y, "Func. Pos. "+str(i))
        elif i==20:    
            c.showPage()
            c.rect(0.015*width,box_top_y,.32*width,0.25*inch)
            c.rect(0.335*width,box_top_y,.32*width,0.25*inch)
            c.rect(0.655*width,box_top_y,.32*width,0.25*inch)
            c.drawCentredString(0.175*width, text_top_y, "Sub-component PID")
            c.drawCentredString(0.5*width, text_top_y, "Component Type Name")
            c.drawCentredString(0.815*width, text_top_y, "Func. Pos. Name")

            box_orig_y  = (box_top_y - (i-19)*delta_y)
            text_orig_y = (text_top_y - (i-19)*delta_y)
            c.rect(0.015*width, box_orig_y,.32*width,0.25*inch)
            c.rect(0.335*width, box_orig_y,.32*width,0.25*inch)
            c.rect(0.655*width, box_orig_y,.32*width,0.25*inch)
            c.drawCentredString(0.175*width, text_orig_y, subcomponents[i])
            c.drawCentredString(0.5*width, text_orig_y, comp_name)
            c.drawCentredString(0.815*width, text_orig_y, comp_name+str(i))
        elif i<60:
            box_orig_y  = (box_top_y - (i-19)*delta_y)
            text_orig_y = (text_top_y - (i-19)*delta_y)
            c.rect(0.015*width, box_orig_y,.32*width,0.25*inch)
            c.rect(0.335*width, box_orig_y,.32*width,0.25*inch)
            c.rect(0.655*width, box_orig_y,.32*width,0.25*inch)
            c.drawCentredString(0.175*width, text_orig_y, subcomponents[i])
            c.drawCentredString(0.5*width, text_orig_y, comp_name)
            c.drawCentredString(0.815*width, text_orig_y, comp_name+str(i))

    c.showPage()
    c.save()

    get_files = GetItemFiles(ce_shipbox_ID)

    if filename in get_files.values():
        filecheck = input("Pre-shipping checklist is already uploaded.\nPleas confirm upload by entering Y: ")
        if filecheck == "Y":
            preshipping_value[len(preshipping_value)-1] = [k for k, v in get_files.items() if v == filename] 
            return

    filelist = []
    filelist.append(filename)
    response, file_ids = UploadShipping(ce_shipbox_ID, None, filelist)
    preshipping_value[len(preshipping_value)-1] = file_ids[0]

def UploadToHWDB(ce_shipbox_ID):
    global preship_block, subids_block, ship_block, preshipping_value, preshipping_name, subcomponents, subcomp_names, shipping_value, shipping_names
    global preship_upload, ship_upload
#!!!!!!!!!!!!!!!!!!!!!!!!!!!! add more names
    comp_names = "FEMB"

    data_labels = ["Pre-Shipping Checklist", "Shipping Checklist", "SubPIDs"] 
    ship_data = {}
    ship_data["part_id"] = ce_shipbox_ID
    ship_status = {}
    ship_status["id"] = 100
    ship_data["status"] = ship_status
    ship_data["specifications"] = {}
    spec_block = {}

    if len(preship_block) == 0 and preship_upload:
        preship_block.append({"POC name": poc_names[0]})
        preship_block.append({"POC Email": poc_emails})

        last = len(preshipping_value) - 1
        for i in range(len(preshipping_value)):
            if preshipping_value[len(preshipping_value) - 1 - i] != None:
                last = len(preshipping_value) - 1 - i
                break
        for i in range(last+1):
            if  preshipping_value[i] != None:
                preship_block.append({preshipping_name[i]: preshipping_value[i]})


    if len(preship_block) > 0:
        spec_block.update({data_labels[0]:preship_block})        

    if len(subids_block) == 0 and len(subcomponents) > 0:
        for i in range(len(subcomponents)):
            subids_block.append({subcomp_names[i]: subcomponents[i]})
        ship_subcomp = {}
        ship_subcomp["component"] = {}
        ship_subcomp["component"]["part_id"] = ce_shipbox_ID
        subcomp_dict = {}
        for i in range(len(subcomponents)):
            subcomp_dict[comp_names+" "+str(i+1)] = subcomponents[i]
        ship_subcomp["subcomponents"] = subcomp_dict
        UploadShipping(ce_shipbox_ID, None, None, ship_subcomp)

    if len(subids_block) > 0:    
        spec_block.update({data_labels[2]:subids_block})    
        
    if len(ship_block) == 0 and ship_upload:
        last = len(shipping_value) - 1
        for i in range(len(shipping_value)):
            if shipping_value[len(shipping_value) -1 - i] != None:
                last = len(shipping_value) - 1 - i                
                break
        for i in range(last+1):
            if  shipping_value[i] != None:
                ship_block.append({shipping_name[i]: shipping_value[i]})

        if len(subcomponents) > 0:
            for i in range(len(subcomponents)):
                dune_ce_hwdb.UpdateLocation(subcomponents[i], "INTRANSIT")
        else:
            print("No items found in shippment.")
        dune_ce_hwdb.UpdateLocation(ce_shipbox_ID, "INTRANSIT")

    if len(ship_block) > 0:
        spec_block.update({data_labels[1]:ship_block})            

    ship_data["specifications"]["DATA"] = spec_block 

    print(json.dumps(ship_data, indent = 4))

    UploadShipping(ce_shipbox_ID, ship_data)

    if len(subcomponents) > 0:
        ship_subcomp = {}
        ship_subcomp["component"] = {}
        ship_subcomp["component"]["part_id"] = ce_shipbox_ID
        subcomp_dict = {}
        for i in range(len(subcomponents)):
            subcomp_dict[comp_names+" "+str(i+1)] = subcomponents[i]
        ship_subcomp["subcomponents"] = subcomp_dict
        UploadShipping(ce_shipbox_ID, None, None, ship_subcomp)


    preship_upload, ship_upload = False, False   

def Preshipping():
    global preship_upload, subpids_upload

    loop = True
    os.system('clear')
    print("Preparation of Pre-Shipping Checklist")

    ce_shipbox_ID = None
    while(loop):
        val = input("Would you like to create a new CE shipping box? (Y/N): ")
        if val == "Y":
            resp_inst = dune_ce_hwdb.siteloc
            print("Select the responsible institution from the list below:")
            print(dune_ce_hwdb.loc_name_list)
            print("The responsible institution is set to: "+resp_inst)
            inst_loop = True
            while(inst_loop):
                inst = input("Please confirm the selection by entering Y or enter a new institution: ")
                if inst == "Y":
                    inst_loop = False
                elif inst in dune_ce_hwdb.loc_name_list:
                    resp_inst = inst
                    inst_loop = False
                else:
                    input("Wrong entry! Press enter to select again.")
            ce_shipbox_ID = dune_ce_hwdb.EnterItemToHWDB("ce_shipbox", None, resp_inst, "US", "", None, None, None, None, specification)
            dune_ce_hwdb.GetQRCode(ce_shipbox_ID)
            dune_ce_hwdb.GetBarCode(ce_shipbox_ID)

            cont_check = input("Please enter Y to continue with the preshipping checklist.")
            loop = False
            if cont_check != "Y":
                return ce_shipbox_ID

        elif val == "N":
            id_loop = True
            while(id_loop):
#                id_val = input("Scan or enter CE Shipping Box ID: ")                 
#                scanned = id_val.strip()
#                item = scanned.split("/")
#                ce_shipbox_ID = item[len(item)-1]
                ce_shipbox_ID = itemID("Scan or enter CE Shipping Box ID: ")
                if dune_ce_hwdb.isPartIDInHWDB(ce_shipbox_ID):
                    item_name = dune_ce_hwdb.GetItemName(ce_shipbox_ID)
                    item_loc = dune_ce_hwdb.GetItemLocation(ce_shipbox_ID)
                    item_status = dune_ce_hwdb.GetItemStatus(ce_shipbox_ID)
                    print("You have entered part with:")
                    print("Part Name: ", item_name)
                    print("Current Location: ", item_loc)
                    print("Part Status: ", item_status)
                    conf_val = input("Please confirm by entering Y: ")
                    if conf_val == "Y":
                        dune_ce_hwdb.GetQRCode(ce_shipbox_ID)
                        dune_ce_hwdb.GetBarCode(ce_shipbox_ID)
                        id_loop = False
                else:
                    print("The CE Shipping Box ID doesn't exist in the HWDB.")
            
            loop = False
        else:
            input("No CE shipping ID is provided. Exiting to main menu.")
            return
    
    EnterPreshippingInfo(ce_shipbox_ID)
    EnterComponents()
    PreparePreshippingChecklist(ce_shipbox_ID)
    preship_upload = True
    subpids_upload = True
    UploadToHWDB(ce_shipbox_ID)
    return ce_shipbox_ID

def Shipping(shipment_ID = None):
    global preship_block, subids_block, ship_block, preshipping_value, preshipping_name, subcomponents, subcomp_names, shipping_value, shipping_names
    global specification, poc_names, poc_emails, ship_upload

    preship_block.clear()
    ship_block.clear()
    subids_block.clear()
    subcomponents.clear()

    shipID_loop = True
    os.system('clear')
    print("Preparation of Shipping Checklist")
    tryagain = False
    while(shipID_loop):
        if shipment_ID == None or tryagain:
            id_val = input("Scan or enter CE Shipping Box ID: ")
            scanned = id_val.strip()
            item = scanned.split("/")
            ce_shipbox_ID = item[len(item)-1]
        else:
            ce_shipbox_ID = shipment_ID

        tryagain = False 
        item_data = GetItem(ce_shipbox_ID)
        data = (item_data.json())
        if data["status"] != "OK":
            print("CE Shipping box item returns an error while retrieving from HWDB.")         
            tryagain = True
            continue

        ship_data = data["data"]["specifications"][0]["DATA"]

        print(json.dumps(ship_data, indent = 4))
        preship_val = input("Please confirm the shipment info by entering Y: ")
        if preship_val == "Y":
            shipID_loop = False
    
    if "Pre-Shipping Checklist" in ship_data.keys():
        preship_block = ship_data["Pre-Shipping Checklist"]
        for field in preship_block:
            field_items = list(field.items())
            if field_items[0][0] == "POC names":
                poc_names = field_items[0][1]
            elif field_items[0][0] == "POC Emails":
                poc_emails = field_items[0][1]
            elif field_items[0][0] in preshipping_name:
                preshipping_value[preshipping_name.index(field_items[0][0])] = field_items[0][1]
    else:
        print("CE Shipping box ", ce_shipbox_ID, " is missing the Pre-Shipping checklist.")
        return

    if "SubPIDs" in ship_data.keys():
        subids_block = ship_data["SubPIDs"]
        for subcomp in subids_block:
            key=next(iter(subcomp))
            subcomponents.append(subcomp[key])
    else:
        print("CE Shipping box ", ce_shipbox_ID, " is missing the list of items.")


    EnterShippingInfo(ce_shipbox_ID)
    ship_upload = True
    UploadToHWDB(ce_shipbox_ID) 


def Receiving():    
    global preship_block, subids_block, ship_block, preshipping_value, preshipping_name, shipping_value, shipping_names, subcomponents
    global specification, poc_names, poc_emails

    preship_block.clear()
    ship_block.clear()
    subids_block.clear()
    subcomponents.clear()

    shipID_loop = True
    os.system('clear')
    print("CE Shipping Box Receiving")
    ce_shipbox_ID = None
    no_shipping_info = False
    while(shipID_loop):
        no_shipping_info = False
        id_val = input("Scan or enter CE Shipping Box ID: ")
        scanned = id_val.strip()
        item = scanned.split("/")
        ce_shipbox_ID = (item[len(item)-1])[1:21]

        item_data = GetItem(ce_shipbox_ID)
        data = (item_data.json())

        if data["status"] != "OK":
            print("CE Shipping box item returns an error while retrieving from HWDB.")
            continue
        elif len(data) == 0:
            print("This shipping box doens't have any shipping information for precessing.")
            no_shipping_info = True
    
        ship_data = data["data"]["specifications"][0]["DATA"]

        print(json.dumps(ship_data, indent = 4))
        preship_val = input("Please confirm the shipment info by entering Y: ")
        if preship_val == "Y":
            shipID_loop = False
        if len(ship_data) > 0:
            if "Pre-Shipping Checklist" in ship_data.keys():
                preship_block = ship_data["Pre-Shipping Checklist"]
            else:
                print("The shipment is missing the Pre-Shipping Checklist!")
            if "Shipping Checklist" in ship_data.keys():    
                ship_block = ship_data["Shipping Checklist"]
            else:
                print("The shipment is missing the Shipping Checklist!")

    subcomp_fpos, subcomp_pids = dune_ce_hwdb.GetSubcomponents(ce_shipbox_ID)

    mismatch1_ids = []
    mismatch2_ids = []
    ceship_subids = []
    if no_shipping_info:
        if "SubPIDs" in ship_data.keys():    
            subids_block = ship_data["SubPIDs"]
            for subcomp in subids_block:
                key=next(iter(subcomp))
                ceship_subids.append(subcomp[key])
        else:
            print("The shipment has no shipped items listed!")

    print(subcomp_pids, ceship_subids)


#    for subcomp in subids_block:
#        key=next(iter(subcomp))
#        if subcomp[key] not in subcomp_pids:
#            mismatch1_ids.append(subcomp[key])
#    for subid in subcomp_pids:
#        if subid not in subids_block.values():
#            mismatch2_ids.append(subid)
#    if len(mismatch1_ids) != 0:
#        print("The following parts are missing from the subcomponents of the shipping box while listed in the manifest.")
#        print(mismatch1_ids)
#    if len(mismatch2_ids) != 0:
#        print("The following parts are missing form the manifest of the shipping box while linked as subcomponents.")
#        print(mismatch1_ids)

    q_loop = True
    while(q_loop):
        q_val = input("Please confirm if you'd like to continue by pressing Y or press M to exit to the main menu: ")
        if q_val == "Y":
            q_loop = False
        elif q_val == "M":
            return

    os.system('clear')

    if subcomp_pids == None:
        return

    rec_loop = True
    while(rec_loop):
        rec_val = input("If you would like to update all items in the shipping list press \"1\", if you would like to scan the items one by one press \"2\": ")
        if rec_val == "1":
            for i in range(len(subcomp_pids)):
                dune_ce_hwdb.UpdateLocation(subcomp_pids[i])
                subcomponents.append(None)
        elif rec_val == "2":
            subcomponents = subcomp_pids
            subcom_loop = True
            while(subcom_loop):
                subcom_val = input("Please enter/scan subcomponent or enter D for done: ")
                subcom = subcom_val.strip()
                subcom = subcom.split("/")
                subcom_ID = subcom[len(subcom)-1]
                if subcom_ID in subcomp_pids:
                    comp_name, serial, resp_inst, curr_loc, manuf, item_stat, qaqc_cert, installed, qc_upload = dune_ce_hwdb.GetItemDetails(subcom_ID)
                    print("You have entered part with:")
                    print("Part Name: ", comp_name)
                    print("Part SN: ", serial)
                    print("Current Location: ", curr_loc)
                    print("Part Status: ", item_stat)
                    print("Part QAQC Cert: ", qaqc_cert)
                    conf_val = input("Please confirm by entering Y: ")
                    os.system('clear')
                    if conf_val == "Y":
                        dune_ce_hwdb.UpdateLocation(subcom_ID)
                        subcomponents[subcomp_pids.index(subcom_ID)] = None
                        print("Part "+subcom_ID+" status will be updated.\n")
                    else:
                        print("Part "+subcom_ID+" is skipped.\n")

                elif subcomp_ID == "D":
                    subcom_loop = False
                else:
                    print("The item "+subcomp_ID+" is not listed in this shipment.\n")
        else:
            continue

        rec_loop = False    
        comp_names = "FEMB"

        if None in subcomponents:
            
            ship_subcomp = {}
            ship_subcomp["component"] = {}
            ship_subcomp["component"]["part_id"] = ce_shipbox_ID
            subcomp_dict = {}
            for i in range(len(subcomponents)):
                subcomp_dict[subcomp_fpos[i]] = subcomponents[i]
            ship_subcomp["subcomponents"] = subcomp_dict

            UploadShipping(ce_shipbox_ID, None, None, ship_subcomp)    
        dune_ce_hwdb.UpdateLocation(ce_shipbox_ID)


if __name__ == '__main__':
    loop = True
    shipment_ID = None
    while(loop):
        os.system('clear')
        print("1. Create new shipment and/or pre-shipping checklist.")
        print("2. Create shipping checklist.")
        print("3. Receive shipment.")
        print("4. Exit.")
        val = input("Select item: ")
        if val == "1":
            shipment_ID = Preshipping()
        elif val == "2":
            Shipping(shipment_ID) 
        elif val == "3":
            Receiving()
        elif val == "4":
            loop = False

