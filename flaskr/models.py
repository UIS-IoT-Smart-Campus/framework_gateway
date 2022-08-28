#import sqlite3
#from flaskr.db import get_db
#from flaskr.popyo.device import Device

from app import db
from datetime import datetime


#Helper tables for many to many relationship
device_topics = db.Table('device_topics',
    db.Column('device_id', db.Integer, db.ForeignKey('device.id'), primary_key=True),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'), primary_key=True),
)

device_resource = db.Table('device_resource',
    db.Column('device_id', db.Integer, db.ForeignKey('device.id'), primary_key=True),
    db.Column('resource_id', db.Integer, db.ForeignKey('resource.id'), primary_key=True),
)

device_app = db.Table('device_app',
    db.Column('device_id', db.Integer, db.ForeignKey('device.id'), primary_key=True),
    db.Column('app_id', db.Integer, db.ForeignKey('application.id'), primary_key=True),
    
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    global_id = db.Column(db.Integer)
    name = db.Column(db.String(80), nullable=False)    
    description = db.Column(db.String(200))
    topics = db.relationship('Topic',secondary=device_topics, lazy='subquery',backref=db.backref('device',lazy=True))
    applications = db.relationship('Application',secondary=device_app, lazy='subquery',back_populates="devices")
    resources = db.relationship('Resource',secondary=device_resource, lazy='subquery',back_populates="devices")
    is_gateway = db.Column(db.Boolean,default=False)
    create_at = db.Column(db.Date)
    update_at = db.Column(db.Date)
    device_parent = db.Column(db.Integer, db.ForeignKey('device.id'))

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id': self.id,
           'global_id': self.global_id,
           'name': self.name,
           'description': self.description,
           'device_parent': self.device_parent,
           'is_gateway': self.is_gateway,
           'applications': self.serializable_apps,
           'properties': self.serializable_properties,
           'resources':self.serializable_resources,
           'devices':self.serializable_devices
       }
    
    @property
    def get_gateway_serialize(self):
       """Return object data in easily serializable format"""
       return {
           'name': self.name,
           'description': self.description,
           'gateway':self.is_gateway,
           'properties':self.serializable_properties,
           'resources':self.serializable_resources,
           'devices':self.serializable_devices
       }
    
    @property
    def serializable_apps(self):
        """
        Return the resources of the device.
        """
        return [app.serializable for app in self.applications]
        
    @property
    def serializable_properties(self):
        """
        Return the properties of the device.
        """
        properties = Property.query.filter_by(device_id=self.id)
        return [properti.serializable for properti in properties]
    
    @property
    def serializable_resources(self):
        """
        Return the resources of the device.
        """
        return [resource.serializable for resource in self.resources]
    
    @property
    def serializable_devices(self):
        """
        Return the devices of the device.
        """
        devices = Device.query.filter_by(device_parent=self.id)
        return [device.serialize for device in devices]

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    global_id = db.Column(db.Integer)
    name = db.Column(db.String(80), unique=True, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    devices = db.relationship('Device',secondary=device_app, lazy='subquery',back_populates="applications")

    @property
    def serializable(self):
        return {
            'global_id': self.global_id,
            'name': self.name
        }

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(80), unique=True, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active_devices = db.Column(db.Integer,default=0)

    @property
    def serializable(self):
        return {
            'topic': self.topic,
            'last_update': self.last_update,
            'active_devices': self.active_devices
        }

class Resource(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    global_id = db.Column(db.Integer)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    resource_type = db.Column(db.String(80), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    devices = db.relationship('Device',secondary=device_resource, lazy='subquery',back_populates="resources")

    @property
    def serializable(self):
        return {
            'global_id': self.global_id,
            'name': self.name,
            'description': self.description,
            'type': self.resource_type,
            'create':self.create_at,
            'properties':self.serializable_properties
        }
    
    @property
    def serialize(self):
        return {
            'id':self.id,
            'name': self.name,
            'description': self.description,
            'type': self.resource_type,
            'properties':self.serializable_properties
        }
    
    @property
    def serializable_properties(self):
        """
        Return the properties of the device.
        """
        properties = Property.query.filter_by(resource_id=self.id)
        return [properti.serializable for properti in properties]


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))

    @property
    def serializable(self):
        return {
            'name': self.name,
            'value': self.value,
            'description': self.description,
        }
    
    @property
    def serialize(self):
        return {
            'id':self.id,
            'name': self.name,
            'value': self.value,
            'description': self.description
        }
