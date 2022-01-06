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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)    
    description = db.Column(db.String(200))
    topics = db.relationship('Topic',secondary=device_topics, lazy='subquery',backref=db.backref('device',lazy=True))
    is_gateway = db.Column(db.Boolean,default=False)
    ipv4_address = db.Column(db.String(20))
    device_parent = db.Column(db.Integer, db.ForeignKey('device.id'))

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'id': self.id,
           'tag': self.tag,
           'name': self.name,
           'description': self.description,
           'device_parent': self.device_parent,
           'ipv4_address': self.ipv4_address,
           'is_gateway':self.is_gateway,
           'topics': self.serializable_topics,
           'properties': self.serializable_properties,
           'resources':self.serializable_resources
       }
    
    @property
    def serializable_topics(self):
        """
        Return topics relations serializable.
        """
        return [ topic.serializable for topic in self.topics]
    
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
        resources = Resource.query.filter_by(device_id=self.id)
        return [resource.serializable for resource in resources]

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
    tag = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    resource_type = db.Column(db.String(80), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    @property
    def serializable(self):
        return {
            'tag': self.tag,
            'name': self.name,
            'description': self.description,
            'type': self.resource_type
        }
    
    @property
    def serialize(self):
        return {
            'tag': self.tag,
            'name': self.name,
            'description': self.description,
            'type': self.resource_type,
            'device_id':self.device_id,
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
            'description': self.description
        }
