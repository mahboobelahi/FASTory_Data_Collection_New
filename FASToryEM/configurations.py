#related to middleware app only

#globals for application
appLocIP = '0.0.0.0'#'192.168.100.100'
appLocPort = 2000#change it back to 2000
WorkStations = [1,2,3,4,5,6,7,8,9,10,11,12] #FASTory Line's workcells
wrkCellLocIP = '192.168.100.100'
wrkCellLocPort = 2000
hav_no_EM = [1,7,8] #  workcells that have no/out of order EM modules
energy_meters=[2,3,4,5,6,9,10,11,12]
FILE_NAME = 's_Measurements10.csv'

#DAQ URLs
ADMIN_URL = f'http://192.168.100.100:30025'
ASYNCH_URL =  f'http://192.168.100.100:30026'
SYNCH_URL = f'http://192.168.100.100:30027'
TOPIC_TYPE= 'multi'

##############################MQTT-Settings###########################################
BASE_TOPIC ='TAU/FASTory/cmd'
Conn_ALIVE = 5#60
NAME = 'FAST-LAB'
MQTT_CLIENT_ID = 'FASToryEMOrchestrator'
zMSG_PORT_VPN = 30204
zMSG_TLS_PORT = 8883#30206
zMQTT_BROKER_URL_VPN = '192.168.100.100'
zMQTT_BROKER_URL = 'msgbus-zdmp.platform.zdmp.eu'  # public ZDMP messageBus
#MQTT_BROKER_PORT = zMSG_PORT  # default port for non-tls connection
MQTT_USERNAME = 'tau'  # set the username here if you need authentication for the broker
MQTT_PASSWORD = 'ZDMP-tau2020!' # set the password here if the broker demands authentication
MQTT_KEEPALIVE = Conn_ALIVE  # set the time interval for sending a ping to the broker to 5 seconds
MQTT_TLS_ENABLED_VPN = False
MQTT_TLS_ENABLED = True  # set TLS to disabled for testing purposes
MQTT_TLS_CERTFILE = './files/ca_certificate.pem'#'files/ca_certificate.pem'
MQTT_REFRESH_TIME = 1.0  # refresh time in seconds
# ZDMP-Cumulocity IoT tenant credentials
#No more required in updated version of DAQ 
# domain = "https://zdmp-da.eu-latest.cumulocity.com"
# TenantID = "t59849255/mahboob.elahi@tuni.fi"
# passward = "mahboobelahi93"
