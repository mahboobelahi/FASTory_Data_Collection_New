import requests,time
import datetime 
from pprint import pprint as P


def get_token():

   
        
        ACCESS_URL = "https://keycloak-zdmp.platform.zdmp.eu/auth/realms/testcompany/protocol/openid-connect/token" 
        headers = { 'accept': "application/json", 'content-type': "application/x-www-form-urlencoded" }
        payload = "grant_type=password&client_id=ZDMP_API_MGMT_CLIENT&username=zdmp_api_mgmt_test_user&password=ZDMP2020!"
        response = requests.post(ACCESS_URL, data=payload, headers=headers)
        j = response.json()
        P(j)




# from FASToryEM.dbModels import WorkstationInfo as W
# from FASToryEM.dbModels import EnergyMeasurements as E
# def sqlTest():
#     emChild=W.EM_child #filter_by(WorkCellID=self.ID).order_by(EnergyMeasurements.id.desc())[:5]
#     print(emChild)
#     e=E.query.first()
#     x=E.query.filter(e.WorkstationInfo.DAQ_ExternalID=='94EM').order_by(E.id.desc())[:5]
#     print(e.WorkstationInfo.DAQ_ExternalID)
# if __name__ == '__main__':

#     sqlTest()


# def zone():

#     load = 0
#     ActiveZone = ''
#     for i in ['1','1','-1','-1','-1']:
        
#         if i =='-1':
#             ActiveZone =ActiveZone+'0'
#         else:
#             ActiveZone =ActiveZone+'1'
#             load =load+1
            
#     return (load,ActiveZone)
# print(zone())

#make query statement
# query = db.session.query(EnergyMeasurements.Power).filter_by(WorkCellID=self.ID).statement
# #print('[X]', query)
# df = pd.read_sql_query(query, con=db.engine)
# #plt.ylim([df["Power(W)"].min(),df["Power(W)"].max()])
# #plt.yticks(np.arange(df["Power(W)"].min(),df["Power(W)"].max(),2))
# #plt.yticks(np.arange(0,500,20))
# # plt.xlim([0,df.size])
# # plt.xticks(np.arange(0,df.size,50))
# # sns.set_theme(style="darkgrid")
# sns.lineplot(x = np.arange(0,df.size,1), y = "Power(W)", data=df)
# plt.show()

# from netifaces import interfaces, ifaddresses, AF_INET
# for ifaceName in interfaces():
#     addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
#     print ('%s: %s' % (ifaceName, ', '.join(addresses)))

from FASToryEM.UtilityFunctions import predict
import tensorflow  as tf
import numpy as np

def predict(power,load):
    model = tf.keras.models.load_model('M_iter3_1.h5', compile=True)
    features = np.array(np.append([power],[load]), ndmin=2)
    pred = np.argmax(model.predict(features), axis=1) 
    print(f"[X-UTF] {pred}")
    return pred    

predict(0.26 ,0.13)

# <app color="#8f0004" lang="English" appname="APPNAME" author="AUTHOR_NAME" email="zdmp@zdmp.com" version="1.0" app_id="APP_A67B37"> 
#   <page icon="keyboard" text="LOGIN" page_id="PAGE_E1B86A">
#     <separator style_nr="1" id="8950F3"/>
#     <login href="PAGE_51F1AA" process_id="login" id="E9ED0B"/>
#   </page>	
#   <page icon="home" text="HOME" page_id="PAGE_51F1AA">
#     <panel text="ENERGY_CONSUMPTION_WELCOME" id="A7E2D9"/>
#   </page> 
#   <page icon="list-alt" text="MSGBUS_ACCESS" page_id="PAGE_00AB84">
#     <separator style_nr="1" id="A356AA"/>
#     <header5 text="LAST_MESSAGE" id="942AD1"/>
#     <last_message id="A5DCEA"/>
#     <separator style_nr="1" id="499B70"/>
#     <header5 text="SUBSCRIBE_TOPIC" id="1FF84F"/>
#     <subscribe_to_a_topic id="730FC1"/>
#     <separator style_nr="1" id="6487E1"/>
#     <header5 text="PUBLISH_TOPIC" id="EA3856"/>
#     <publish_message id="CFCC97"/>
#     <separator style_nr="1" id="12D2E8"/>
#     <header5 text="UNSUBSCRIBE_TOPIC" id="83DAE9"/>
#     <unsubscribe_a_topic id="5CC2CF"/>
#   </page> 
#   <page icon="chart-bar" text="REALTIME_DATA" page_id="PAGE_5D3581">
#     <separator style_nr="1" id="7D92E8"/>
#     <line-chart datasource="http://localhost/z_studio/sample_data/line-chart.json" id="9DD4E7"/>
#     <separator style_nr="1" id="A90A69"/>
#     <line-chart datasource="http://localhost/z_studio/sample_data/line-chart.json" id="943281"/>
#     <separator style_nr="1" id="836C63"/>
#     <line-chart datasource="http://localhost/z_studio/sample_data/line-chart.json" id="6C8F09"/>   
#     <bar-chart direction="vertical" datasource="http://localhost/z_studio/sample_data/bar-chart.json" id="C8F07E"/>
#   </page>  
#   <page icon="bell" text="ALERTS" page_id="PAGE_A073FF">
#     <separator style_nr="1" id="44E9B4"/>
#     <header5 text="CREATE_PROCUCT_API" id="EF3666"/>
#     <create_kpi id="507F7F"/>
#     <separator style_nr="1" id="39DBFA"/>
#     <header5 text="CREATE_USER_ALERT" id="A44215"/>
#     <create_alert id="B9D4C6"/>
#   </page>
# </app> 
















# @app.route('/home', methods=['GET','POST'])
# def home():
#     if request.method == 'GET':
#         return '<h2>Hello from  Workstation_' + str(self.ID) + '! Workstation_request.url :=  ' + request.url+'<h2>'
#     else:
#             if request.json.get("Msg"):
#                 print(f'{self.get_ID()} {request.json.get("Msg")}')
#             elif request.json.get("Msg-id") == "Error":
#                 print('Command Status at Workstation {ID} is: Command \' {command} \': is not recognized.'
#                       .format( ID=request.json.get('CellID'), command=request.json.get("cmd_status")
#                                ))
#                 print('Available Commands are:\n 1.{main}\t\t2.{bypass}\t3.{both}'.format(main='main',bypass='bypass',both='both'))
#             else:
#                     print('CNVs Status at Workstation {ID} are: Main: {main}  , Bypass:{bypass}'
#                           .format( ID=request.json.get('CellID'), main=request.json.get("mt_main Status"),
#                                    bypass=request.json.get("mt_by Status")
#                                    ))
#     return ''

