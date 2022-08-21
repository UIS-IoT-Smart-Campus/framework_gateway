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

import os
import shutil
import selfconfig as sc

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
    dirc= 'device_data/'+str(device.id)+'/'
    db.session.delete(device)
    db.session.commit()
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
@bp.route('/<int:id>/view', methods=['GET'])
@login_required
def device_view(id):
    """ Devices View Section"""
    device = Device.query.filter_by(id=id).first()
    properties = Property.query.filter_by(device_id=id)
    resources = Resource.query.filter_by(device_id=id)
    offspring_devices = Device.query.filter_by(device_parent=device.id)
    if device.id:
        db = TinyDB('device_data/'+str(device.id)+'/'+str(device.id)+'.json')
        tables = db.tables()
        data = {}
        for table in tables:
            data[table] = db.table(str(table)).all()

    return render_template('device/device_detail.html', device=device,properties=properties,resources=resources,offspring_devices=offspring_devices,tables=tables,data=data)


#Create Device
@bp.route('/create', methods=('GET', 'POST'))
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
                categories_instances = []                
                if device_parent != "null":
                    device = Device(name=name, description=description,global_id=count_dev, is_gateway=is_gateway, create_at = create_at, update_at=update_at, device_parent=device_parent)
                else:
                    device = Device(name=name, description=description,global_id=count_dev, is_gateway=is_gateway, create_at = create_at, update_at=update_at, device_parent=1)
                db.session.add(device)
                db.session.commit()
                return redirect(url_for('device.device_index'))

            except OSError as e:
                flash("Creation of the directory %s failed" % count_dev_str)
            except Exception as e:
                print(e)
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

        r_name = request.form['name']
        r_type = request.form['type']
        r_description = request.form['description']
        device_id = device.id
        error = None

        if not r_name or not r_type:
            error = 'No mandatory property is set.'        

        if error is not None:
            flash(error)
        else:            
            try:
                last_resource = db.session.query(Resource).order_by(Resource.id.desc()).first()
                if last_resource != None:
                    last_resource_id = last_resource.id+1
                else:
                    last_resource_id = 1
                resource_d = Resource(name=r_name, description=r_description,global_id = last_resource_id, resource_type=r_type,device_id=device_id)
                db.session.add(resource_d)
                db.session.commit()
                return redirect(url_for('device.device_view',id=device.id))

            except OSError as e:
                flash("Creation of the directory %s failed" % e)
            except Exception as e:
                print(e)
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

#########################
# DEVICES API REST #####
########################

#Get all devices except the gateway
@bp.route('/api/', methods=["GET"])
def get_devices_api():
    return jsonify(devices=[i.serialize for i in Device.query.filter(Device.id != 1).all()])

#Get a single device
@bp.route('/api/<id>/', methods=["GET"])
def get_device_api(id):
    device = Device.query.filter_by(id=id).first()
    return jsonify(device.serialize)

#Create a Device
@bp.route('/api/', methods=["POST"])
def add_device_api():
    body = request.get_json()
    if 'name' not in body:
        error = {"Error":"No mandatory property is set."}
        return make_response(jsonify(error),400)
    else:
        
        name = body['name']    
        description = body.get('description',None)
        global_id = body.get('global_id',None)
        device_parent = body.get('device_parent',None)
        is_gateway = body.get('is_gateway',None)        
        properties = body.get('properties',None)
        resources = body.get('resources',None)
        
        devices = Device.query.filter_by(name=name).first()
        if devices is not None:
            error = {"Error":"The device with this name is already exist."}
            return make_response(jsonify(error),400)
        if device_parent is not None:
            device = Device.query.filter_by(id=device_parent)
            if device is None:
                error = {"Error":"The parent device ID not exist."}
                return make_response(jsonify(error),400)
        else:
            device_parent=1
        
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

        device = Device(name=name,description=description,global_id=global_id,is_gateway=is_gateway,device_parent=device_parent)
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
                    resource_d = Resource(name=resource["name"],resource_type=resource["resource_type"],device_id=device.id)
                else:
                    resource_d = Resource(name=resource["name"],description=resource["description"],resource_type=resource["resource_type"],device_id=device.id)
                db.session.add(resource_d)
        
        db.session.commit()

        #create directory for data
        try:
            directory = "device_data/"+str(device.id)
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError as e:
            flash("Creation of the directory %s failed" % count_dev_str)
        
        return jsonify(device.serialize)

#Update device
@bp.route('/api/<id>/', methods=["PUT"])
def update_device_api(id):
    device = Device.query.filter_by(id=id).first()
    
    if device is not None:
        body = request.get_json()
        propers = []
        resources_list = []
        
        #Get properties from request
        name = body.get('name',None)
        description = body.get('description',None)
        device_parent = body.get('device_parent',None)
        is_gateway = body.get('is_gateway',None)
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
                resource_i = Resource(name=resource.get("name",None),resource_type=resource.get("resource_type",None))
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
                resource = Resource.query.filter_by(device_id=device.id).first()                
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
@bp.route('/api/<id>/', methods=["DELETE"])
def delete_device_api(id):
    device = Device.query.filter_by(id=id).first()
    try:
        delete_device_method(device)
        return make_response(jsonify({"Delete":"The device was remove"}),200)

    except Exception as e:
        error = {"Error":"It's not possible to delete the device"}
        return make_response(jsonify(error),400)



@bp.route('/get_data', methods=('GET', 'POST'))
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
# RESOURCES API REST #####
########################
--------------------------------------------------------------------------------------------"""


#Get all Resources
@bp.route('resource/api/', methods=["GET"])
def get_resources_api():
    return jsonify(resources=[i.serialize for i in Resource.query.all()])

#Get specific Resource by id
@bp.route('resource/api/<id>/', methods=["GET"])
def get_resource_by_id(id):
    resource = Resource.query.filter_by(id=id).first()
    if resource is not None:
        return jsonify(resource.serialize)
    else:
        error={"error":"Not resource found"}
        return make_response(jsonify(error),400)


#Create a Resource
@bp.route('/resource/api/', methods=["POST"])
def add_resource_api():
    body = request.get_json()
    if 'name' not in body or 'resource_type' not in body or 'device_id' not in body:
        error = {"Error":"No mandatory property is set."}
        return make_response(jsonify(error),400)
    else:
        name = body['name']
        resource_type = body['resource_type']
        device_id = body['device_id']          
        description = body.get('description',None)
        properties = body.get('properties',None)
        
        device = Device.query.filter_by(id=device_id)
        if device is None:
            error = {"Error":"The parent device ID not exist."}
            return make_response(jsonify(error),400)
        
        if properties:
            for proper in properties:
                keys_list = list(proper.keys())
                if "name" not in keys_list or "value" not in keys_list:
                    error = {"Error":"The properties doesn't have the mandatory attributes."}
                    return make_response(jsonify(error),400)
        
        resource = Resource(name=name,description=description,resource_type=resource_type,device_id=device_id)
        db.session.add(resource)
        db.session.commit()

        if properties:
            for proper in properties:
                if "description" not in list(proper.keys()):
                    proper_d = Property(name=proper["name"],value=proper["value"],resource_id=resource.id)
                else:
                    proper_d = Property(name=proper["name"],value=proper["value"],description=proper["description"],resource_id=resource.id)
                db.session.add(proper_d)
        
        db.session.commit()        
        return jsonify(resource.serialize)



#Update resource
@bp.route('/resource/api/<id>/', methods=["PUT"])
def update_resource_api(id):
    resource = Resource.query.filter_by(id=id).first()
    
    if resource is not None:
        body = request.get_json()
        propers= []
        
        #Get properties from request
        name = body.get('name',None)
        description = body.get('description',None)
        resource_type = body.get('resource_type',None)
        device_id = body.get('device_id',None)
        properties = body.get('properties',None)


        #Set properties to model
        if name:
            resource.name = name
        if description:
            resource.description = description
        if resource_type:
            resource.resource_type = resource_type
        if device_id:
            resource.device_id = device_id
        if properties:            
            for proper in properties:
                keys_list = list(proper.keys())
                if "name" not in keys_list or "value" not in keys_list:
                    error = {"Error":"The properties doesn't have the mandatory attributes."}
                    return make_response(jsonify(error),400)
                properti = Property(name=proper["name"],value=proper["value"],description=proper.get("description",None))
                propers.append(properti)        

        
        db.session.add(resource)
        db.session.commit()

        if len(propers)>0:
            for new_proper in propers:
                proper = Property.query.filter_by(resource_id=resource.id,name=new_proper.name).first()
                if proper is not None:
                    proper.value = new_proper.value
                    proper.description = new_proper.description
                    db.session.add(proper)
                else:
                    new_proper.resource_id = resource.id
                    db.session.add(new_proper)
            db.session.commit()
                
        return jsonify(resource.serialize)

    else:
        error = {"Error":"The device doesn't exist."}
        return make_response(jsonify(error),400)


#Delete Resource
@bp.route('/resource/api/<id>/', methods=["DELETE"])
def delete_resource_api(id):
    resource = Resource.query.filter_by(id=id).first()
    try:
        delete_resource_method(resource)
        return make_response(jsonify({"Delete":"The resource was remove"}),200)

    except Exception as e:
        error = {"Error":"It's not possible to delete the device"}
        return make_response(jsonify(error),400)






"""
REMOTE ADMIN API REST
"""


"""----------------------------------------------------------------------------------------------
#########################
# REMOTE ADMIN DEVICE API REST #####
########################
--------------------------------------------------------------------------------------------"""



"""----------------------------------------------------------------------------------------------
#########################
# REMOTE ADMIN PROPERTIES API REST #####
########################
--------------------------------------------------------------------------------------------"""


#Update resource
@bp.route('/property/api/<global_id>/', methods=["PUT"])
def update_global_property(global_id):
    prop = Property.query.filter_by(global_id=global_id).first()
    
    if prop is not None:
        body = request.get_json()

        #Get data from request
        name = body.get('name',None)
        value = body.get('value',None)
        description = body.get('description',None)

        #Set properties to model
        if name:
            prop.name = name
        if value:
            prop.value = value
        if description:
            prop.description = description
                
        db.session.add(prop)
        db.session.commit()        
                
        return jsonify(prop.serialize)

    else:
        error = {"Error":"The property doesn't exist."}
        return make_response(jsonify(error),400)