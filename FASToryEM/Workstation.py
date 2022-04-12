import csv,socket
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import threading, requests, json, time
from pprint import pprint as P
from flask import Flask, redirect, render_template, request, jsonify, url_for,flash,send_from_directory
from FASToryEM import configurations as CONFIG
from FASToryEM.dbModels import EnergyMeasurements, WorkstationInfo,MeasurementsForDemo
from FASToryEM import UtilityFunctions as helper
# orchestrator connector object
#EnergyMeasurements.query.filter_by(ActiveZones='1001').update(dict(LoadCombination=9))
from FASToryEM import db
from flask_sqlalchemy import SQLAlchemy
import os
from  sqlalchemy.sql.expression import func




# workstation class

class Workstation:
    def __init__(self, ID, wLocIP, make ,type, wLocPort,numFast,num):
        # token
        self.token = ''
        self.access_token_time = 0
        self.expire_time = 0
        self.headers = {}
        # workstation attributes
        self.count = 0
        self.stop_recording = 0
        self.LoadCombination = 0
        self.activeZones = ''
        self.classLabel = 2
        self.BeltTension = 0
        self.make = make
        self.type = type
        self.name = f'FASTory_Energy_Monitoring_E10_Module_WrkStation_{ID}'
        self.ID = ID
        self.source_ID = 0
        self.external_ID = f'{ID}4EM'
        #self.url_self = f'http://{wLocIP}:{wLocPort}' #use when working in FASTory network
        self.url_self = f'http://{self.get_local_ip()}:{wLocPort}'#130.230.190.118
        self.port = wLocPort
        self.EM = True
        # workstaion servies
        self.measurement_ADD = f'{self.url_self}/measurements'
        self.EM_service_url = f'http://192.168.{ID}.4/rest/services/send_all_REST'
        self.CNV_start_stop_url = f'http://192.168.{ID}.2/rest/services/'
        # for reat-time grphs
        self.powerlist = []
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
        self.num = num #request timeout
        self.numFast = numFast
        self.stop_simulation = False
        
    # *****************************************
    #  WorkstationClass mutators and DB section
    # *****************************************

    def callWhenDBdestroyed(self):
        # inserting info to db
        # one time call, only uncomment when db destroyed otherwise
        # do the update
        info = WorkstationInfo(
            WorkCellName=self.name,
            WorkCellID=self.ID,
            RobotMake = self.make,
            RobotType = self.type,
            DAQ_ExternalID=self.external_ID,
            DAQ_SourceID=self.source_ID,
            HasZone4=self.hasZone4,
            HasEM_Module=self.EM,
            WorkCellIP=self.url_self,
            EM_service_url=self.EM_service_url,
            CNV_service_url=self.CNV_start_stop_url
        )
        db.session.add(info)
        db.session.commit()

    def updateIP(self):
        WrkIP = WorkstationInfo.query.get(self.ID)
        WrkIP.WorkCellIP = self.url_self
        # WrkIP=WorkstationInfo.query.filter(WorkstationInfo.WorkCellID==self.ID)
        # WrkIP.update({WorkstationInfo.WorkCellIP:self.url_self})
        db.session.commit()

    # accessors and setters

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def get_ID(self):
        return self.ID
    
    def get_external_ID(self):
        return self.external_ID
    
    def get_headers(self):
        return self.headers
    
    def get_stop_simulation(self):
        return self.stop_simulation

    def WkSINFO(self):
        P(self.__dict__)

    def has_EM(self):
        return self.EM

    def set_has_EM(self, flage):
        self.EM = flage

    def set_source_ID(self, srID):
        self.source_ID = srID

    def set_count(self, num=0):
        self.count = num

    def count_inc(self):
        self.count = self.count + 1
        return self.count

    def stop_recording_inc(self):
        self.stop_recording = self.stop_recording + 1

    def set_stop_recording(self, num=0):
        self.stop_recording = num

    def set_stop_simulations(self,flag):
        self.stop_simulation =flag

    def updatePR_parameters(self, L, AZ):
        self.load = L
        self.activeZones = AZ

    def updateClassLabel(self, CL,BT,lc):
        self.classLabel = CL
        self.BeltTension = BT
        self.LoadCombination = lc

    def update_PVC(self, p, v, c):
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
            "ReceiverADDR": 'http://192.168.100.100:2000/noware'  # f'{self.url_self}/noware'
        }
        try:
            r = requests.post(url=self.EM_service_url, json=body)
            #r.raise_for_status()
            #return jsonify({"payload": body, "Status Code": r.status_code, "Reason": r.reason})
        except requests.exceptions.RequestException as err:
            print("[X-W] OOps: Something Else", err)
        #return jsonify({"Message": "Not Connected to Line"}, {"Response": None})

    # related to DAQ
    # events/alarms/deviceControl etc

    def handleAlarms(self):
        pass

    def sendEvent(self, type, text):
        payload = {"externalId": self.get_external_ID(),
                   "type": type,
                   "text": text}
        try:
            req = requests.post(f'{CONFIG.SYNCH_URL}/sendEvent',
                                params=payload,
                                headers=self.get_headers())
            print(f'[X-W-SnDE] {req.status_code}')
            if req.status_code !=200:
                time.sleep(1)
                req = requests.post(f'{CONFIG.SYNCH_URL}/sendEvent',
                                params=payload,
                                headers=self.get_headers())
                                
        except requests.exceptions.RequestException as err:
            print("[X-W-SnDE] OOps: Something Else", err)

    def deviceControl(self):
        pass

    # registration to ZDMP-DAQ component
    def register_device(self):
        # need to set some guard condition to avoid re-registration of device
        # each device registared against a unique external ID
        try:
            req = requests.get(
                url=f'{CONFIG.ADMIN_URL}/deviceInfo?externalId={self.external_ID}',
                headers=self.headers)
            if req.status_code == 200:
                self.set_source_ID(req.json().get('id'))
                print('[X-W-RD] Device already Registered. Device details are:\n')
                # pprint(req.json())
            else:
                print('[X-W-RD] Registering the device')
                req_R = requests.post(
                    url=f'{CONFIG.ADMIN_URL}/registerDevice?externalId={self.external_ID}&name={self.name}&type=c8y_Serial',
                    headers=self.headers)
                print(f'Http Status Code: {req_R.status_code}')
                # setting souece ID of device
                self.set_source_ID(req_R.json().get('id'))
                print('[X-W-RD] Device Registered Successfully.\n')
                # pprint(req_R.json())
        # except requests.exceptions.HTTPError as errh:
        #     print("[X-W-RD] Http Error:", errh)
        # except requests.exceptions.ConnectionError as errc:
        #     print("[X-W-RD] Error Connecting:", errc)
        # except requests.exceptions.Timeout as errt:
        #     print("[X-W-RD] Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("[X-W-RD] OOps: Something Else", err)

    # register data source to ASYNC-DAQ service
    def sub_or_Unsubscribe_DataSource(self, subs=False):

        payload = {"externalId": self.external_ID, "topicType": 'multi'}
        try:
            if subs:
                req = requests.get(f'{CONFIG.ASYNCH_URL}/unsubscribe',
                                   params=payload, headers=self.headers)
                self.sendEvent('DAQ-ASYNC', 'Data source have unsubscribed to previous subscriptions.....')
                print(f'[X-W-SUD] Subscribing to Data Source: {self.external_ID}....{req.status_code}')
                req = requests.get(f'{CONFIG.ASYNCH_URL}/subscribe',
                                   params=payload, headers=self.headers)
                if req.status_code == 200:
                    self.sendEvent('DAQ-ASYNC', 'Data source have subscribed to ASYNC data access...')
                    print(f'[X-W-SUD] Subscription Status: {req.status_code} {req.reason}')
                elif req.status_code == 500 or req.status_code == 408:
                    time.sleep(1)
                    req = requests.get(f'{CONFIG.ASYNCH_URL}/subscribe',
                                       params=payload, headers=self.headers)
                    if req.status_code == 200:
                        self.sendEvent('DAQ-ASYNC', 'Data source have subscribed to ASYNC data access...')
                        print(f'[X-W-SUD] Subscription Status: {req.status_code} {req.reason}')

                else:

                    print(f'[X-W-SUD] Subscription Status: {req.status_code} {req.reason}')
            else:
                req = requests.get(f'{CONFIG.ASYNCH_URL}/unsubscribe',
                                   params=payload, headers=self.headers)

                if req.status_code == 200:
                    print(f'[X-W-SUD] Unsubscribe Status: {req.status_code} {req.reason}')
                else:
                    print(f'[X-W-SUD] Unsubscribe Status: {req.status_code} {req.reason}')

        except requests.exceptions.RequestException as err:
            print("[X-W-SUD] OOps: Something Else", err)

    # checks for active zones on conveyor of a particular workstation

    def get_ZoneStatus(self):
        load = 0
        ActiveZone = ''
        for i in [1, 2, 3, 5]:
            req = requests.post(
                f'http://192.168.{self.ID}.2/rest/services/Z{i}', json={"destUrl": ""})
            if req.json().get('PalletID') == '-1':
                ActiveZone = ActiveZone + '0'
            else:
                ActiveZone = ActiveZone + '1'
                load = load + 1
        return (load, ActiveZone[::-1])

    def info(self):
        """
        This method gives information of object on which it is called
        :return: object information dictionary
        """
        return self.__dict__

    def get_access_token(self):
        try:
            ACCESS_URL = "https://keycloak-zdmp.platform.zdmp.eu/auth/realms/testcompany/protocol/openid-connect/token"
            headers = {'accept': "application/json", 'content-type': "application/x-www-form-urlencoded"}
            payload = "grant_type=password&client_id=ZDMP_API_MGMT_CLIENT&username=zdmp_api_mgmt_test_user&password=ZDMP2020!"
            response = requests.post(ACCESS_URL, data=payload, headers=headers)
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                self.access_token_time = int(time.time())
                self.expire_time = response.json().get('expires_in')
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print(f'[X-W-Tk] ({response.status_code})')
                self.sendEvent('Token', 'Accessing Token......')
            else:
                print(f"[X-W-Tk] {response.status_code}")
        except requests.exceptions.RequestException as err:
            self.sendEvent('Token', 'Not Accessed......')
            print("[X-W-Tk] OOps: Something Else", err)
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
        @app.route('/class', methods=['POST'])
        def hom():
            
            self.updateClassLabel(request.json.get("cl"),request.json.get("BT"),request.json.get("lc"))
            print(self.classLabel,self.BeltTension,self.LoadCombination)
            
            return "OK:"

        @app.route('/', methods=['GET','POST'])
        def home():
            if request.method == 'GET':
                context = {"ID": self.ID, "url": self.url_self}
                return render_template(f'workstations/Workstation.html', title=f'Wrk{self.ID}', content=context)
            else:
                self.set_stop_recording()
                self.set_count()
                return "OK"

        @app.route('/info')  # ,methods=['GET']
        def info():

            return render_template(f'workstations/info.html',
                                   title='Information',
                                   info=WorkstationInfo.query.get(self.ID))
        ###########Measurements for PR##########
# EM measurements from FASTory received here and stored to DB
        @app.route('/PR-measurements', methods=['GET', 'POST'])
        def measurements4PR():
         
            if int(time.time() - self.access_token_time) >= (self.expire_time - 50):
                print(f'[X-W-sm] Accessing New Token.......')
                self.get_access_token()
            
            if request.method == 'GET':
            
                page = request.args.get('page',1,type=int)
                measurements = MeasurementsForDemo.query.filter_by(WorkCellID=self.ID).order_by(
                    MeasurementsForDemo.id.desc()).paginate(per_page=20, page=page )#[:500]
                if measurements:
                    return render_template(f'workstations/PR_measurements.html',
                                        title='History',
                                        contxt={"measurements":measurements,
                                                        "id":self.ID,
                                                        "hasEM":self.EM})
                else:
                    return render_template(f'workstations/PR_measurements.html',
                                        title='History',
                                        contxt={"measurements":measurements,
                                                        "id":self.ID,
                                                        "hasEM":self.EM})

            else:
                if self.EM:
                    self.count_inc()
                    print(self.count,self.stop_recording,self.classLabel)

                    # Averaging the power
                    print(f'-----{request.json.get("active_power_c")}')
                    if self.count == 10 and self.stop_recording <= 100:
                        l,az = self.get_ZoneStatus()
                        #print(type(request.json),az, l)
                        #print(request.json)
                        data_in = request.json
                        self.powerlist.append(data_in.get("active_power_c"))


                        AvgPower = round(sum(self.powerlist) / len(self.powerlist), 3)
                        nominalPower = round((AvgPower / 1000) * 100, 3)
                        nP = np.round(CONFIG.Power_scaler.transform([[AvgPower]]),4)[0,0]
                        nL = np.round(CONFIG.Load_scaler.transform([[l]]),4)[0,0]
                        pred = helper.predict(nP,nL)
                        measurements = EnergyMeasurements( 
                            WorkCellID=self.ID,
                            RmsVoltage=data_in.get("rms_voltage_c"),
                            RmsCurrent=data_in.get("rms_current_c"),
                            Power=AvgPower,
                            Nominal_Power=nominalPower,
                            ActiveZones=az,
                            LoadCombination = self.LoadCombination,
                            Load=l,
                            BeltTension = self.BeltTension,
                            TrueClass = self.classLabel,
                            NormalizedPower = nP,
                            NormalizedLoad = nL,
                            PredictedClass = pred,
                            Fkey=data_in.get("CellID"),
                            line_Frequency = data_in.get("line_frequency")
                            
                            )

                        db.session.add(measurements)
                        db.session.commit()

                        # if want to sending measurements to ZDMP-DAQ then uncomment following requests
                        # req_V = requests.post(
                        #     url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=CurrentMeasurement&value={data_in.get("rms_current_c")}&unit=A',
                        #     headers=self.headers)
                        # req_A = requests.post(
                        #     url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=VoltageMeasurement&value={data_in.get("rms_voltage_c")}&unit=V',
                        #     headers=self.headers)
                        # req_P = requests.post(
                        #     url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=PowerMeasurement&value={AvgPower}&unit=W',
                        #     headers=self.headers)
                        # print( f'[X-W-DAQ] ({req_A.status_code}, {req_V.status_code}, {req_P.status_code})')
                        print(f'[X-PR] Record added to DB({self.ID})....{self.count}-{self.stop_recording}-{az}-{l}-{self.classLabel}--{pred}')
                        self.set_count()
                        self.stop_recording_inc()
                        self.powerlist.clear()
                        # for real-time plot ---->  power,voltage,current
                        self.update_PVC(AvgPower, data_in.get("rms_voltage_c"), data_in.get("rms_current_c"))
                        return jsonify({"results": data_in.get("active_power_c")})

                
                return 'NOT-OK'
        ########################################
        # EM measurements from FASTory received here and stored to DB
        @app.route('/measurements', methods=['GET', 'POST'])
        def insert_measurements2Db():
            
            #print(f'[X-W-sm] ({self.access_token_time}, {self.expire_time}, {int(time.time() - self.access_token_time)})')
            
            if int(time.time() - self.access_token_time) >= (self.expire_time - 50):
                print(f'[X-W-sm] Accessing New Token.......')
                self.get_access_token()
            
            if request.method == 'GET':
            
                page = request.args.get('page',1,type=int)
                measurements = MeasurementsForDemo.query.filter_by(WorkCellID=self.ID).order_by(
                    MeasurementsForDemo.id.desc()).paginate(per_page=20, page=page )#[:500]
                if measurements:
                    return render_template(f'workstations/measurements.html',
                                        title='History',
                                        contxt={"measurements":measurements,
                                                        "id":self.ID,
                                                        "hasEM":self.EM})
                else:
                    return render_template(f'workstations/measurements.html',
                                        title='History',
                                        contxt={"measurements":measurements,
                                                        "id":self.ID,
                                                        "hasEM":self.EM})

            else:
                if self.EM:
                    self.count_inc()
                    print(self.count,self.stop_recording)

                    # Averaging the power
                    if self.count == 10 and self.stop_recording <= 100:
                        l,az = self.get_ZoneStatus()
                        print(type(request.json),az, l)
                        #print(request.json)
                        data_in = request.json
                        self.powerlist.append(data_in.get("active_power_c"))


                        AvgPower = round(sum(self.powerlist) / len(self.powerlist), 3)
                        nominalPower = round((AvgPower / 1000) * 100, 3)
                        measurements = MeasurementsForDemo( #EnergyMeasurements MeasurementsForDemo
                            WorkCellID=self.ID,
                            RmsVoltage=data_in.get("rms_voltage_c"),
                            RmsCurrent=data_in.get("rms_current_c"),
                            Power=AvgPower,
                            Nominal_Power=nominalPower,
                            ActiveZones=az,
                            Load=l,
                            Fkey=data_in.get("CellID"),
                            line_Frequency = data_in.get("line_frequency")
                            #info=data_in.get("CellID")
                            )

                        db.session.add(measurements)
                        db.session.commit()

                        # sending measurements to ZDMP-DAQ
                        # req_V = requests.post(
                        #     url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=CurrentMeasurement&value={data_in.get("rms_current_c")}&unit=A',
                        #     headers=self.headers)
                        # req_A = requests.post(
                        #     url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=VoltageMeasurement&value={data_in.get("rms_voltage_c")}&unit=V',
                        #     headers=self.headers)
                        # req_P = requests.post(
                        #     url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=PowerMeasurement&value={AvgPower}&unit=W',
                        #     headers=self.headers)
                        # print( f'[X-W-DAQ] ({req_A.status_code}, {req_V.status_code}, {req_P.status_code})')
                        print(f'[X-WdbA] Record added to DB({self.ID})....{self.count}-{self.stop_recording}-{az}-{l}')
                        self.set_count()
                        self.stop_recording_inc()
                        self.powerlist.clear()
                        # for real-time plot ---->  power,voltage,current
                        self.update_PVC(AvgPower, data_in.get("rms_voltage_c"), data_in.get("rms_current_c"))
                        return jsonify({"results": data_in.get("active_power_c")})
                    #self.set_stop_recording()
                    #time.sleep(10)
                
                return 'NOT-OK'

        # for jQuery
        @app.route('/measurements/history', methods=['GET'])
        def history():
            from time import time
            x = int(time()) * 1000
            return jsonify([x, self.power])  # jsonify({"results":self.data})

        @app.route('/meaurements/real-time', methods=['GET'])
        def realTimePlot():
            from time import time
            return render_template(f'workstations/live_data.html', title='RT-Plot', ID=self.ID)

        @app.route('/services', methods=['GET'])
        def services():
            return render_template(f'workstations/services.html')

        @app.route('/fastory_services', methods=['GET'])
        def fastory_services():
            return render_template(f'workstations/cnv_services.html', Z4=self.hasZone4)

        @app.route('/s1000_services', methods=['GET'])
        def s1000_services():
            print(f'[X-W-sS] {self.has_EM()}')
            return render_template(f'workstations/s1000_services.html', EM=self.has_EM())

        @app.route('/cnv_cmd', methods=['POST'])
        def cnv_cmd():
            # i do not want to change S1000 code
            cmd = request.form["cnv"]  # CNV section
            cnv = request.form["cmd"]  # comand
            self.sendEvent('CNV', f'Received command "{cnv}" for "{cmd}" CNV section(s)')
            if cnv == 'start':
                payload = {"cmd": cmd, "ReceiverADDR": self.url_self}
                try:
                    r = requests.post(f'{self.CNV_start_stop_url}StartUnCondition', json=payload, timeout= self.numFast)
                    r.raise_for_status()

                    #jsonify({"payload": payload, "Status Code": r.status_code, "Reason": r.reason})
                except requests.exceptions.RequestException as err:
                    flash('Test','error')
                    print("[X-W-cC] OOps: Something Else", err)
                    return redirect(url_for('services'))
                flash("Service Execuated.","info")
                return redirect(url_for('services'))#return jsonify({"payload": payload, "Message": "Not Connected to Line"}, {"Response": None})
            else:
                payload = {"cmd": cmd, "ReceiverADDR": self.url_self}
                try:
                    r = requests.post(f'{self.CNV_start_stop_url}StopUnCondition', json=payload,timeout=self.numFast)
                    r.raise_for_status()
                    # jsonify(payload, {"Status Code": r.status_code, "Reason": r.reason})
                except requests.exceptions.RequestException as err:
                    flash('Test','Danger')
                    print("[X-W-cC] OOps: Something Else", err)
                    return redirect(url_for('services'))
                flash("Service Execuated.")
                return redirect(url_for('services'))#return jsonify({"payload": payload, "Message": "Not Connected to Line"}, {"Response": None})

        @app.route('/E10_services', methods=['POST'])
        def E10_services():
            cmd = request.form["cmd"]

            if cmd == 'start':
                # return jsonify({"cmd":cmd},{"Message": "Not Connected to Line" },{"Status-Code":403})
                res = self.invoke_EM_service(cmd)
                self.sendEvent('S1000-E10', f'Energy Service has {cmd}')
                return redirect(url_for('services'))#res
            else:
                res = self.invoke_EM_service()
                self.sendEvent('S1000-E10', f'Energy Service has {cmd}')
                return redirect(url_for('services'))# res

        # simulation routes
        @app.route('/api/stop_simulations', methods =['POST'])
        def stop_simulations():
            self.set_stop_simulations(True)
            return "ok"

        @app.route('/api/start_simulations', methods =['POST'])
        def start_simulations():
            self.set_stop_simulations(False)
            requests.post(f'{self.url_self}/api/simulate_measurements')
            return "ok"

        #with belt prediction data
        @app.route('/api/simulate_predicitons', methods=['GET','POST'])
        def simulate_predictions():
            def send_():
                while True:
                    if self.get_stop_simulation() == True:
                        print("in predection-While")
                        break      
                    try:
                        count = 0
                        payload = {"externalId": self.external_ID,
                                "fragment": f'belt-tension-class-pred'
                                }
                        records = EnergyMeasurements.query.filter_by(WorkCellID=self.ID).order_by(func.random()).limit(5).all()
                        with open(CONFIG.FILE_NAME, 'r') as file:  # with open('N_Measurements9.csv', 'r') as file:
                            reader = csv.DictReader(file)
                            # sending measurements to ZDMP-DAQ
                            #.order_by(func.random()).limit(5)
                            for row in reader:
                                if self.get_stop_simulation() == True:
                                    print("in predection-FOR")
                                    break
                                Power = row["Power(W)"]
                                load = row["LoadCombination"]
                                features = np.round(np.array(np.append(CONFIG.Power_scaler.transform([[Power]]),
                                                                    CONFIG.Load_scaler.transform([[load]])),
                                                            ndmin=2), 4)

                                
                                
                                req_pred = requests.post(url=f'{CONFIG.SYNCH_URL}/sendCustomMeasurement',
                                                        params=payload, headers=self.headers,
                                                        json={"powerConsumption": round(features[0][0], 3),
                                                            "load": round(features[0][1], 3)})

                                #print(f'[X-SP] ("{self.count_inc()}, {self.external_ID}, {req_pred.status_code},{features}, {row["Class_3"]}, {[Power, load]})')# {req_A.status_code}, {req_V.status_code}, {req_P.status_code}, {req_pred.status_code},
                                time.sleep(1)
                                helper.predict(features[0][0],features[0][1])
                        self.set_count()
                        #send_()

                    except requests.exceptions.RequestException as err:
                        print("[X-SP] OOps: Something Else", err)
                    except OSError:
                        print("[X-SP] Could not open/read file:", CONFIG.FILE_NAME)
                print("[X-SP] Return from FUNC")
                return 

            send_loop_thread = threading.Thread(target=send_)
            send_loop_thread.daemon = True
            send_loop_thread.start()
            return jsonify({"Response": 200})

        @app.route('/api/simulate_measurements', methods=['GET','POST'])
        def simulate_measurements():

            def send_():
                while True:
                    if self.get_stop_simulation() == True:
                        print("[X-W-SM] in simulate_measurements-while")
                        break
                    # PR values must be added
                    records = MeasurementsForDemo.query.filter_by(WorkCellID=self.ID).all()
                    for measurement in records:
                        if self.get_stop_simulation() == True:
                            print("[X-W-SM] in simulate_measurements-FOR ")
                            break
                        if int(time.time() - self.access_token_time) >= (self.expire_time - 50):
                            print(f'[X-W-SM] Accessing New Token.......')
                            self.get_access_token()
                        try:
                            # for real-time HighCharts
                            self.update_PVC(measurement.Power, measurement.RmsVoltage, measurement.RmsCurrent)
                            # sending measurements to ZDMP-DAQ
                            req_A = requests.post(
                                url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=CurrentMeasurement&value={measurement.RmsCurrent}&unit=A',       
                                headers=self.headers)
                            req_V = requests.post(
                                url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=VoltageMeasurement&value={measurement.RmsVoltage}&unit=V',   
                                headers=self.headers)
                            req_P = requests.post(
                                url=f'{CONFIG.SYNCH_URL}/sendMeasurement?externalId={self.external_ID}&fragment=PowerMeasurement&value={measurement.Power}&unit=W',
                                headers=self.headers)
                            print(f'[X-W-SM] ("{self.get_stop_simulation()}, {self.external_ID}", "{req_V.status_code}", "{req_A.status_code}", "{req_P.status_code}" "{self.count}")')
                            time.sleep(1)  
                        except requests.exceptions.RequestException as err:
                            print("[X-W-SM] OOps: Something Else", err)
                    # self.set_stop_simulations(True)
                    # time.sleep(1)
                    # self.set_stop_simulations(False)
                print("[X-W-SM] Return from FUNC")
                return 

            send_loop_thread = threading.Thread(target=send_)
            send_loop_thread.daemon = True
            send_loop_thread.start()
            requests.post(self.url_self+'/api/simulate_predicitons')
            
            return jsonify({"Response": 200})

        app.run(host='0.0.0.0', port=self.port)#0.0.0.0 192.168.100.100
