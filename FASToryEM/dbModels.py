from datetime import datetime
from tkinter import W
from FASToryEM import db

class WorkstationInfo(db.Model):
    __tablename__ = 'workstationinfo'
    id = db.Column(db.Integer, primary_key=True)
    WorkCellName = db.Column(db.String(255), unique=True, nullable=False)
    WorkCellID = db.Column(db.Integer, unique=True, default=0,nullable=False)
    DAQ_ExternalID = db.Column(db.String(10),nullable=False,unique=True)
    DAQ_SourceID = db.Column(db.Integer)
    HasZone4 = db.Column(db.Boolean)
    HasEM_Module = db.Column(db.Boolean)
    WorkCellIP = db.Column(db.String(255), unique=True, nullable=False)
    #WorkCellPort = db.Column(db.Integer)
    EM_service_url = db.Column(db.String(255), unique=True, nullable=False)
    CNV_service_url = db.Column(db.String(255), unique=True, nullable=False)
    EM_child= db.relationship('EnergyMeasurements',backref='WorkstationInfo',lazy=True)#,uselist=False
    def __repr__(self):
        return f"Workstation('{self.ID}', '{self.DAQ_ExternalID}')"


class EnergyMeasurements(db.Model):
    __tablename__ = 'energymeasurements'
    id = db.Column(db.Integer, primary_key=True)
    WorkCellID = db.Column(db.Integer)
    RmsVoltage = db.Column(db.Float)
    RmsCurrent = db.Column(db.Float)
    Power = db.Column('Power(W)',db.Float)
    Nominal_Power = db.Column(db.Float)
    ActiveZones = db.Column(db.String(15))
    Load = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    info = db.Column(db.Integer, db.ForeignKey('workstationinfo.id'),nullable=False)
    #DAQ_ExID = db.Column(db.String(10), db.ForeignKey('WorkstationInfo.DAQ_ExternalID'),nullable=False)
    def __repr__(self):
        return f"Workstation('{self.WorkCellID}', '{self.Power}', '{self.Load}', '{self.info}')"

# from FASToryEM.dbModels import WorkstationInfo as W
# from FASToryEM.dbModels import EnergyMeasurements as E
