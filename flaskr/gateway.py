from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from auth import login_required
from persistence import Persistence
from app import db

from flask import jsonify,request
import json
from tinydb import TinyDB, Query

import os
import configparser

bp = Blueprint('gateway', __name__, url_prefix='/gateway')



@bp.route('/get_records', methods=('GET', 'POST'))
#@login_required
def get_records():
    data = Persistence().get_gateway_records()
    return jsonify(data)


@bp.route('/settings', methods=('GET', 'POST'))
#@login_required
def settings():
    if request.method == 'POST':
        os.system('sudo reboot now')
        return render_template('gateway/settings.html')
    else:
        settings = {}
        config = configparser.ConfigParser()
        config.readfp(open('init.cfg'))
        settings["standalone"] = config.getboolean('DEFAULT','standalone')
        settings["backendIp"] = config.get('DEFAULT','backendIp')
        settings["backendPort"] = config.get('DEFAULT','backendPort')
        settings["brokerIp"] = config.get('DEFAULT','brokerIp')
        settings["brokerPort"] = config.get('DEFAULT','brokerPort')
        settings["backend_topic"] = config.get('DEFAULT','backend_topic')
        settings["MqttClient"] = config.get('DEFAULT','MqttClient')
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
        #Save Settings
        config = configparser.ConfigParser()
        config['DEFAULT'] = settings
        with open('init.cfg', 'w') as configfile:
            config.write(configfile)

        return redirect(url_for('gateway.settings'))
    else:
        settings = {}
        config = configparser.ConfigParser()
        config.readfp(open('init.cfg'))
        settings["standalone"] = config.getboolean('DEFAULT','standalone')
        settings["backendIp"] = config.get('DEFAULT','backendIp')
        settings["backendPort"] = config.get('DEFAULT','backendPort')
        settings["brokerIp"] = config.get('DEFAULT','brokerIp')
        settings["brokerPort"] = config.get('DEFAULT','brokerPort')
        settings["backend_topic"] = config.get('DEFAULT','backend_topic')
        settings["MqttClient"] = config.get('DEFAULT','MqttClient')
        return render_template('gateway/update-settings.html',settings=settings)