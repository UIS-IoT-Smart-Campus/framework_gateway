#import sqlite3
#from flaskr.db import get_db
#from flaskr.popyo.device import Device

from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    device_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)

"""
class DeviceModel():

    @staticmethod
    def get_all():
        db = get_db()
        devices = db.execute(
            'SELECT p.id, tagGlobal, name, device_type, description'
            ' FROM device p'
            ' ORDER BY name DESC'
            ).fetchall()
        return devices
    
    @staticmethod
    def get_device_tag(tag):
        db = get_db()
        device_cursor = db.execute(
                'SELECT id, tagGlobal, name, device_type, description'
                ' FROM device'
                ' WHERE tagGlobal == ?',(tag,)
            ).fetchone()
        device = Device()
        device.set_cursor(device_cursor)
        return device
    
    @staticmethod
    def get_device_id(id):
        db = get_db()
        device_cursor = db.execute(
                'SELECT id, tagGlobal, name, device_type, description'
                ' FROM device'
                ' WHERE id == ?',(id,)
            ).fetchone()
        device = Device()
        device.set_cursor(device_cursor)
        return device
    

    @staticmethod
    def create_device(device):
        db = get_db()
        db.execute(
            'INSERT INTO device (tagGlobal, name, device_type, description)'
            ' VALUES (?, ?, ?, ?)',
            (device.tag, device.name, device.device_type, device.description)
        )
        db.commit()
    
    @staticmethod
    def update_device(device):
        db = get_db()
        #Update Device
        db.execute(
            'UPDATE device'
            ' SET name=?, device_type=?, description=? WHERE id = ?',
            (device.name, device.device_type, device.description, device.id)
        )
        db.commit()"""