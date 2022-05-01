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

def get_config_values() -> dict:
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
    return settings

def set_config_values(settings):
    last_settings = get_config_values()
    if 'standalone' in settings: last_settings['standalone'] = settings['standalone']
    if 'backendIp' in settings: last_settings['backendIp'] = settings['backendIp']
    if 'backendPort' in settings: last_settings['backendPort'] = settings['backendPort']
    if 'brokerIp' in settings: last_settings['brokerIp'] = settings['brokerIp']
    if 'brokerPort' in settings: last_settings['brokerPort'] = settings['brokerPort']
    if 'backend_topic' in settings: last_settings['backend_topic'] = settings['backend_topic']
    if 'MqttClient' in settings: last_settings['MqttClient'] = settings['MqttClient']
    #Save Settings
    config = configparser.ConfigParser()
    config['DEFAULT'] = last_settings
    with open('init.cfg', 'w') as configfile:
        config.write(configfile)
    return last_settings



def disable_standalone():
    #Update internal Settings
    #FALTA HACER REBOOT DE BASE DE DATOS EN ESTE PUNTO, BORRAR TODAS LAS TABLAS MENOS USUARIOS.
    settings = {}
    settings['standalone'] = 'false'
    settings = set_config_values(settings)

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