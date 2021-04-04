#import sqlite3
from flaskr.db import get_db
from flaskr.popyo.device import Device


class DeviceModel():

    @staticmethod
    def get_all():
        db = get_db()
        devices = db.execute(
            'SELECT p.id, tagGlobal, device_name, device_description'
            ' FROM device p'
            ' ORDER BY device_name DESC'
            ).fetchall()
        return devices
    
    @staticmethod
    def get_device_tag(tag):
        db = get_db()
        device_cursor = db.execute(
                'SELECT id, tagGlobal, device_name, device_description'
                ' FROM device'
                ' WHERE tagGlobal == ?',(tag,)
            ).fetchone()
        device = Device()
        device.set_cursor(device_cursor)
        return device