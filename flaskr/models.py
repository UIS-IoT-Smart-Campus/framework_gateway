#import sqlite3
#from flaskr.db import get_db
#from flaskr.popyo.device import Device

from app import db
from datetime import datetime


#Helper tables for many to many relationship
device_topics = db.Table('device_topics',
    db.Column('device_id', db.Integer, db.ForeignKey('device.id'), primary_key=True),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'), primary_key=True),
    db.Column('frequency',db.Integer),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    device_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    topics = db.relationship('Topic',secondary=device_topics, lazy='subquery',backref=db.backref('device',lazy=True))

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(80), unique=True, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active_devices = db.Column(db.Integer,default=0)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'),nullable=False)




