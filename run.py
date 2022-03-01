from FASToryEM import app
from flask_mqtt import Mqtt
from FASToryEM import UtilityFunctions as helper
from FASToryEM import configurations as CONFIG
#from FASToryEM.msgBus import MqqtClient
from FASToryEM.dbModels import EnergyMeasurements,WorkstationInfo
import time,threading,json


# app.config['MQTT_CLIENT_ID'] = CONFIG.MQTT_CLIENT_ID
# app.config['MQTT_USERNAME'] = CONFIG.NAME
# app.config['MQTT_BROKER_URL'] = CONFIG.MQTT_BROKER_URL  # use the free broker from HIVEMQ
# app.config['MQTT_BROKER_PORT'] = CONFIG.zMSG_TLS_PORT#zMSG_PORT  # default port for non-tls connection
# app.config['MQTT_USERNAME'] = CONFIG.USER  # set the username here if you need authentication for the broker
# app.config['MQTT_PASSWORD'] = CONFIG.PASSWORD  # set the password here if the broker demands authentication
# app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
# app.config['MQTT_TLS_ENABLED'] = True#CONFIG.MQTT_TLS_ENABLED # set TLS to disabled for testing purposes
# app.config['MQTT_TLS_CA_CERTS'] = 'ca_certificate.pem' #MQTT_TLS_CA_CERTS
# app.config['MQTT_TLS_INSECURE'] = True#-'MQTT_TLS_CERTFILE'
# # app.config["MQTT_TLS_KEYFILE"] = None
# # app.config["MQTT_TLS_CIPHERS"] = None

# mqtt = Mqtt(app)
# #####MQTT Endpoints################
# @mqtt.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     if rc==0:
#         result=WorkstationInfo.query.all()
#         print("[X-Routes] connected, OK Returned code=",rc)
#         #subscribe to tpoics
#         time.sleep(1)
#         mqtt.unsubscribe_all()
#         #mqtt.unsubscribe(BASE_TOPIC)
#         time.sleep(5)
#         for  res in result:
#             if res.id==10:
#                 mqtt.subscribe(f'T5_1-Data-Acquisition/Datasource ID: {res.DAQ_ExternalID} - MultiTopic/Measurements/cmd')
#                 print(f'[X-Routes] {res.id}')    
#     else:
#         print("[X-Routes] Bad connection Returned code=",rc)

# @mqtt.on_subscribe()
# def handle_subscribe(client, userdata, mid, granted_qos):
#     print('[X-Routes] Subscription id {} granted with qos {}.'
#           .format(mid, granted_qos))   

# # @mqtt.unsubscribe()
# # def handle_unsubscribe(client, userdata, mid):
# #     print('Unsubscribed from topic (id: {})'.format(mid))

# @mqtt.on_disconnect()
# def handle_disconnect():
#     mqtt.unsubscribe_all()
#     # mqtt.unsubscribe(BASE_TOPIC)
#     mqtt.unsubscribe_all()
#     print("[X-Routes] CLIENT DISCONNECTED")

# #handles commands from MQTT 
# ##command structure#####
# # {
# #     "external_ID":"104EM",
# #     "E10_Services": "start",
# #     "CNV":{"cmd":"start","CNV_section":"both"}
# # }
# @mqtt.on_message()
# def handle_mqtt_message(client, userdata, message):
#     try:
#         payload=json.loads(message.payload)
#         print(f"{type(payload)},'??',{payload}")
#         #db will handles
#         exID = int(payload.get("external_ID").split('4')[0])
#         result = WorkstationInfo.query.get(exID)
#         E10_url=result.EM_service_url
#         CNV_url = result.CNV_service_url
#         url_self = result.WorkCellIP

#         if payload.get("E10_Services") !=None and exID not in CONFIG.hav_no_EM:

#             cmd = payload.get("E10_Services")
#             res=threading.Thread(target=helper.invoke_EM_service,
#                                         args=(E10_url,cmd),
#                                         daemon=True).start()
#             print('[X-Routes] ',res)
#         else:
#             print(f'[X-Routes] Invalid Command!')

#         if payload.get("CNV").get("cmd") !=None:
#             cnv_cmd = payload.get("CNV").get("cmd")
#             cnv_section = payload.get("CNV").get("CNV_section").lower()
#             if exID in [7,1] and (cnv_section == 'bypass' or cnv_section == 'both'):
#                 print(f'[X-Routes] Invalid Command! ')
#             else:
                
#                 res= threading.Thread(target=helper.cnv_cmd,
#                                             args=((cnv_cmd,cnv_section,CNV_url,url_self)),
#                                             daemon=True).start()
#                 print('[X-Routes] ',res)
                
#     except ValueError:
#         print('[X-Routes] Decoding JSON has failed')
if __name__ == '__main__':

    # mqtt = MqqtClient(CONFIG.NAME,CONFIG.MQTT_CLIENT_ID)
    # mqtt.connect()
    
    #helper.createModels()    
    # Workstation Objects
    helper.Workstations()
    #time.sleep(10)
    app.run(host=CONFIG.appLocIP, port=CONFIG.appLocPort,use_reloader=False,debug=True)#,use_reloader=False,debug=True



