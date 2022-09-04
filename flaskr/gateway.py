from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from requests import patch

from werkzeug.exceptions import abort

from auth import login_required
from models import Application, Device, Property, Resource
from persistence import Persistence
from app import db

from flask import jsonify,request
import json
from tinydb import TinyDB, Query

import configparser
import shutil
import os
import requests as rq
import selfconfig as sc
from datetime import datetime
from redisTool import RedisQueue
from datetime import timezone

bp = Blueprint('gateway', __name__, url_prefix='/gateway')


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

def get_self_description(settings):
    this_gateway = {}
    device = Device.query.filter_by(id=1).first()
    return device.get_gateway_serialize

def disable_standalone():
    #Update internal Settings
    settings = {}
    settings['standalone'] = 'false'
    settings = sc.set_config_values(settings)

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
    id = str(settings["backendgatewayid"])
    backend_ip = settings["backendurl"]
    backend_port = settings["backendport"]
    api_url = "http://"+backend_ip+":"+backend_port+"/device/"+id
    response = rq.get(api_url)
    #Create self-representation
    create_json_respresentation(response.json(),device_parent=0)

def set_representation(settings):
    backend_url = settings["backendurl"]
    backend_port = settings["backendport"]
    api_url = "http://"+backend_url+":"+str(backend_port)+"/device"
    this_gateway_obj = get_self_description(settings)
    response = json.loads(rq.post(api_url,json=this_gateway_obj).text)
    #Actualizar configuración interna
    settings["backendgatewayid"] = response["id"]
    sc.set_config_values(settings)
    #Actualizar ID Globales.
    this_gateway = Device.query.filter_by(id=1).first()
    this_gateway.backend_ip = response["id"]
    db.session.add(this_gateway)
    db.session.commit()
    #Actualizar id globales propiedades
    backend_properties = response["properties"]
    properties = Property.query.filter_by(device_id=1)
    for prop in properties:
        for b_prop in backend_properties:
            if prop.name == b_prop['name']:
                prop.global_id = b_prop['id']
                db.session.add(prop)
                db.session.commit()
        




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
        elif request.form.get('getrepresentation',False):
            settings = sc.get_config_values()
            synchronized_gateway(settings)
            return render_template('gateway/settings.html',settings=settings)
        elif request.form.get('setrepresentation',False):
            settings = sc.get_config_values()
            set_representation(settings)
            return render_template('gateway/settings.html',settings=settings)
        elif request.form.get('sdaInit',False):
            q = RedisQueue('register')
            self_device = {"type":"device"}
            self_device["queue"] = "create"
            this_device = Device.query.filter_by(id=1).first()
            self_device["content"] = this_device.light_serialize
            q.put(json.dumps(self_device))
            properties = Property.query.filter_by(parent_id=1,prop_type="DEVICE")            
            for proper in properties:
                prop = {"type":"property"}
                prop["queue"] = "create"
                prop["content"] = proper.complete_serializable
                q.put(json.dumps(prop))
            flash("SDA Initialized")
            settings = sc.get_config_values()
            return render_template('gateway/settings.html',settings=settings)
            
    else:
        settings = sc.get_config_values()
        return render_template('gateway/settings.html',settings=settings)



@bp.route('/settings/update', methods=('GET', 'POST'))
#@login_required
def settings_update():
    if request.method == 'POST':
        #Get settings form
        settings = {}
        settings['standalone'] = request.form.get('standalone','false')
        settings['backendurl'] = request.form.get('backendurl','127.0.0.1')
        settings['backendport'] = request.form.get('backendport','8080')
        settings['brokerbackendurl'] = request.form.get('brokerbackendurl','127.0.0.1')
        settings['brokerbackendport'] = request.form.get('brokerbackendport','1883')
        settings['brokerbackendtopic'] = request.form.get('brokerbackendtopic','devices/messages/')
        settings['mqttclient'] = request.form.get('mqttclient','GT001')
        settings['backendgatewayid'] = request.form.get('backendgatewayid','0')
        settings = sc.set_config_values(settings)
        return redirect(url_for('gateway.settings'))
    else:
        settings = sc.get_config_values()
        return render_template('gateway/update-settings.html',settings=settings)


"""------------------------------------------------------------------
Rest API Methods
-----------------------------------------------------------------"""


#Get representation
@bp.route('/api/representation/', methods=["GET"])
def get_self_representation():
    self_representation = {}
    device = Device.query.filter_by(id=1).first()
    self_representation["device"] = device.serialize
    resources = Resource.query.all()
    self_representation["resources"] = []
    for resource in resources:
        self_representation["resources"].append(resource.serialize)
    applications = Application.query.all()
    self_representation["apps"] = []
    for app in applications:
        self_representation["apps"].append(app.serialize)
    
    
    return jsonify(self_representation)
