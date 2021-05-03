from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)


from werkzeug.exceptions import abort

from auth import login_required
from models import Device

from flask import request
from flask import jsonify
import json
from tinydb import TinyDB, Query
from app import db

import os

bp = Blueprint('device', __name__, url_prefix='/device')



@bp.route('/')
@login_required
def device_index():
    """ Devices Index Section"""
    devices = Device.query.all()
    return render_template('device/device_index.html', devices=devices)


#Create Device
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """View for create devices"""
    if request.method == 'POST':

        tag = request.form['tag']
        name = request.form['name']
        device_type = request.form['device_type']
        description = request.form['description']
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
                directory = "flaskr/device_data/"+tag
                if not os.path.exists(directory):
                    os.makedirs(directory)
                device = Device(tag=tag, name=name, device_type=device_type, description=description)
                db.session.add(device)
                db.session.commit()
                return redirect(url_for('device.device_index'))

            except OSError as e:
                flash("Creation of the directory %s failed" % tag)
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('device/create.html')


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
                flash("DB Creation Failed")
    else:
        flash("Device Not Found")

    return render_template('device/edit.html',device=device)


@bp.route('/<int:id>/view', methods=['GET'])
@login_required
def device_view(id):
    """ Devices View Section"""
    device = Device.query.filter_by(id=id).first()
    return render_template('device/device_detail.html', device=device)


@bp.route('/get_data', methods=('GET', 'POST'))
#@login_required
def get_data():
    device_tag = request.args.get('device_tag',None)
    table = request.args.get('device_table',None)
    if device_tag and table:
        dbn = TinyDB('flaskr/device_data/'+str(device_tag)+'/'+str(device_tag)+'.json')
        #data = json.load(db.all())
        table = dbn.table(str(table))
        data = table.all()
    else:
        data = {}
    return jsonify(data)


