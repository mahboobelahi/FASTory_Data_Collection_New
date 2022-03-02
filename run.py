from FASToryEM import app
from FASToryEM import UtilityFunctions as helper
from FASToryEM import configurations as CONFIG
#from FASToryEM.msgBus import MqqtClient


if __name__ == '__main__':

    # mqtt = MqqtClient(CONFIG.NAME,CONFIG.MQTT_CLIENT_ID)
    # mqtt.connect()
    
    #helper.createModels()    
    # Workstation Objects
    helper.Workstations()
    #time.sleep(10)
    app.run(host=CONFIG.appLocIP, port=CONFIG.appLocPort,use_reloader=False,debug=True)#,use_reloader=False,debug=True



