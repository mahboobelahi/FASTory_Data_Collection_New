import csv
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt 
import numpy as np
import threading,requests,json,time
from pprint import pprint
from flask import Flask,render_template,request,jsonify
from FASToryEM import configurations as CONFIG
from FASToryEM.dbModels import EnergyMeasurements, WorkstationInfo
from FASToryEM import UtilityFunctions as helper
#orchestrator connector object
from FASToryEM import db
from flask_sqlalchemy import SQLAlchemy

power = []
# workstation class

class Workstation:
    def __init__(self, ID, wLocIP, wLocPort):
        # workstation attributes
        self.count=0
        self.stop_recording=0
        self.name = f'FASTory_Energy_Monitoring_E10_Module_WrkStation_{ID}'
        self.ID = ID
        self.source_ID = 0
        self.external_ID = f'{ID}4EM'
        # f'http://{wLocIP}:{wLocPort}' use when working in FASTory network
        self.url_self = f'http://130.230.190.118:{wLocPort}'
        self.port = wLocPort
        self.EM = True
        #workstaion servies
        self.measurement_ADD = f'{self.url_self}/measurements'
        self.EM_service_url = f'http://192.168.{ID}.4/rest/services/send_all_REST'
        self.CNV_start_stop_url = f'http://192.168.{ID}.2/rest/services/'
        #for reat-time grphs
        self.power = 0
        self.voltage = 0
        self.current = 0
        # checking for Z4 and installed EM modules
        if self.ID in CONFIG.hav_no_EM:
            self.EM = False
        if ID == 1 or ID == 7:
            self.hasZone4 = False
        else:
            self.hasZone4 = True


    # *****************************************
    #  WorkstationClass mutators and DB section
    # *****************************************
    
    def callWhenDBdestroyed(self):
        # inserting info to db
        #one time call, only uncomment when db destroyed otherwise
        #do the update
        info = WorkstationInfo(
                                WorkCellName=self.name,
                                WorkCellID =self.ID,
                                DAQ_ExternalID =self.external_ID,
                                DAQ_SourceID = self.source_ID,
                                HasZone4 = self.hasZone4,
                                HasEM_Module = self.EM,
                                WorkCellIP= self.url_self,
                                EM_service_url = self.EM_service_url,
                                CNV_service_url = self.CNV_start_stop_url
                                )
        db.session.add(info)
        db.session.commit()
 
    
    def updateIP(self):
        WrkIP=WorkstationInfo.query.get(self.ID)
        WrkIP.WorkCellIP = self.url_self
        #WrkIP=WorkstationInfo.query.filter(WorkstationInfo.WorkCellID==self.ID)
        #WrkIP.update({WorkstationInfo.WorkCellIP:self.url_self})
        db.session.commit()
    
    # accessors and setters

    def get_ID(self):
        return self.ID

    def WkSINFO(self):
        pprint(self.__dict__)

    def has_EM(self):
        return self.EM

    def set_has_EM(self, flage):
        self.EM = flage

    def set_source_ID(self, srID):
        self.source_ID = srID

    def set_count(self,num=0):
        self.count=num

    def count_inc(self):
        self.count =self.count+1
    
    def stop_recording_inc(self):
        self.stop_recording = self.stop_recording+1
  
    def set_stop_recording(self,num=0):
      self.stop_recording = num


    def update_PVC(self,p,v,c):
        self.power = p
        self.voltage = v
        self.current = c
        print(self.power)

    # *********************************************
    # Workstation Methods
    # *********************************************
    # auto start/stop energy-measurement service

    def invoke_EM_service(self, cmd='stop'):
        if self.EM == False:
            print("Has no EM module.")
            return
        body = {
            "cmd": cmd,
            "send_measurement_ADDR": self.measurement_ADD,
            "ReceiverADDR":''#'http://130.230.190.18:2010/noware'#f'{self.url_self}/noware'
        }
        try:
            r = requests.post(url=self.EM_service_url, json=body,timeout=3)
            r.raise_for_status()
            return jsonify({"payload":body,"Status Code":r.status_code,"Reason":r.reason})
        except requests.exceptions.HTTPError as errh:
            print ("[X-W] Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("[X-W] Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("[X-W] Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("[X-W] OOps: Something Else",err)   
        return jsonify({"Message": "Not Connected to Line" },{"Response":None})
                  
        

    # registration to ZDMP-DAQ component
    def register_device(self):
        # need to set some guard condition to avoid re-registration of device
        # each device registared against a unique external ID
        req = requests.get(
            url=f'{CONFIG.ADMIN_URL}/deviceInfo?externalId={self.external_ID}')
        if req.status_code == 200:
            self.set_source_ID(req.json().get('id'))
            print('[X-W] Device already Registered. Device details are:\n')
            # pprint(req.json())
        else:
            print('[X-W] Registering the device')
            req_R = requests.post(
                url=f'{CONFIG.ADMIN_URL}/registerDevice?externalId={self.external_ID}&name={self.name}&type=c8y_Serial')
            print(f'Http Status Code: {req_R.status_code}')
            # setting souece ID of device
            self.set_source_ID(req_R.json().get('id'))
            print('[X-W] Device Registered Successfully.\n')
            # pprint(req_R.json())

    # register data source to ASYNC-DAQ service
    def sub_or_Unsubscribe_DataSource(self, subs=False):
        
        try:
            if subs:
                req = requests.get(f'{CONFIG.ASYNCH_URL}/unsubscribe',
                                params={"externalId": self.external_ID, "topicType": 'multi'})
                print(f'[X-W] Subscribing to Data Source: {self.external_ID}....{req.status_code}')
                req = requests.get(f'{CONFIG.ASYNCH_URL}/subscribe',
                                params={"externalId": self.external_ID, "topicType": 'multi'})
                if req.status_code == 200:
                    print(f'[X-W] Subscrption Status: {req.status_code} {req.reason}')
                else:
                    print(f'[X-W] Subscrption Status: {req.status_code} {req.reason}')
            else:
                req = requests.get(f'{CONFIG.ASYNCH_URL}/unsubscribe',
                                params={"externalId": self.external_ID, "topic": 'multi'})

                if req.status_code == 200:
                    print(f'[X-W] Unsubscrption Status: {req.status_code} {req.reason}')
                else:
                    print(f'[X-W] Unsubscrption Status: {req.status_code} {req.reason}')
        except requests.exceptions.HTTPError as errh:
            print ("[X-W] Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("[X-W] Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("[X-W] Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("[X-W] OOps: Something Else",err)
    # checks for active zones on conveyor of a particular workstation
    
    def get_ZoneStatus(self):
        load = 0
        ActiveZone = ''
        for i in [1, 2, 3,4, 5]:
            req = requests.get(
                f'http://192.168.{self.ID}.2/rest/services/Z{i}', json={"destUrl": ""})
            if req.json().get('PalletID') =='-1':
                ActiveZone =ActiveZone+'0'
            else:
                ActiveZone =ActiveZone+'1'
                load =load+1    
        return (load,ActiveZone)

    def info(self):
        """
        This method gives information of object on which it is called
        :return: object information dictionary
        """
        return self.__dict__

    # *******************************************
    #   Flask Application
    # *******************************************

    def runApp(self):
        """
        Set the flask application
        :return:none
        """
        # ,
        app = Flask(__name__)  # template_folder='./workstations'
        app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mahboobelahi93@localhost/fastoryemdb'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        
        # Flask application routes
        @app.route('/', methods=['GET'])
        def home():
            
            context = {"ID": self.ID, "url": self.url_self}
            return render_template(f'workstations/Workstation.html', title=f'Wrk{self.ID}', content=context)

        @app.route('/info')  # ,methods=['GET']
        def info():
            
            return render_template(f'workstations/info.html',
                                     title='Information',
                                     info=WorkstationInfo.query.get(self.ID))

        #EM measurements from FASTory received here and stored to DB
        @app.route('/measurements', methods=['GET','POST'])
        def insert_measurements2Db():
            global count, power, stop_recording
            
            if request.method == 'GET':
                if self.EM:
                    measurements = EnergyMeasurements.query.filter_by(WorkCellID=self.ID).order_by(EnergyMeasurements.id.desc())[:500]
                    
                    return render_template(f'workstations/measurements.html',
                                            title='History',
                                            measurements=measurements)
                else:
                    return jsonify({"EM-Module":self.EM,"Message": f"Workstation_{self.ID} has no S1000-EM modules" },{"Measurements":[]})
            else:
                if self.EM:
                    az,l = self.get_ZoneStatus()
                    print(type(request.json))
                    print(request.json)
                    data_in=request.json
                    power.append(data_in.get("active_power_c"))
                    self.count_inc()
  
                    #Averaging the power
                    if self.count ==10 and self.stop_recording<=500:
                        AvgPower = round(sum(power)/len(power),3)
                        nominalPower = round((AvgPower/ 1000) * 100,3)
                        measurements =EnergyMeasurements(
                                WorkCellID= self.ID,
                                RmsVoltage=data_in.get("rms_voltage_c"),
                                RmsCurrent=data_in.get("rms_current_c"),
                                Power=AvgPower,
                                Nominal_Power=nominalPower,
                                ActiveZones=az,
                                Load=l,
                                info=data_in.get("CellID"))

                        db.session.add(measurements)
                        db.session.commit()
                        self.stop_inc()
                        print(f'Record added to DB({self.ID})....{self.count}-{self.stop_recording}-{az}-{l}')
                        self.set_count(0)
                        self.stop_recording_inc()
                        power.clear()
                        # sending measurements to ZDMP-DAQ
                        req_V=requests.post(url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=CurrentMeasurement&value={measurements[2]}&unit=A')
                        req_A=requests.post(url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=VoltageMeasurement&value={measurements[1]}&unit=V')
                        req_P=requests.post(url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=PowerMeasurement&value={measurements[3]}&unit=W' )
                        #for real-time plot ---->  power,voltage,current
                        self.update_PVC(measurements[3], measurements[1],measurements[2])
                        return jsonify({"results":data_in.get("active_power_c")})
                    self.set_stop_recording()
                    time.sleep(10)
                #print( f'{req_A.status_code}, {req_V.status_code}, {req_P.status_code}, {req_pred.status_code}, {external_ID}',{row["Class_3"]})
                return'NOT-OK'
        # for jQuery
        @app.route('/measurements/history', methods=['GET'])
        def history():
            from time import time
            x=int(time()) * 1000
            return jsonify([x,self.power])#jsonify({"results":self.data})

        @app.route('/meaurements/real-time',methods=['GET'])
        def realTimePlot():
            from time import time
            return render_template(f'workstations/live_data.html',title='RT-Plot',ID=self.ID)
            
        @app.route('/services', methods=['GET'])
        def services():
            return render_template(f'workstations/services.html')

        @app.route('/fastory_services', methods=['GET'])
        def fastory_services():
            return render_template(f'workstations/cnv_services.html',Z4=self.hasZone4)
        
        @app.route('/s1000_services', methods=['GET'])
        def s1000_services():
            print(f'[X-W] {self.has_EM()}')
            return render_template(f'workstations/s1000_services.html',EM=self.has_EM())

        @app.route('/cnv_cmd', methods=['POST'])
        def cnv_cmd():
            #i do not want to change S1000 code
            cmd=request.form["cnv"]#CNV section
            cnv=request.form["cmd"]#comand
            
            if cnv =='start':
                payload={"cmd":cmd, "ReceiverADDR":self.url_self}
                try:
                    r = requests.post(f'{self.CNV_start_stop_url}StartUnCondition',json=payload,timeout=3)
                    r.raise_for_status()
                    return jsonify({"payload":payload,"Status Code":r.status_code,"Reason":r.reason})
                except requests.exceptions.HTTPError as errh:
                    print ("[X-W] Http Error:",errh)
                except requests.exceptions.ConnectionError as errc:
                    print ("[X-W] Error Connecting:",errc)
                except requests.exceptions.Timeout as errt:
                    print ("[X-W] Timeout Error:",errt)
                except requests.exceptions.RequestException as err:
                    print ("[X-W] OOps: Something Else",err)
                
                return jsonify({"payload":payload,"Message": "Not Connected to Line" },{"Response":None})
            else:
                payload={"cmd":cmd, "ReceiverADDR":self.url_self}
                try:
                    r = requests.post(f'{self.CNV_start_stop_url}StopUnCondition',json=payload,timeout=3)
                    r.raise_for_status()
                    return jsonify(payload,{"Status Code":r.status_code,"Reason":r.reason})
                except requests.exceptions.HTTPError as errh:
                    print ("[X-W] Http Error:",errh)
                except requests.exceptions.ConnectionError as errc:
                    print ("[X-W] Error Connecting:",errc)
                except requests.exceptions.Timeout as errt:
                    print ("[X-W] Timeout Error:",errt)
                except requests.exceptions.RequestException as err:
                    print ("[X-W] OOps: Something Else",err)               
                return jsonify({"payload":payload,"Message": "Not Connected to Line" },{"Response":None})

        @app.route('/E10_services',methods=['POST'])
        def E10_services():
            cmd=request.form["cmd"]
            if cmd =='start':
                #return jsonify({"cmd":cmd},{"Message": "Not Connected to Line" },{"Status-Code":403})
                res=self.invoke_EM_service(cmd)
                return res
            else:
                res= self.invoke_EM_service()
                return res
        
        # simulation routes
        @app.route('/simulate_predicitons',methods=['POST'])
        def simulate_predictions():
            def send_():
                while(True):
                    try:
                        payload = {"externalId":self.external_ID,
                            "fragment": f'belt-tension-class-pred'
                            }  
                        with open(CONFIG.FILE_NAME, 'r') as file: #with open('N_Measurements9.csv', 'r') as file:
                            reader = csv.DictReader(file)                       
                            # sending measurements to ZDMP-DAQ
                            for row in reader:
                                Power = row["Power (W)"]
                                load = row["Load Combinations"]
                                features= np.round(np.array(np.append( CONFIG.Power_scaler.transform( [[Power]] ),
                                 CONFIG.Load_scaler.transform( [[load]] ) ),
                                  ndmin=2),4)
                                  
                                req_pred=requests.post(url=f'{CONFIG.SYNCH_URL}/sendCustomMeasurement',
                                            params=payload,
                                            json={"powerConsumption": round(features[0][0],3),
                                                    "load":round(features[0][1],3)},
                                                    timeout=3)
                                req_V=requests.post(url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=CurrentMeasurement&value={row["RMS Current (A)"]}&unit=A')
                                req_A=requests.post(url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=VoltageMeasurement&value={row["RMS Voltage (V)"]}&unit=V')
                                req_P=requests.post(url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=PowerMeasurement&value={row["Power (W)"]}&unit=W' )

                                print(f'[X-W-sm] ("{req_A.status_code}, {req_V.status_code}, {req_P.status_code}, {req_pred.status_code}, {self.external_ID}, {features}, {row["Class_3"]})')
                                time.sleep(2)
                    except requests.exceptions.HTTPError as errh:
                        print ("[X-W-sm] Http Error:",errh)
                    except requests.exceptions.ConnectionError as errc:
                        print ("[X-W-sm] Error Connecting:",errc)
                    except requests.exceptions.Timeout as errt:
                        print ("[X-W-sm] Timeout Error:",errt)
                    except requests.exceptions.RequestException as err:
                        print ("[X-W-sm] OOps: Something Else",err) 
                    except OSError:
                        print ("[X-W-sm] Could not open/read file:", CONFIG.FILE_NAME)

            send_loop_thread= threading.Thread(target=send_)
            send_loop_thread.daemon = True
            send_loop_thread.start()
            return jsonify({"Response":200})

        @app.route('/simulate_measurements', methods=['POST'])
        def simulate_measurements():
            
            def send_():
                counter=1
                while(True):
                    #PR values must be added
                    records= EnergyMeasurements.query.filter_by(WorkCellID=self.ID).all()
                    for measurement in records:
                        #for real-time HighCharts
                        try:
                            self.update_PVC(measurement.Power,measurement.RmsVoltage,measurement.RmsCurrent)
                            # sending measurements to ZDMP-DAQ
                            req_A=requests.post(url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=CurrentMeasurement&value={measurement.RmsCurrent}&unit=A',timeout=3)
                            # #time.sleep(0.2)
                            req_V=requests.post(url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=VoltageMeasurement&value={measurement.RmsVoltage}&unit=V',timeout=3)
                            # #time.sleep(0.2)
                            req_P=requests.post(url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=PowerMeasurement&value={measurement.Power}&unit=W',timeout=3 )
                            print(f'[X-W-sm] ("{self.external_ID}", "{req_V.status_code}", "{req_A.status_code}", "{req_P.status_code}" "{counter}")')
                            time.sleep(1)
                        except requests.exceptions.HTTPError as errh:
                            print ("[X-W-sm] Http Error:",errh)
                        except requests.exceptions.ConnectionError as errc:
                            print ("[X-W-sm] Error Connecting:",errc)
                        except requests.exceptions.Timeout as errt:
                            print ("[X-W-sm] Timeout Error:",errt)
                        except requests.exceptions.RequestException as err:
                            print ("[X-W-sm] OOps: Something Else",err) 
                    counter = counter+1
            send_loop_thread= threading.Thread(target=send_)
            send_loop_thread.daemon = True
            send_loop_thread.start()
            return jsonify({"Response":200})
        app.run(host='0.0.0.0', port=self.port)
