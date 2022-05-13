import threading,time,requests,json,socket,csv
from FASToryEM import Workstation as WkS
from FASToryEM import configurations as CONFIG
from FASToryEM.dbModels import EnergyMeasurements, WorkstationInfo,MeasurementsForDemo
from FASToryEM import db
# import tensorflow  as tf
# import numpy as np


def SQL_queryToCsv(fileName=None, query=None):
    try:
        
        with open(fileName,'w', newline='') as csvFile:
            
            csvWriter = csv.writer(csvFile, delimiter=',')
            csvWriter.writerow(
                [
                    "WorkCellID", "RmsVoltage(V)", "RmsCurrent(A)", "Power(W)", "NominalPower",
                    "%BeltTension", "ActiveZones", "LoadCombination", "Load"
                ]
            )
            for record in query:
                csvWriter.writerow([
                    record.WorkCellID, record.RmsVoltage, record.RmsCurrent, record.Power,
                    record.Nominal_Power, record.BeltTension, record.ActiveZones, record.LoadCombination, record.Load
                ])

            # send_file("./forWorksation10_PR.csv",
            #             mimetype= 'text/csv',
            #             attachment_filename= 'EM_PatternRecognizer.csv',
            #             as_attachment=True
            #)
    except IOError as e:
         print ("[X-SQL] :",e)
    # if not query:
    #     raise ValueError('No data available')




def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


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
        if id !=10:# and id!=1:
            continue
        temp_obj = WkS.Workstation(id,CONFIG.wrkCellLocIP,
                                    CONFIG.make[id-1],CONFIG.type[id-1],
                                    CONFIG.wrkCellLocPort+id,
                                    CONFIG.num_Fast,CONFIG.num)
        #temp_obj.WkSINFO()
        #deleting past subscription to EM service.
        #temp_obj.invoke_EM_service()
        #now invoke EM service for accurate results
        temp_obj.get_access_token()
        # send_measurements=threading.Timer(8,temp_obj.invoke_EM_service,args=("start",))
        # send_measurements.daemon=True
        # send_measurements.start()
        #startring server for workstation
        threading.Thread(target=temp_obj.runApp,daemon=True).start()
        
        #wait a while for server initialization
        #time.sleep(1)
        #check device registration or register device to ZDMP-DAQ component 
        #temp_obj.register_device()

        #subscribe device for ASYNC data access
        #temp_obj.sub_or_Unsubscribe_DataSource(True)

        #Db functions
        #if you delete DB Schema then call this method. After that comment it.
        #temp_obj.callWhenDBdestroyed()
        #uncomment following line when base IP got changed
        temp_obj.updateIP()

#FASTory BT class-prediction function

# def predict(power,load):
#     model = tf.keras.models.load_model('M_iter3_1.h5', compile=True)
#     features = np.array(np.append([power],[load]), ndmin=2)
#     pred = np.argmax(model.predict(features), axis=1) 
#     #print(f"[X-UTF] {pred[0]}")
#     return pred[0]   

