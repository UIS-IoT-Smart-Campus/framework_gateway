from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)


from werkzeug.exceptions import abort

from auth import login_required
from models import Device,Property

from flask import request,Response,make_response
from flask import jsonify
import json
from tinydb import TinyDB, Query
from app import db

import os
import shutil

bp = Blueprint('device', __name__, url_prefix='/device')


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
    offspring_devices = Device.query.filter_by(device_parent=device.id)
    return render_template('device/device_detail.html', device=device,properties=properties,offspring_devices=offspring_devices)


#Create Device
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    devices = db.session.query(Device).filter(Device.device_type.in_(('COMPOUND','COMPOUND SENSOR','COMPOUND ACTUATOR')))
    """View for create devices"""
    if request.method == 'POST':

        tag = request.form['tag']
        name = request.form['name']
        device_type = request.form['device_type']
        description = request.form['description']
        device_parent = request.form['device_parent']
        error = None

        if not tag or not name or not device_type:
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
                    device = Device(tag=tag, name=name, device_type=device_type, description=description, device_parent=device_parent)
                else:
                    device = Device(tag=tag, name=name, device_type=device_type, description=description)
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
            device_type = request.form['device_type']
            description = request.form['description']
            
            try:
                device.name = name
                device.device_type = device_type
                device.description = description
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
                dirc= 'device_data/'+device.tag+'/'
                #Delete the database register
                properties = Property.query.filter_by(device_id=device.id)
                for proper in properties:
                    db.session.delete(proper)
                db.session.delete(device)
                db.session.commit()
                #Delete the folder and NOSQL database for the device.
                if os.path.isdir(dirc):
                    shutil.rmtree(dirc)
                flash("The device was removed")
                return redirect(url_for('device.device_index'))

            except Exception as e:
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Device Not Found")

    return render_template('device/delete.html',device=device)



#Create Property
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
                flash("Creation of the directory %s failed" % tag)
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('device/create_property.html',device=device)


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

"""------------------------------------------------------------------
Rest API Methods
-----------------------------------------------------------------"""

#Devices Rest API

#Get all devices
@bp.route('/devices', methods=["GET"])
def get_devices_api():
    return jsonify(devices=[i.serialize for i in Device.query.all()])

#Get a single device
@bp.route('/devices/<tag>', methods=["GET"])
def get_device_api(tag):
    device = Device.query.filter_by(tag=tag).first()
    return jsonify(device.serialize)

#Create a Device
@bp.route('/devices', methods=["POST"])
def add_device_api():
    body = request.get_json()
    tag = body['tag']
    name = body['name']
    device_type = body['device_type']
    description = body['description']
    device_parent = body['device_parent']
    properties = body['properties']

    error = None

    if not tag or not name or not device_type:
        error = {"Error":"No mandatory property is set."}
        return make_response(jsonify(error),400)
    else:
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
                if "name" not in keys_list or "value" not in keys_list or "description" not in keys_list:
                    error = {"Error":"The properties doesn't have the mandatory attributes."}
                    return make_response(jsonify(error),400)

        device = Device(tag=tag,name=name,device_type=device_type,description=description,device_parent=device_parent)
        db.session.add(device)
        db.session.commit()

        if properties:
            for proper in properties:
                proper = Property(name=proper["name"],value=proper["value"],description=proper["description"],device_id=device.id)
                db.session.add(proper)
        
        
        db.session.commit()        
        return jsonify(device.serialize)

    return jsonify(devices=[i.serialize for i in Device.query.all()])

#Update device
@bp.route('/devices/<tag>', methods=["PUT"])
def update_device_api(tag):
    device = Device.query.filter_by(tag=tag).first()
    
    if device is not None:
        name = request.json['name']
        device_type = request.json['device_type']
        description = request.json['description']
        device_parent = request.json['device_parent']
        properties = request.json['properties']

        if name:
            device.name = name
        if device_type:
            device.device_type = device_type
        if description:
            device.description = description
        if device_parent:
            device.device_parent = device_parent
        if properties:
            propers = []
            for proper in properties:
                keys_list = list(proper.keys())
                if "name" not in keys_list or "value" not in keys_list or "description" not in keys_list:
                    error = {"Error":"The properties doesn't have the mandatory attributes."}
                    return make_response(jsonify(error),400)
                properti = Property(name=proper["name"],value=proper["value"],description=proper["description"])
                propers.append(properti)
        
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
        return jsonify(device.serialize)

    else:
        error = {"Error":"The device doesn't exist."}
        return make_response(jsonify(error),400)
    

    
#Delete device
@bp.route('/devices/<tag>', methods=["DELETE"])
def delete_device_api(tag):
    device = Device.query.filter_by(tag=tag).first()
    try:
        dirc= 'device_data/'+device.tag+'/'
        #Delete the database register
        properties = Property.query.filter_by(device_id=device.id)
        for proper in properties:
            db.session.delete(proper)
        db.session.delete(device)
        db.session.commit()
        #Delete the folder and NOSQL database for the device.
        if os.path.isdir(dirc):
            shutil.rmtree(dirc)
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


