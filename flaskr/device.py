import re
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)


from werkzeug.exceptions import abort

from auth import login_required
from models import Device,Property,Resource

from flask import request,Response,make_response
from flask import jsonify
import json
from tinydb import TinyDB, Query
from app import db

import os
import shutil

bp = Blueprint('device', __name__, url_prefix='/device')



#Delete Resource
def delete_resource_method(resource):
    properties = Property.query.filter_by(resource_id=resource.id)
    for property in properties:
        db.session.delete(property)
    db.session.delete(resource)
    db.session.commit()


#Delete Device
def delete_device_method(device):
    devices = Device.query.filter_by(device_parent=device.id)
    for device_s in devices:
        delete_device_method(device_s)    
    resources = Resource.query.filter_by(device_id=device.id)
    for resource in resources:
        delete_resource_method(resource)
    properties = Property.query.filter_by(device_id=device.id)
    for property in properties:
        db.session.delete(property)
    dirc= 'device_data/'+device.tag+'/'
    db.session.delete(device)
    db.session.commit()
    if os.path.isdir(dirc):
        shutil.rmtree(dirc)

#Index
@bp.route('/')
@login_required
def device_index():
    """ Devices Index Section"""
    devices = Device.query.filter_by(device_parent=None)
    return render_template('device/device_index.html', devices=devices)

#Device Detail View
@bp.route('/<int:id>/view', methods=['GET'])
@login_required
def device_view(id):
    """ Devices View Section"""
    device = Device.query.filter_by(id=id).first()
    properties = Property.query.filter_by(device_id=id)
    resources = Resource.query.filter_by(device_id=id)
    offspring_devices = Device.query.filter_by(device_parent=device.id)
    return render_template('device/device_detail.html', device=device,properties=properties,resources=resources,offspring_devices=offspring_devices)


#Create Device
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    devices = db.session.query(Device).all()
    """View for create devices"""
    if request.method == 'POST':

        tag = request.form['tag']
        name = request.form['name']
        is_gateway = request.form.get('is_gateway',False)
        description = request.form['description']
        ip = request.form['ip']
        device_parent = request.form['device_parent']
        error = None

        if is_gateway:
            is_gateway = True

        if not tag or not name:
            error = 'No mandatory property is set.'
        else:
            device = Device.query.filter_by(tag=tag).first()
            if device is not None:
                error = "The tag is already exist."      

        if error is not None:
            flash(error)
        else:            
            try:
                directory = "device_data/"+tag
                if not os.path.exists(directory):
                    os.makedirs(directory)
                if device_parent != "null":
                    device = Device(tag=tag, name=name, description=description,is_gateway=is_gateway, ipv4_address=ip, device_parent=device_parent)
                else:
                    device = Device(tag=tag, name=name, is_gateway=is_gateway, ipv4_address=ip, description=description)
                db.session.add(device)
                db.session.commit()
                return redirect(url_for('device.device_index'))

            except OSError as e:
                flash("Creation of the directory %s failed" % tag)
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('device/create.html',devices=devices)


#Edit Device
@bp.route('/edit_device/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_device(id):
    device = Device.query.filter_by(id=id).first()
    if device is not None:

        """View for create devices"""
        if request.method == 'POST':

            name = request.form['name']
            is_gateway = request.form.get('is_gateway',False)
            description = request.form['description']
            ip = request.form['ip']

            
            if is_gateway:
                is_gateway = True

            
            try:
                device.name = name
                device.is_gateway = is_gateway
                device.description = description
                device.ipv4_address = ip
                db.session.add(device)
                db.session.commit()

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
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Device Not Found")

    return render_template('device/delete.html',device=device)



#Create Property Device
@bp.route('/add_property/<int:id>', methods=('GET', 'POST'))
@login_required
def create_property(id):
    device = Device.query.filter_by(id=id).first()
    """View for create properties"""
    if request.method == 'POST':

        p_name = request.form['name']
        p_value = request.form['value']
        p_description = request.form['description']
        device_id = device.id
        error = None

        if not p_name or not p_value:
            error = 'No mandatory property is set.'

        if error is not None:
            flash(error)
        else:            
            try:
                property_d = Property(name=p_name, value=p_value, description=p_description, device_id=device_id)
                db.session.add(property_d)
                db.session.commit()
                return redirect(url_for('device.device_view',id=device.id))

            except OSError as e:
                flash("Creation of the directory %s failed" % e)
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('device/create_property.html',device=device)


#Create Property Resource
@bp.route('/add_property_resource/<int:id>', methods=('GET', 'POST'))
@login_required
def create_property_resource(id):
    resource = Resource.query.filter_by(id=id).first()
    """View for create properties"""
    if request.method == 'POST':

        p_name = request.form['name']
        p_value = request.form['value']
        p_description = request.form['description']
        resource_id = resource.id
        error = None

        if not p_name or not p_value:
            error = 'No mandatory property is set.'

        if error is not None:
            flash(error)
        else:            
            try:
                property_d = Property(name=p_name, value=p_value, description=p_description, resource_id=resource_id)
                db.session.add(property_d)
                db.session.commit()
                return redirect(url_for('device.resource_view',id=resource.id))

            except OSError as e:
                flash("Creation of the directory %s failed" % e)
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('device/create_property.html',resource=resource)


#Delete Property
@bp.route('/delete_property/<int:id>', methods=['GET','POST'])
@login_required
def delete_property(id):
    property_d = Property.query.filter_by(id=id).first()
    if property_d is not None:
        if request.method == 'POST':
            device_id = property_d.device_id
            try:
                #Delete the database register
                db.session.delete(property_d)
                db.session.commit()
                flash("The property was removed")
                return redirect(url_for('device.device_view',id=device_id))

            except Exception as e:
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Device Not Found")

    return render_template('device/delete_property.html',property=property_d)

#Delete Property
@bp.route('/delete_property_resource/<int:id>', methods=['GET','POST'])
@login_required
def delete_property_resource(id):
    property_d = Property.query.filter_by(id=id).first()
    if property_d is not None:
        if request.method == 'POST':
            resource_id = property_d.resource_id
            try:
                #Delete the database register
                db.session.delete(property_d)
                db.session.commit()
                flash("The property was removed")
                return redirect(url_for('device.resource_view',id=resource_id))

            except Exception as e:
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Device Not Found")

    return render_template('device/delete_property.html',property=property_d)


#Resource View
@bp.route('resource/<int:id>/view', methods=['GET'])
@login_required
def resource_view(id):
    """ Resource View Section"""
    resource = Resource.query.filter_by(id=id).first()
    properties = Property.query.filter_by(resource_id=id)
    return render_template('device/resource_detail.html', resource=resource,properties=properties)


#Create Resource
@bp.route('/add_resource/<int:id>', methods=('GET', 'POST'))
@login_required
def create_resource(id):
    device = Device.query.filter_by(id=id).first()
    """View for create resources"""
    if request.method == 'POST':

        r_tag = request.form['tag']
        r_name = request.form['name']
        r_type = request.form['type']
        r_description = request.form['description']
        device_id = device.id
        error = None

        if not r_tag or not r_name or not r_type:
            error = 'No mandatory property is set.'
        
        resource = Resource.query.filter_by(tag=r_tag).first()
        if resource is not None:
            error = 'The Tag is already exist'

        if error is not None:
            flash(error)
        else:            
            try:
                resource_d = Resource(tag=r_tag, name=r_name, description=r_description, resource_type=r_type,device_id=device_id)
                db.session.add(resource_d)
                db.session.commit()
                return redirect(url_for('device.device_view',id=device.id))

            except OSError as e:
                flash("Creation of the directory %s failed" % e)
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('device/create_resource.html',device=device)


#Edith Resource
@bp.route('/edit_resource/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_resource(id):
    resource = Resource.query.filter_by(id=id).first()
    if resource is not None:

        """View for create devices"""
        if request.method == 'POST':

            r_name = request.form['name']
            r_description = request.form['description']
            r_type = request.form['type']
            
            
            try:
                resource.name = r_name
                resource.description = r_description
                resource.resource_type = r_type
                db.session.add(resource)
                db.session.commit()

                return redirect(url_for('device.resource_view',id = resource.id))

            except Exception as e:
                print(e)
                flash("DB Update Failed")
    else:
        flash("Resource Not Found")

    return render_template('device/edit_resource.html',resource=resource)


#Delete Resource
@bp.route('/delete_resource/<int:id>', methods=['GET','POST'])
@login_required
def delete_resource(id):
    resource_d = Resource.query.filter_by(id=id).first()
    if resource_d is not None:
        if request.method == 'POST':
            device_id = resource_d.device_id
            try:
                #Delete the database register
                db.session.delete(resource_d)
                db.session.commit()
                flash("The resource was removed")
                return redirect(url_for('device.device_view',id=device_id))

            except Exception as e:
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Resource Not Found")

    return render_template('device/delete_resource.html',resource=resource_d)

"""------------------------------------------------------------------
Rest API Methods
-----------------------------------------------------------------"""

#Devices Rest API

#Get all devices
@bp.route('/api/', methods=["GET"])
def get_devices_api():
    return jsonify(devices=[i.serialize for i in Device.query.all()])

#Get a single device
@bp.route('/api/<tag>/', methods=["GET"])
def get_device_api(tag):
    device = Device.query.filter_by(tag=tag).first()
    return jsonify(device.serialize)

#Create a Device
@bp.route('/api/', methods=["POST"])
def add_device_api():
    body = request.get_json()
    if 'tag' not in body or 'name' not in body:
        error = {"Error":"No mandatory property is set."}
        return make_response(jsonify(error),400)
    else:
        tag = body['tag']
        name = body['name']
    
        description = body.get('description',None)
        device_parent = body.get('device_parent',None)
        is_gateway = body.get('is_gateway',None)
        ipv4_address = body.get('ipv4_address',None)
        properties = body.get('properties',None)
        resources = body.get('resources',None)
        
        devices = Device.query.filter_by(tag=tag).first()
        if devices is not None:
            error = {"Error":"The device with this tag is already exist."}
            return make_response(jsonify(error),400)
        if device_parent is not None:
            device = Device.query.filter_by(id=device_parent)
            if device is None:
                error = {"Error":"The parent device ID not exist."}
                return make_response(jsonify(error),400)
        
        if properties:
            for proper in properties:
                keys_list = list(proper.keys())
                if "name" not in keys_list or "value" not in keys_list:
                    error = {"Error":"The properties doesn't have the mandatory attributes."}
                    return make_response(jsonify(error),400)
        
        if resources:
            for resource in resources:
                keys_list = list(resource.keys())
                if "tag" not in keys_list or "name" not in keys_list or "resource_type" not in keys_list:
                    error = {"Error":"The resources doesn't have the mandatory attributes."}
                    return make_response(jsonify(error),400)

        device = Device(tag=tag,name=name,description=description,ipv4_address=ipv4_address,is_gateway=is_gateway,device_parent=device_parent)
        db.session.add(device)
        db.session.commit()

        if properties:
            for proper in properties:
                if "description" not in list(proper.keys()):
                    proper_d = Property(name=proper["name"],value=proper["value"],device_id=device.id)
                else:
                    proper_d = Property(name=proper["name"],value=proper["value"],description=proper["description"],device_id=device.id)
                db.session.add(proper_d)
        
        if resources:
            for resource in resources:
                if "description" not in list(resource.keys()):
                    resource_d = Resource(tag=resource["tag"],name=resource["name"],resource_type=resource["resource_type"],device_id=device.id)
                else:
                    resource_d = Resource(tag=resource["tag"],name=resource["name"],description=resource["description"],resource_type=resource["resource_type"],device_id=device.id)
                db.session.add(resource_d)
        
        db.session.commit()        
        return jsonify(device.serialize)

#Update device
@bp.route('/api/<tag>/', methods=["PUT"])
def update_device_api(tag):
    device = Device.query.filter_by(tag=tag).first()
    
    if device is not None:
        body = request.get_json()
        propers = []
        resources_list = []
        
        #Get properties from request
        name = body.get('name',None)
        description = body.get('description',None)
        device_parent = body.get('device_parent',None)
        is_gateway = body.get('is_gateway',None)
        ipv4_address = body.get('ipv4_address',None)
        properties = body.get('properties',None)
        resources = body.get('resources',None)


        #Set properties to model
        if name:
            device.name = name
        if description:
            device.description = description
        if device_parent:
            device.device_parent = device_parent
        if is_gateway is not None:
            device.is_gateway = is_gateway
        if ipv4_address:
            device.ipv4_address = ipv4_address
        if properties:            
            for proper in properties:
                keys_list = list(proper.keys())
                if "name" not in keys_list or "value" not in keys_list:
                    error = {"Error":"The properties doesn't have the mandatory attributes."}
                    return make_response(jsonify(error),400)
                properti = Property(name=proper["name"],value=proper["value"],description=proper.get("description",None))
                propers.append(properti)
        if resources:
            for resource in resources:
                keys_list = list(resource.keys())
                if "tag" not in keys_list or "name" not in keys_list or "resource_type" not in keys_list:
                    error = {"Error":"The resources doesn't have the mandatory attributes."}
                    return make_response(jsonify(error),400)
                resource_i = Resource(tag=resource["tag"],name=resource.get("name",None),resource_type=resource.get("resource_type",None))
                resources_list.append(resource_i)

        
        db.session.add(device)
        db.session.commit()

        if len(propers)>0:
            for new_proper in propers:
                proper = Property.query.filter_by(device_id=device.id,name=new_proper.name).first()
                if proper is not None:
                    proper.value = new_proper.value
                    proper.description = new_proper.description
                    db.session.add(proper)
                else:
                    new_proper.device_id = device.id
                    db.session.add(new_proper)
            db.session.commit()
        

        if len(resources_list)>0:
            for new_resource in resources_list:
                resource = Resource.query.filter_by(device_id=device.id,tag=new_resource.tag).first()                
                if resource is not None:
                    print("entro aquí")
                    resource.name = new_resource.name
                    resource.resource_type = new_resource.resource_type
                    if new_resource.description:
                        resource.description = new_resource.description
                    db.session.add(resource)
                else:
                    print("entro aca")
                    new_resource.device_id = device.id
                    db.session.add(new_resource)
            db.session.commit()

        return jsonify(device.serialize)

    else:
        error = {"Error":"The device doesn't exist."}
        return make_response(jsonify(error),400)
    

    
#Delete device
@bp.route('/api/<tag>/', methods=["DELETE"])
def delete_device_api(tag):
    device = Device.query.filter_by(tag=tag).first()
    try:
        delete_device_method(device)
        return make_response(jsonify({"Delete":"The device was remove"}),200)

    except Exception as e:
        error = {"Error":"It's not possible to delete the device"}
        return make_response(jsonify(error),400)



@bp.route('/get_data', methods=('GET', 'POST'))
#@login_required
def get_data():
    device_tag = request.args.get('device_tag',None)
    table = request.args.get('device_table',None)
    if device_tag and table:
        dbn = TinyDB('device_data/'+str(device_tag)+'/'+str(device_tag)+'.json')
        #data = json.load(db.all())
        table = dbn.table(str(table))
        data = table.all()
    else:
        data = {}
    return Response( json.dumps(data) ,mimetype="application/json", status=200)


