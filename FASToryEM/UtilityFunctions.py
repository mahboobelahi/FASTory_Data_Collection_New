import threading,time,requests,csv,json
from FASToryEM import Workstation as WkS
from FASToryEM import configurations as CONFIG
from FASToryEM.dbModels import EnergyMeasurements,WorkstationInfo
from FASToryEM import db
from datetime import datetime
from flask import jsonify

#creating data base modles
def createModels():
    db.create_all()

#Workcell Instructions from MsgBus
def invoke_EM_service(url,cmd='stop'):
    body = {
        "cmd": cmd,
        "send_measurement_ADDR": '',
        "ReceiverADDR":''
    }
    try:
        r = requests.post(url=url, json=body,timeout=3)
        r.raise_for_status()
        return {"Status Code":r.status_code,"Reason":r.reason}
    except requests.exceptions.HTTPError as errh:
        print ("[X-UTF] Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("[X-UTF] Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("[X-UTF] Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("[X-UTF] OOps: Something Else",err)   
    return None  
        

def cnv_cmd(cmd,section,url,url_self):
    if cmd =='start':
        payload={"cmd":section, "ReceiverADDR":url_self}
        try:
            r = requests.post(f'{url}StartUnCondition',json=payload,timeout=3)
            r.raise_for_status()
            return {"Status Code":r.status_code,"Reason":r.reason}
        except requests.exceptions.HTTPError as errh:
            print ("[X-UTF] Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("[X-UTF] Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("[X-UTF] Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("[X-UTF] OOps: Something Else",err)
        return None

    else:
        payload={"cmd":section, "ReceiverADDR":url_self}
        try:
            r = requests.post(f'{url}StopUnCondition',json=payload,timeout=3)
            r.raise_for_status()
            return {"Status Code":r.status_code,"Reason":r.reason}
        except requests.exceptions.HTTPError as errh:
            print ("[X-UTF] Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("[X-UTF] Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("[X-UTF] Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("[X-UTF] OOps: Something Else",err)
        return None      

def Workstations():
    
    for id in range(1,len(CONFIG.WorkStations)+1):
        if id !=10:
            continue
        temp_obj = WkS.Workstation(id,CONFIG.wrkCellLocIP,
                                    CONFIG.wrkCellLocPort+id)
        #temp_obj.WkSINFO()
        #deleting past subscription to EM service.
        # temp_obj.invoke_EM_service()
        #now invoke EM service for accurate results
        # send_measurements=threading.Timer(8,temp_obj.invoke_EM_service,args=("start",))
        # send_measurements.daemon=True
        # send_measurements.start()
        #startring server for workstation
        threading.Thread(target=temp_obj.runApp,daemon=True).start()
        
        #wait a while for server initialization
        time.sleep(1)
        #check device registration or register device to ZDMP-DAQ component 
        #temp_obj.register_device()

        #subscribe device for ASYNC data access
        temp_obj.sub_or_Unsubscribe_DataSource(True)

        #Db functions
        #if you delete DB Schema then call this method. After that comment it.
        #temp_obj.callWhenDBdestroyed()
        #uncomment following line when base IP got changed
        temp_obj.updateIP()






def dumyMeasurements():
    with open(CONFIG.FILE_NAME, 'r') as file: 
        reader = csv.DictReader(file)
        count=0
        for row in reader:

            Voltage= row["RMS Voltage (V)"]
            Current= row["RMS Current (A)"]
            _Power= row["Power (W)"]
            Nominal_Power = row["Normalized_Power"]
            Active_Zones = row["Load Combinations"]#will come from zone status service
            _Load = row["Load"]
            json_str=json.dumps((Voltage,Current,_Power,
            Nominal_Power,Active_Zones,_Load))
            print(json_str)
            time.sleep(.1)
            requests.post("http://130.230.190.118:2002/simulate_measurements",json=json_str)
            time.sleep(.1)
            requests.post("http://130.230.190.118:2003/simulate_measurements",json=json_str)
            time.sleep(.1)
            requests.post("http://130.230.190.118:2004/simulate_measurements",json=json_str)
            time.sleep(.1)
            requests.post("http://130.230.190.118:2005/simulate_measurements",json=json_str)
            time.sleep(.1)
            requests.post("http://130.230.190.118:2006/simulate_measurements",json=json_str)
            time.sleep(.1)
            requests.post("http://130.230.190.118:2009/simulate_measurements",json=json_str)
            time.sleep(.1)
            requests.post("http://130.230.190.118:2010/simulate_measurements",json=json_str)
            time.sleep(.1)
            requests.post("http://130.230.190.118:2011/simulate_measurements",json=json_str)
            time.sleep(.1)
            requests.post("http://130.230.190.118:2012/simulate_measurements",json=json_str)
            time.sleep(1)
             

# from FASToryEM.UtilityFunctions import dumysimulate_Measurements as DM
