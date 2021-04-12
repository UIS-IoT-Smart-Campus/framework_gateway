from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)


from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.models.models import DeviceModel
from flaskr.popyo.device import Device
from flask import request

from flask import jsonify
import json
from tinydb import TinyDB, Query

import os

bp = Blueprint('device', __name__, url_prefix='/device')



@bp.route('/')
@login_required
def device_index():
    """ Devices Index Section"""
    devices = DeviceModel.get_all()
    return render_template('device/device_index.html', devices=devices)


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
            device = DeviceModel.get_device_tag(tag)
            if device.tag is not None:
                error = "The tag is already exist."      

        if error is not None:
            flash(error)
        else:            
            try:
                directory = "flaskr/device_data/"+tag
                if not os.path.exists(directory):
                    os.makedirs(directory)
                device = Device()
                device.set_data(tag,name,device_type,description)
                DeviceModel.create_device(device)
                return redirect(url_for('device.device_index'))

            except OSError as e:
                flash("Creation of the directory %s failed" % tag)
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('device/create.html')

@bp.route('/<int:id>/view', methods=['GET'])
@login_required
def device_view(id):
    """ Devices View Section"""
    device = DeviceModel.get_device_id(id)
    return render_template('device/device_detail.html', device=device)


@bp.route('/get_data', methods=('GET', 'POST'))
#@login_required
def temp_lebrija():
    device_tag = request.args.get('device_tag',None)
    table = request.args.get('device_table',None)
    if device_tag and table:
        db = TinyDB('flaskr/device_data/'+str(device_tag)+'/'+str(device_tag)+'.json')
        #data = json.load(db.all())
        table = db.table(str(table))
        data = table.all()
    else:
        data = {}
    return jsonify(data)


