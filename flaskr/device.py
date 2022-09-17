from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from sqlalchemy import update

from werkzeug.exceptions import abort

from auth import login_required
from models import Device,Property,Resource
from datetime import date

from flask import request,Response,make_response
from flask import jsonify
import json
from tinydb import TinyDB
from app import db
from redisTool import RedisQueue

import os
import shutil
import selfconfig as sc

bp = Blueprint('device', __name__, url_prefix='/device')


#Delete Device
def delete_device_method(device):
    devices = Device.query.filter_by(device_parent=device.id)
    for device_s in devices:
        delete_device_method(device_s)
    properties = Property.query.filter_by(parent_id=device.id,prop_type="DEVICE")
    for property in properties:
        db.session.delete(property)
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_prop = {"type":"property","queue":"delete"}
        self_prop["content"] = property.complete_serializable
        q.put(json.dumps(self_prop))
        #-------------END SDA CODE--------------------#
    dirc= 'device_data/'+str(device.id)+'/'
    db.session.delete(device)
    db.session.commit()
    #-------------SDA CODE--------------------#
    q = RedisQueue('register')
    self_device = {"type":"device","queue":"delete"}
    self_device["content"] = device.light_serialize
    q.put(json.dumps(self_device))
    #-------------END SDA CODE--------------------#
    if os.path.isdir(dirc):
        shutil.rmtree(dirc)

#Index
@bp.route('/')
@login_required
def device_index():
    """ Devices Index Section"""
    devices = Device.query.filter(Device.device_parent==1)
    settings = sc.get_config_values()
    return render_template('device/device_index.html', devices=devices,settings=settings)

#Device Detail View
@bp.route('/<int:id>/view', methods=['GET','POST'])
@login_required
def device_view(id):
    """ Devices View Section"""
    device = Device.query.filter_by(id=id).first()
    if request.method == 'POST':
        resource_id = request.form.get('resource_id',None)
        if resource_id is not None:
            resource = Resource.query.filter_by(id=resource_id).first()
            if resource is not None:
                device.resources.append(resource)
                db.session.add(device)
                db.session.commit()
                #-------------SDA CODE--------------------#
                q = RedisQueue('register')
                self_device = {"type":"device_resource","queue":"create"}
                self_device["content"] = {"device_id":device.global_id,"resource_id":resource.global_id}
                q.put(json.dumps(self_device))
                #-------------END SDA CODE----------------#
                return redirect(url_for('device.device_view',id = device.id))
    else:
        properties = Property.query.filter_by(parent_id=device.id,prop_type="DEVICE")
        offspring_devices = Device.query.filter_by(device_parent=device.id)
        if device.id:
            dbj = TinyDB('device_data/'+str(device.id)+'/'+str(device.id)+'.json')
            tables = dbj.tables()
            data = {}
            for table in tables:
                data[table] = dbj.table(str(table)).all()

        return render_template('device/device_detail.html', device=device,properties=properties,offspring_devices=offspring_devices,tables=tables,data=data)


#Create Device
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    devices = db.session.query(Device).all()

    """View for create devices"""
    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        is_gateway = request.form.get('is_gateway',False)
        device_parent = request.form['device_parent']
        create_at = update_at = date.today()
        error = None

        if is_gateway:
            is_gateway = True

        if not name:
            error = 'No mandatory property is set.'     

        if error is not None:
            flash(error)
        else:            
            try:
                if len(devices)!=0:
                    count_dev = devices[len(devices)-1].id+1
                else:
                    count_dev = 1
                directory = "device_data/"+str(count_dev)
                if not os.path.exists(directory):
                    os.makedirs(directory)             
                if device_parent != "null":
                    device = Device(name=name, description=description,global_id=count_dev, is_gateway=is_gateway, create_at = create_at, update_at=update_at, device_parent=device_parent)
                else:
                    device = Device(name=name, description=description,global_id=count_dev, is_gateway=is_gateway, create_at = create_at, update_at=update_at, device_parent=1)
                db.session.add(device)
                db.session.commit()
                #-------------SDA CODE--------------------#
                q = RedisQueue('register')
                self_device = {"type":"device","queue":"create"}
                self_device["content"] = device.light_serialize
                q.put(json.dumps(self_device))
                #-------------END SDA CODE--------------------#
                return redirect(url_for('device.device_index'))

            except OSError as e:
                flash("Creation of the directory failed")
            except Exception as e:
                print(e)
                flash("DB Creation Failed")

    return render_template('device/create.html',devices=devices)

#Edit Device
@bp.route('/edit_device/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_device(id):
    device = Device.query.filter_by(id=id).first()
    if device is not None:

        """View for create devices"""
        if request.method == 'POST':

            name = request.form['name']
            is_gateway = request.form.get('is_gateway',False)
            description = request.form['description']
            update_at = date.today()
            
            if is_gateway:
                is_gateway = True            
            try:
                device.name = name
                device.is_gateway = is_gateway
                device.description = description
                device.update_at = update_at
                db.session.add(device)
                db.session.commit()
                #-------------SDA CODE--------------------#
                q = RedisQueue('register')
                self_device = {"type":"device","queue":"update"}
                self_device["content"] = device.light_serialize
                q.put(json.dumps(self_device))
                #-------------END SDA CODE----------------#
                return redirect(url_for('device.device_view',id = device.id))

            except Exception as e:
                print(e)
                flash("DB Update Failed")
    else:
        flash("Device Not Found")

    return render_template('device/edit.html',device=device)


#Delete Device
@bp.route('/delete_device/<int:id>', methods=['GET','POST'])
@login_required
def delete_device(id):
    device = Device.query.filter_by(id=id).first()
    if device is not None:
        if request.method == 'POST':
            try:                
                delete_device_method(device)                
                flash("The device was removed")
                return redirect(url_for('device.device_index'))

            except Exception as e:
                print(e)
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Device Not Found")

    return render_template('device/delete.html',device=device)



#Create Property Device
@bp.route('/add_property/<int:id>', methods=['GET', 'POST'])
@login_required
def create_property(id):
    device = Device.query.filter_by(id=id).first()
    """View for create properties"""
    if request.method == 'POST':

        p_name = request.form['name']
        p_value = request.form['value']
        prop_type = "DEVICE"
        parent_id = device.id
        error = None

        if not p_name or not p_value:
            error = 'No mandatory property is set.'

        if error is not None:
            flash(error)
        else:            
            try:
                property_d = Property(name=p_name, value=p_value, prop_type=prop_type,parent_id=parent_id)
                db.session.add(property_d)
                db.session.commit()
                #-------------SDA CODE--------------------#
                q = RedisQueue('register')
                self_prop = {"type":"property","queue":"create"}
                self_prop["content"] = property_d.complete_serializable
                q.put(json.dumps(self_prop))
                #-------------END SDA CODE----------------#
                return redirect(url_for('device.device_view',id=device.id))

            except Exception as e:
                print(e)
                flash("DB Creation Failed")

    return render_template('device/create_property.html',device=device)


#Delete Property
@bp.route('/delete_property/<int:id>', methods=['GET','POST'])
@login_required
def delete_property(id):
    property_d = Property.query.filter_by(id=id).first()
    if property_d is not None:
        if request.method == 'POST':
            device_id = property_d.parent_id
            try:
                #Delete the database register
                db.session.delete(property_d)
                db.session.commit()
                #-------------SDA CODE--------------------#
                q = RedisQueue('register')
                self_prop = {"type":"property","queue":"delete"}
                self_prop["content"] = property_d.complete_serializable
                q.put(json.dumps(self_prop))
                #-------------END SDA CODE----------------#
                flash("The property was removed")
                return redirect(url_for('device.device_view',id=device_id))

            except Exception as e:
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Device Not Found")

    return render_template('device/delete_property.html',property=property_d)

"""------------------------------------------------------------------
Rest API Methods
-----------------------------------------------------------------"""

#########################
# DEVICES API REST #####
########################

#Get all devices except the gateway
@bp.route('/api/', methods=["GET"])
def get_devices_api():
    return jsonify(devices=[i.serialize for i in Device.query.filter(Device.id != 1).all()])

#Get a single device
@bp.route('/api/<int:id>/', methods=["GET"])
def get_device_api(id):
    device = Device.query.filter_by(id=id).first()
    return jsonify(device.serialize)

#Create a Device
@bp.route('/create/api/', methods=["POST"])
def add_device_api():
    body = request.get_json()
    if 'name' not in body:
        error = {"Error":"No mandatory property is set."}
        return make_response(jsonify(error),400)
    else:        
        name = body['name']    
        description = body.get('description',None)
        global_id = body.get('global_id',None)
        if global_id == None:
            device_id = db.session.query(Device).all()[-1]
            global_id = device_id.id+1
        device_parent = body.get('device_parent',None)
        is_gateway = body.get('is_gateway',None)
        create_at = update_at = date.today()
        
        devices = Device.query.filter_by(name=name).first()
        if devices is not None:
            error = {"Error":"The device with this name is already exist."}
            return make_response(jsonify(error),400)
        if device_parent is not None:
            device = Device.query.filter_by(global_id=device_parent)
            if device is None:
                error = {"Error":"The parent device ID not exist."}
                return make_response(jsonify(error),400)
        else:
            device_parent=1        

        device = Device(name=name,description=description,global_id=global_id,is_gateway=is_gateway,device_parent=device_parent,create_at=create_at,update_at=update_at)
        db.session.add(device)
        db.session.commit()
        #-----------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"device","queue":"create"}
        self_device["content"] = device.light_serialize
        q.put(json.dumps(self_device))
        #-------------END SDA CODE--------------------#

        #create directory for data
        try:
            directory = "device_data/"+str(device.id)
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError as e:
            flash("Creation of the directory failed")
        
        return jsonify(device.serialize)

#Update device
@bp.route('/update/api/<int:global_id>/', methods=["PUT"])
def update_device_api(global_id):
    device = Device.query.filter_by(global_id=global_id).first()
    
    if device is not None:
        body = request.get_json()

        #Get properties from request
        name = body.get('name',None)
        description = body.get('description',None)
        device_parent = body.get('device_parent',None)
        is_gateway = body.get('is_gateway',None)
        global_id = body.get('global_id',None)


        #Set properties to model
        if name:
            device.name = name
        if description:
            device.description = description
        if device_parent:
            device.device_parent = device_parent
        if is_gateway:
            device.is_gateway = is_gateway   
        if global_id:
            device.global_id = global_id  
        db.session.add(device)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"device","queue":"update"}
        self_device["content"] = device.light_serialize
        q.put(json.dumps(self_device))
        #-------------END SDA CODE----------------#
        return jsonify(device.light_serialize)

    else:
        error = {"Error":"The device doesn't exist."}
        return make_response(jsonify(error),400)
    

    
#Delete device
@bp.route('/delete/api/<int:global_id>/', methods=["DELETE"])
def delete_device_api(global_id):
    device = Device.query.filter_by(global_id=global_id).first()
    try:
        delete_device_method(device)
        return make_response(jsonify({"Delete":"The device was remove"}),200)

    except Exception as e:
        print(e)
        error = {"Error":"It's not possible to delete the device"}
        return make_response(jsonify(error),400)


#Add Resource device
@bp.route('/resource/api/<device_id>/', methods=["POST"])
def set_device_resource(device_id):
    device = Device.query.filter_by(id=device_id).first()
    body = request.get_json()
    resource_id = body.get('resource_id',None)
    resource = Resource.query.filter_by(id=resource_id).first()
    if resource is not None:
        device.resources.append(resource)
        db.session.add(device)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"device_resource","queue":"create"}
        self_device["content"] = {"device_id":device.global_id,"resource_id":resource.global_id}
        q.put(json.dumps(self_device))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)

#Add Resource device
@bp.route('/resource/api/global/<global_device_id>/', methods=["POST"])
def set_global_device_resource(global_device_id):
    device = Device.query.filter_by(global_id=global_device_id).first()
    body = request.get_json()
    resource_id = body.get('resource_id',None)
    resource = Resource.query.filter_by(global_id=resource_id).first()
    if resource is not None:
        device.resources.append(resource)
        db.session.add(device)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"device_resource","queue":"create"}
        self_device["content"] = {"device_id":device.global_id,"resource_id":resource.global_id}
        q.put(json.dumps(self_device))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)



#Remove Resource device
@bp.route('/resource/api/delete/<int:device_id>/', methods=["POST"])
def delete_device_resource(device_id):
    device = Device.query.filter_by(id=device_id).first()
    body = request.get_json()
    resource_id = body.get('resource_id',None)
    resource = Resource.query.filter_by(id=resource_id).first()
    if resource is not None:
        device.resources.remove(resource)
        db.session.add(device)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"device_resource","queue":"delete"}
        self_device["content"] = {"device_id":device.global_id,"resource_id":resource.global_id}
        q.put(json.dumps(self_device))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)

#Remove Resource device
@bp.route('/resource/api/global/delete/<int:global_id>/', methods=["POST"])
def delete_global_device_resource(global_id):
    device = Device.query.filter_by(global_id=global_id).first()
    body = request.get_json()
    resource_id = body.get('resource_id',None)
    resource = Resource.query.filter_by(global_id=resource_id).first()
    if resource is not None:
        device.resources.remove(resource)
        db.session.add(device)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"device_resource","queue":"delete"}
        self_device["content"] = {"device_id":device.global_id,"resource_id":resource.global_id}
        q.put(json.dumps(self_device))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)

@bp.route('/get_data', methods=['GET'])
#@login_required
def get_data():
    device_id = request.args.get('device_id',None)
    table = request.args.get('table',None)
    if device_id and table:
        dbn = TinyDB('device_data/'+str(device_id)+'/'+str(device_id)+'.json')
        #data = json.load(db.all())
        table = dbn.table(str(table))
        data = table.all()
    else:
        data = {}
    return Response( json.dumps(data) ,mimetype="application/json", status=200)



"""----------------------------------------------------------------------------------------------
#########################
# REMOTE ADMIN PROPERTIES API REST #####
########################
--------------------------------------------------------------------------------------------"""
#Create Device Property
@bp.route('/property/api/<int:device_id>/', methods=["POST"])
def create_device_property(device_id):

    device = Device.query.filter_by(id=device_id).first()
    if not device:
        error = {"Error":"No device exist."}
        return make_response(jsonify(error),400)
      
    body = request.get_json()

    #Get data from request
    name = body.get('name',None)
    value = body.get('value',None)
    global_id = body.get('global_id',None)
    if not global_id:
        properties = db.session.query(Property).all()
        if len(properties)>0:
            global_id = properties[-1].id+1
        else:
            global_id = 1
 
    if not name or not value:
        error = {"Error":"No mandatory property is set."}
        return make_response(jsonify(error),400)
    
    property_d = Property(name=name, value=value, prop_type="DEVICE",parent_id=device.id,global_id=global_id)
    db.session.add(property_d)
    db.session.commit()
    #-------------SDA CODE--------------------#
    q = RedisQueue('register')
    self_prop = {"type":"property","queue":"create"}
    self_prop["content"] = property_d.complete_serializable
    q.put(json.dumps(self_prop))
    #-------------END SDA CODE----------------#
    return make_response(jsonify(property_d.complete_serializable),200)

#Create Device Property
@bp.route('/property/global/api/<int:global_device_id>/', methods=["POST"])
def create_global_device_property(global_device_id):

    device = Device.query.filter_by(global_id=global_device_id).first()
    if not device:
        error = {"Error":"No device exist."}
        return make_response(jsonify(error),400)
      
    body = request.get_json()

    #Get data from request
    name = body.get('name',None)
    value = body.get('value',None)
    global_id = body.get('global_id',None)
    if not global_id:
        properties = db.session.query(Property).all()
        if len(properties)>0:
            global_id = properties[-1].id+1
        else:
            global_id = 1
 
    if not name or not value:
        error = {"Error":"No mandatory property is set."}
        return make_response(jsonify(error),400)
    
    property_d = Property(name=name, value=value, prop_type="DEVICE",parent_id=device.id,global_id=global_id)
    db.session.add(property_d)
    db.session.commit()
    #-------------SDA CODE--------------------#
    q = RedisQueue('register')
    self_prop = {"type":"property","queue":"create"}
    self_prop["content"] = property_d.complete_serializable
    q.put(json.dumps(self_prop))
    #-------------END SDA CODE----------------#
    return make_response(jsonify(property_d.complete_serializable),200)

#Delete Device Property
@bp.route('/property/delete/api/<int:property_id>/', methods=["POST"])
def delete_device_property(property_id):

    property_d = Property.query.filter_by(id=property_id).first()
    if not property_d:
        error = {"Error":"No property exist."}
        return make_response(jsonify(error),400)
      
    body = request.get_json()

    try:
        #Delete the database register
        db.session.delete(property_d)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_prop = {"type":"property","queue":"delete"}
        self_prop["content"] = property_d.complete_serializable
        q.put(json.dumps(self_prop))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)               

    except Exception as e:
        error = {"Error":"Internal Error"}
        return make_response(jsonify(error),500)

#Delete Device Property
@bp.route('/property/delete/api/global/<int:global_id>/', methods=["DELETE"])
def delete_global_device_property(global_id):

    property_d = Property.query.filter_by(global_id=global_id).first()
    if not property_d:
        error = {"Error":"No property exist."}
        return make_response(jsonify(error),400)      
    try:
        #Delete the database register
        db.session.delete(property_d)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_prop = {"type":"property","queue":"delete"}
        self_prop["content"] = property_d.complete_serializable
        q.put(json.dumps(self_prop))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)               

    except Exception as e:
        error = {"Error":"Internal Error"}
        return make_response(jsonify(error),500)