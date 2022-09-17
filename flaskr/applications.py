from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from auth import login_required
from models import Application,Device
import selfconfig as sc
from app import db
from datetime import date
from flask import jsonify, make_response
from redisTool import RedisQueue
import json

bp = Blueprint('applications', __name__, url_prefix='/apps')


#Index
@bp.route('/')
@login_required
def applications_index():
    """ Applications Index Section"""
    applications = Application.query.all()
    settings = sc.get_config_values()
    return render_template('applications/app_index.html', applications=applications,settings=settings)

#Application Detail View
@bp.route('/<int:id>/view', methods=['GET', 'POST'])
@login_required
def application_view(id):
    """ Application View Section"""
    application = Application.query.filter_by(id=id).first()
    if request.method == 'POST':
        device_id = request.form.get('device_id',None)
        if device_id is not None:
            device = Device.query.filter_by(id=device_id).first()
            if device is not None:
                application.devices.append(device)
                db.session.add(application)
                db.session.commit()
                #-------------SDA CODE--------------------#
                q = RedisQueue('register')
                self_device = {"type":"app_device","queue":"create"}
                self_device["content"] = {"app_id":application.global_id,"device_id":device.global_id}
                q.put(json.dumps(self_device))
                #-------------END SDA CODE----------------#   
                return redirect(url_for('applications.application_view',id = application.id))
    return render_template('applications/detail_app.html', application=application)



#Create Application
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_application():
    """View for create applications"""
    if request.method == 'POST':

        name = request.form['name']        
        create_at = date.today()
        error = None

        if not name:
            error = 'No mandatory property is set.'     

        if error is not None:
            flash(error)
        else:            
            try:
                apps = Application.query.all()
                if len(apps)!=0:
                    g_id = apps[len(apps)-1].id+1
                else:
                    g_id = 1
                application = Application(global_id = g_id,name=name, create_at=create_at)
                db.session.add(application)
                db.session.commit()
                #-----------SDA CODE--------------------#
                q = RedisQueue('register')
                self_device = {"type":"app","queue":"create"}
                self_device["content"] = application.light_serialize
                q.put(json.dumps(self_device))
                #-------------END SDA CODE--------------------#             
                return redirect(url_for('applications.applications_index'))
           
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('applications/create_app.html')


#Edit Application
@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_application(id):
    application = Application.query.filter_by(id=id).first()
    if application is not None:

        """View for create devices"""
        if request.method == 'POST':

            name = request.form['name']            
                       
            try:
                application.name = name
                db.session.add(application)
                db.session.commit()
                #-----------SDA CODE--------------------#
                q = RedisQueue('register')
                self_device = {"type":"app","queue":"update"}
                self_device["content"] = application.light_serialize
                q.put(json.dumps(self_device))
                #-------------END SDA CODE--------------------#  

                return redirect(url_for('applications.application_view',id = application.id))

            except Exception as e:
                print(e)
                flash("DB Update Failed")
    else:
        flash("Application Not Found")

    return render_template('applications/edit_app.html',application=application)



#Delete Application
@bp.route('/delete/<int:id>', methods=['GET','POST'])
@login_required
def delete_application(id):
    application = Application.query.filter_by(id=id).first()
    if application is not None:
        if request.method == 'POST':
            try:                
                db.session.delete(application)
                db.session.commit()
                #-----------SDA CODE--------------------#
                q = RedisQueue('register')
                self_device = {"type":"app","queue":"delete"}
                self_device["content"] = application.light_serialize
                q.put(json.dumps(self_device))
                #-------------END SDA CODE--------------------#             
                flash("The Application was removed")
                return redirect(url_for('applications.applications_index'))

            except Exception as e:
                print(e)
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Application Not Found")

    return render_template('applications/delete_app.html',application=application)

"""------------------------------------------------------------------
API REST Methods
-----------------------------------------------------------------"""

#########################
# APPS API REST #####
########################
#Get a apps
@bp.route('/api/', methods=["GET"])
def get_all():
    return jsonify(applications=[i.serialize for i in Application.query.all()])

#Get a apps
@bp.route('/api/<id>', methods=["GET"])
def get_app_by_id(id):
    app = Application.query.filter_by(id=id).first()
    return jsonify(app.serialize)



#Create a App
@bp.route('/create/api/', methods=["POST"])
def create_app():
    body = request.get_json()
    if 'name' not in body:
        error = {"Error":"No mandatory property is set."}
        return make_response(jsonify(error),400)
    else:        
        name = body['name']           
        global_id = body.get('global_id',None)
        if not global_id:
            apps = db.session.query(Application).all()
            if len(apps)>0:
                global_id = apps[-1].id+1
            else:
                global_id = 1
        application = Application(name=name,global_id=global_id)
        db.session.add(application)
        db.session.commit()
        #-----------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"app","queue":"create"}
        self_device["content"] = application.light_serialize
        q.put(json.dumps(self_device))
        #-------------END SDA CODE--------------------#        
        return jsonify(application.light_serialize)


#Update a App
@bp.route('/update/api/<int:id>/', methods=["PUT"])
def update_app(id):
    application = Application.query.filter_by(id=id).first()
    if not application:
        error = {"Error":"Application doesn't exist."}
        return make_response(jsonify(error),400)    
    else:
        body = request.get_json()     
        name = body['name']           
        global_id = body.get('global_id',None)
        #Set properties to model
        if name:
            application.name = name
        if global_id:
            application.global_id = global_id
        db.session.add(application)
        db.session.commit()
        #-----------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"app","queue":"update"}
        self_device["content"] = application.light_serialize
        q.put(json.dumps(self_device))
        #-------------END SDA CODE--------------------#        
        return jsonify(application.light_serialize)


#Delete a App
@bp.route('/delete/api/<int:id>/', methods=["DELETE"])
def delete_app(id):
    application = Application.query.filter_by(id=id).first()
    if not application:
        error = {"Error":"Application doesn't exist."}
        return make_response(jsonify(error),400)    
    else:        
        db.session.delete(application)
        db.session.commit()
        #-----------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"app","queue":"delete"}
        self_device["content"] = application.light_serialize
        q.put(json.dumps(self_device))
        #-------------END SDA CODE--------------------#        
        return jsonify({"RESULT":"OK"})

#Delete a App
@bp.route('/delete/api/global/<int:app_global_id>/', methods=["DELETE"])
def delete_global_app(app_global_id):
    application = Application.query.filter_by(global_id=app_global_id).first()
    if not application:
        error = {"Error":"Application doesn't exist."}
        return make_response(jsonify(error),400)    
    else:        
        db.session.delete(application)
        db.session.commit()
        #-----------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"app","queue":"delete"}
        self_device["content"] = application.light_serialize
        q.put(json.dumps(self_device))
        #-------------END SDA CODE--------------------#        
        return jsonify({"RESULT":"OK"})

#Add App device
@bp.route('/device/api/<int:app_id>/', methods=["POST"])
def set_app_device(app_id):
    application = Application.query.filter_by(id=app_id).first()
    if not application:
        error = {"Error":"Application doesn't exist."}
        return make_response(jsonify(error),400)
    body = request.get_json()
    device_id = body.get('device_id',None)    
    if device_id is not None:
        device = Device.query.filter_by(id=device_id).first()
        application.devices.append(device)
        db.session.add(application)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"app_device","queue":"create"}
        self_device["content"] = {"app_id":application.global_id,"device_id":device.global_id}
        q.put(json.dumps(self_device))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)

#Add App device
@bp.route('/device/api/global/<int:app_global_id>/', methods=["POST"])
def set_app_global_device(app_global_id):
    application = Application.query.filter_by(global_id=app_global_id).first()
    if not application:
        error = {"Error":"Application doesn't exist."}
        return make_response(jsonify(error),400)
    body = request.get_json()
    device_id = body.get('device_id',None)    
    if device_id is not None:
        device = Device.query.filter_by(id=device_id).first()
        application.devices.append(device)
        db.session.add(application)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"app_device","queue":"create"}
        self_device["content"] = {"app_id":application.global_id,"device_id":device.global_id}
        q.put(json.dumps(self_device))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)

#Delete App device
@bp.route('/device/delete/api/<int:app_id>/', methods=["POST"])
def delete_app_device(app_id):
    application = Application.query.filter_by(id=app_id).first()
    if not application:
        error = {"Error":"Application doesn't exist."}
        return make_response(jsonify(error),400)
    body = request.get_json()
    device_id = body.get('device_id',None)    
    if device_id is not None:
        device = Device.query.filter_by(id=device_id).first()
        application.devices.remove(device)
        db.session.add(application)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"app_device","queue":"delete"}
        self_device["content"] = {"app_id":application.global_id,"device_id":device.global_id}
        q.put(json.dumps(self_device))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)

#Delete App device
@bp.route('/device/delete/api/global/<int:global_app_id>/', methods=["POST"])
def delete_app_global_device(global_app_id):
    application = Application.query.filter_by(global_id=global_app_id).first()
    if not application:
        error = {"Error":"Application doesn't exist."}
        return make_response(jsonify(error),400)
    body = request.get_json()
    device_id = body.get('device_id',None)
    print(device_id)    
    if device_id is not None:
        device = Device.query.filter_by(global_id=device_id).first()
        application.devices.remove(device)
        db.session.add(application)
        db.session.commit()
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_device = {"type":"app_device","queue":"delete"}
        self_device["content"] = {"app_id":application.global_id,"device_id":device.global_id}
        q.put(json.dumps(self_device))
        #-------------END SDA CODE----------------#
        return make_response(jsonify({"RESULT":"OK"}),200)