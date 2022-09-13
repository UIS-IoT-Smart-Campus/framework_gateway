from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from auth import login_required
import selfconfig as sc
from models import Device,Resource, Property
from datetime import date
from app import db
from redisTool import RedisQueue
import json
from flask import jsonify,make_response

bp = Blueprint('resource', __name__, url_prefix='/resources')


#Delete Resource
def delete_resource_method(resource):
    properties = Property.query.filter_by(prop_type="RESOURCE",parent_id=resource.id)
    for property in properties:
        db.session.delete(property)
        #-------------SDA CODE--------------------#
        q = RedisQueue('register')
        self_prop = {"type":"property","queue":"delete"}
        self_prop["content"] = property.complete_serializable
        q.put(json.dumps(self_prop))
        #-------------END SDA CODE--------------------#
    db.session.delete(resource)
    db.session.commit()
    #-------------SDA CODE--------------------#
    q = RedisQueue('register')
    self_resource= {"type":"resource","queue":"delete"}
    self_resource["content"] = resource.light_serializable
    q.put(json.dumps(self_resource))
    #-------------END SDA CODE--------------------#


#Index
@bp.route('/')
@login_required
def resources_index():
    """ Resources Index Section"""
    resources = Resource.query.all()
    settings = sc.get_config_values()
    return render_template('resources/resource_index.html', resources=resources,settings=settings)



#Resource Detail View
@bp.route('/view/<int:id>', methods=['GET'])
@login_required
def resource_view(id):
    """ Resource View Section"""
    resource = Resource.query.filter_by(id=id).first()
    properties = Property.query.filter_by(prop_type="RESOURCE",parent_id=resource.id)
    return render_template('resources/detail_view.html', resource=resource,properties=properties)


#Create Resource
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_resource():
    """View for create resource"""
    if request.method == 'POST':

        name = request.form['name']
        description = request.form.get('description',None)
        resource_type = request.form.get('type',None)    
        create_at = date.today()
        error = None

        if not name or not resource_type:
            error = 'No mandatory property is set.'     

        if error is not None:
            flash(error)
        else:            
            try:
                resources = Resource.query.all()
                if len(resources)!=0:
                    g_id = resources[len(resources)-1].id+1
                else:
                    g_id = 1
                resource = Resource(global_id = g_id, name=name, description=description, resource_type=resource_type, create_at=create_at)
                db.session.add(resource)
                db.session.commit()
                #-----------SDA CODE--------------------#
                q = RedisQueue('register')
                self_resource = {"type":"resource","queue":"create"}
                self_resource["content"] = resource.light_serializable
                q.put(json.dumps(self_resource))
                #-------------END SDA CODE--------------------#           
                return redirect(url_for('resource.resources_index'))
           
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('resources/create.html')



#Update Resource
@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_resource(id):
    resource = Resource.query.filter_by(id=id).first()
    if resource is not None:

        """View for update Resources"""
        if request.method == 'POST':

            name = request.form['name']
            description = request.form.get('description',None)
            resource_type = request.form.get('type',None)
            error = None

            if not name or not resource_type:
                error = 'No mandatory property is set.'

            if error is not None:
                flash(error)        
                       
            try:
                resource.name = name
                resource.description = description
                resource.resource_type = resource_type
                db.session.add(resource)
                db.session.commit()
                #-----------SDA CODE--------------------#
                q = RedisQueue('register')
                self_resource = {"type":"resource","queue":"update"}
                self_resource["content"] = resource.light_serializable
                q.put(json.dumps(self_resource))
                #-------------END SDA CODE--------------------#   

                return redirect(url_for('resource.resource_view',id = resource.id))

            except Exception as e:
                print(e)
                flash("DB Update Failed")
    else:
        flash("Resource Not Found")

    return render_template('resources/update.html',resource=resource)



#Delete Resource
@bp.route('/delete/<int:id>', methods=['GET','POST'])
@login_required
def delete_resource(id):
    resource = Resource.query.filter_by(id=id).first()
    if resource is not None:
        if request.method == 'POST':
            try:                
                delete_resource_method(resource)             
                flash("The Resource was removed")
                return redirect(url_for('resource.resources_index'))

            except Exception as e:
                print(e)
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Resource Not Found")

    return render_template('resources/delete.html',resource=resource)



#Create Property Resource
@bp.route('/add_property/<int:id>', methods=['POST'])
@login_required
def create_property(id):
    resource = Resource.query.filter_by(id=id).first()
    """View for create properties"""
    if request.method == 'POST':

        p_name = request.form['name']
        p_value = request.form['value']
        p_description = request.form['description']
        resource_id = resource.id
        global_id = request.get('global_id',None)
        if not global_id:
            properties = db.session.query(Property).all()
            if len(properties)>0:
                global_id = properties[-1].id+1
            else:
                global_id = 1

        error = None

        if not p_name or not p_value:
            error = 'No mandatory property is set.'

        if error is not None:
            flash(error)
        else:            
            try:
                property_d = Property(name=p_name, value=p_value, description=p_description,prop_type="RESOURCE" ,parent_id=resource_id)
                db.session.add(property_d)
                db.session.commit()
                #-------------SDA CODE--------------------#
                q = RedisQueue('register')
                self_prop = {"type":"property","queue":"create"}
                self_prop["content"] = property_d.complete_serializable
                q.put(json.dumps(self_prop))
                #-------------END SDA CODE----------------#
                return redirect(url_for('resource.resource_view',id=resource.id))
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('resources/add_property.html',resource=resource)



#Delete Property
@bp.route('/delete_property/<int:id>', methods=['POST'])
@login_required
def delete_property(id):
    property_d = Property.query.filter_by(id=id).first()
    if property_d is not None:
        if request.method == 'POST':
            resource_id = property_d.resource_id
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
                return redirect(url_for('resource.resource_view',id=resource_id))

            except Exception as e:
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Device Not Found")

    return render_template('resources/delete_property.html',property=property_d)


"""------------------------------------------------------------------
Rest API Methods
-----------------------------------------------------------------"""

#########################
# RESOURCE API REST #####
########################

#Get all Resources
@bp.route('/api/', methods=["GET"])
def get_resources_api():
    return jsonify(resources=[i.serialize for i in Resource.query.all()])

#Get specific Resource by id
@bp.route('/api/<id>/', methods=["GET"])
def get_resource_by_id(id):
    resource = Resource.query.filter_by(id=id).first()
    if resource is not None:
        return jsonify(resource.serialize)
    else:
        error={"error":"Not resource found"}
        return make_response(jsonify(error),400)


#Create a Resource
@bp.route('/api/', methods=["POST"])
def add_resource_api():
    body = request.get_json()
    if 'name' not in body or 'resource_type' not in body:
        error = {"Error":"No mandatory property is set."}
        return make_response(jsonify(error),400)
    else:
        name = body['name']
        resource_type = body['resource_type']        
        description = body.get('description',None) 
        global_id = body.get('global_id',None)
        if not global_id:
            resources = db.session.query(Resource).all()
            if len(resources)>0:
                global_id = resources[-1].id+1
            else:
                global_id = 1


        resource = Resource(name=name,description=description,resource_type=resource_type,global_id=global_id)
        db.session.add(resource)
        db.session.commit()       
        #-----------SDA CODE--------------------#
        q = RedisQueue('register')
        self_resource = {"type":"resource","queue":"create"}
        self_resource["content"] = resource.light_serializable
        q.put(json.dumps(self_resource))
        #-------------END SDA CODE--------------------#
        return jsonify(resource.serialize)




#Update resource
@bp.route('/api/<id>/', methods=["PUT"])
def update_resource_api(id):
    resource = Resource.query.filter_by(id=id).first()
    
    if resource is not None:
        body = request.get_json()
        
        #Get properties from request
        name = body.get('name',None)
        description = body.get('description',None)
        resource_type = body.get('resource_type',None)
        global_id = body.get('global_id',None)


        #Set properties to model
        if name:
            resource.name = name
        if description:
            resource.description = description
        if resource_type:
            resource.resource_type = resource_type
        if global_id:
            resource.global_id = global_id
                
        db.session.add(resource)
        db.session.commit()
        #-----------SDA CODE--------------------#
        q = RedisQueue('register')
        self_resource = {"type":"resource","queue":"update"}
        self_resource["content"] = resource.light_serializable
        q.put(json.dumps(self_resource))
        #-------------END SDA CODE--------------------#
        return make_response(jsonify(resource.serialize),200)

    else:
        error = {"Error":"The device doesn't exist."}
        return make_response(jsonify(error),400)


#Delete Resource
@bp.route('/api/<id>/', methods=["DELETE"])
def delete_resource_api(id):
    resource = Resource.query.filter_by(id=id).first()
    try:
        delete_resource_method(resource)
        return make_response(jsonify({"Delete":"The resource was remove"}),200)

    except Exception as e:
        error = {"Error":"It's not possible to delete the device"}
        return make_response(jsonify(error),400)

#Delete Resource
@bp.route('/api/global/<global_id>/', methods=["DELETE"])
def delete_global_resource_api(global_id):
    resource = Resource.query.filter_by(global_id=global_id).first()
    try:
        delete_resource_method(resource)
        return make_response(jsonify({"Delete":"The resource was remove"}),200)

    except Exception as e:
        error = {"Error":"It's not possible to delete the device"}
        return make_response(jsonify(error),400)

"""----------------------------------------------------------------------------------------------
#########################
# REMOTE ADMIN PROPERTIES API REST #####
########################
--------------------------------------------------------------------------------------------"""


#Create Resource Property
@bp.route('/property/create/api/<int:resource_id>/', methods=["POST"])
def create_resource_property(resource_id):

    resource = Resource.query.filter_by(id=resource_id).first()
    if not resource:
        error = {"Error":"No resource exist."}
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
    
    property_d = Property(name=name, value=value, prop_type="RESOURCE",parent_id=resource.id,global_id=global_id)
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