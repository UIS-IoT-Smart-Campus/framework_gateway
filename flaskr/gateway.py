from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from requests import patch

from werkzeug.exceptions import abort

from auth import login_required
from models import Device, Property, Resource,Category
from persistence import Persistence
from app import db

from flask import jsonify,request
import json
from tinydb import TinyDB, Query

import configparser
import shutil
import os
import requests as rq
from datetime import datetime
from datetime import timezone

bp = Blueprint('gateway', __name__, url_prefix='/gateway')

def get_config_values() -> dict:
    settings = {}
    config = configparser.ConfigParser()
    config.readfp(open('init.cfg'))
    settings["standalone"] = config.getboolean('DEFAULT','standalone')
    settings["backendip"] = config.get('DEFAULT','backendip')
    settings["backendport"] = config.get('DEFAULT','backendport')
    settings["brokerip"] = config.get('DEFAULT','brokerip')
    settings["brokerport"] = config.get('DEFAULT','brokerport')
    settings["backend_topic"] = config.get('DEFAULT','backend_topic')
    settings["MqttClient"] = config.get('DEFAULT','MqttClient')
    settings["synchronized"] = config.get('DEFAULT','synchronized')
    settings["gatewayId"] = config.getint('DEFAULT','gatewayId')
    return settings

def set_config_values(settings):
    last_settings = get_config_values()
    if 'standalone' in settings: last_settings['standalone'] = settings['standalone']
    if 'backendip' in settings: last_settings['backendip'] = settings['backendip']
    if 'backendport' in settings: last_settings['backendport'] = settings['backendport']
    if 'brokerip' in settings: last_settings['brokerip'] = settings['brokerip']
    if 'brokerport' in settings: last_settings['brokerport'] = settings['brokerport']
    if 'backend_topic' in settings: last_settings['backend_topic'] = settings['backend_topic']
    if 'MqttClient' in settings: last_settings['MqttClient'] = settings['MqttClient']
    if 'synchronized' in settings: last_settings['synchronized'] = settings['synchronized']
    if 'gatewayId' in settings: last_settings['gatewayId'] = settings['gatewayId']
    #Save Settings
    config = configparser.ConfigParser()
    config['DEFAULT'] = last_settings
    with open('init.cfg', 'w') as configfile:
        config.write(configfile)
    return last_settings

def delete_info():
    devices = db.session.query(Device).all()
    #delete folders
    for device in devices:
        path = "device_data/"+str(device.id)
        try:
            shutil.rmtree(path)
        except Exception as e:
            print("Is not posible delete folder"+str(device.id))
    
    #Delete tables
    db.session.query(Property).delete()
    db.session.commit()
    db.session.query(Resource).delete()
    db.session.commit()
    db.session.query(Device).delete()
    db.session.commit()
    db.session.query(Category).delete()
    db.session.commit()


def disable_standalone():
    #Update internal Settings
    delete_info()
    settings = {}
    settings['standalone'] = 'false'
    settings = set_config_values(settings)

def create_json_respresentation(json_response,device_parent):    
    #Create Gateway Device
    device = Device(backendid=json_response["id"],name=json_response["name"],description=json_response["description"],is_gateway=json_response["gateway"],local_device=False)
    device.create_at = datetime.fromisoformat(json_response["created_at"])
    device.update_at = datetime.fromisoformat(json_response["update_at"])
    if device_parent!=0:
        device.device_parent = device_parent
    db.session.add(device)
    db.session.commit()

    #Create Folder
    directory = "device_data/"+str(device.id)
    if not os.path.exists(directory):
        os.makedirs(directory)

    #Add properties
    if len(json_response["properties"]) != 0:
        for json_property in json_response["properties"]:
            d_property = Property(backendid=json_property["id"],name=json_property["name"], value=json_property["value"], description=json_property["description"], device_id=device.id)
            db.session.add(d_property)
            db.session.commit()
    
    #Add resource
    if len(json_response["resources"]) != 0:
        for json_resource in json_response["resources"]:
            d_resource = Resource(backendid = json_resource["id"],name=json_resource["name"], description=json_resource["description"], resource_type=json_resource["type"],device_id=device.id)
            db.session.add(d_resource)
            db.session.commit()

            if len(json_resource["properties"]) != 0:
                for json_property in json_resource["properties"]:
                    r_property = Property(backendid=json_property["id"],name=json_property["name"], value=json_property["value"], description=json_property["description"], resource_id=d_resource.id)
                    db.session.add(r_property)
                    db.session.commit()


    #Is the gateway
    if device_parent==0:
        for device_son in json_response["devices"]:
            create_json_respresentation(device_son,device.id)


def synchronized_gateway(settings):
    id = str(settings["gatewayId"])
    backend_ip = settings["backendip"]
    backend_port = settings["backendport"]
    api_url = "http://"+backend_ip+":"+backend_port+"/device/"+id
    response = rq.get(api_url)
    #Create self-representation
    create_json_respresentation(response.json(),device_parent=0)





@bp.route('/get_records', methods=('GET', 'POST'))
#@login_required
def get_records():
    data = Persistence().get_gateway_records()
    return jsonify(data)

@bp.route('/settings', methods=('GET', 'POST'))
#@login_required
def settings():
    if request.method == 'POST':
        if request.form.get('disablestandalone',False):
            disable_standalone()
            return render_template('index.html')
        elif request.form.get('synchronized',False):
            print("sincronizando")
            settings = get_config_values()
            synchronized_gateway(settings)
            return render_template('gateway/settings.html',settings=settings)
        else:
            #os.system('sudo reboot now')
            print("reboot")
            return render_template('index.html')
            
    else:
        settings = get_config_values()
        return render_template('gateway/settings.html',settings=settings)



@bp.route('/settings/update', methods=('GET', 'POST'))
#@login_required
def settings_update():
    if request.method == 'POST':
        #Get settings form
        settings = {}
        settings['standalone'] = request.form.get('standalone','false')
        settings['backendIp'] = request.form.get('backendip','127.0.0.1')
        settings['backendPort'] = request.form.get('backendport','8080')
        settings['brokerIp'] = request.form.get('brokerip','127.0.0.1')
        settings['brokerPort'] = request.form.get('brokerport','1883')
        settings['backend_topic'] = request.form.get('backendtopic','devices/messages/')
        settings['MqttClient'] = request.form.get('mqttclientname','GT001')
        settings = set_config_values(settings)
        return redirect(url_for('gateway.settings'))
    else:
        settings = get_config_values()
        return render_template('gateway/update-settings.html',settings=settings)