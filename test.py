import requests,time

def req():
        requests.post("http://130.230.190.118:2002/simulate_measurements")
        time.sleep(.1)
        requests.post("http://130.230.190.118:2003/simulate_measurements")
        time.sleep(.1)
        requests.post("http://130.230.190.118:2004/simulate_measurements")
        time.sleep(.1)
        requests.post("http://130.230.190.118:2005/simulate_measurements")
        time.sleep(.1)
        requests.post("http://130.230.190.118:2006/simulate_measurements")
        time.sleep(.1)
        requests.post("http://130.230.190.118:2009/simulate_measurements")
        time.sleep(.1)
        requests.post("http://130.230.190.118:2010/simulate_measurements")
        time.sleep(.1)
        requests.post("http://130.230.190.118:2011/simulate_measurements")
        time.sleep(.1)
        requests.post("http://130.230.190.118:2012/simulate_measurements")

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

