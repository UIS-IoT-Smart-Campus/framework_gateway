from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from auth import login_required
import selfconfig as sc
from models import Device,Resource, Property
from datetime import date
from app import db

bp = Blueprint('resource', __name__, url_prefix='/resources')

#Index
@bp.route('/')
@login_required
def resources_index():
    """ Resources Index Section"""
    resources = Resource.query.all()
    settings = sc.get_config_values()
    return render_template('resources/resource_index.html', resources=resources,settings=settings)



#Resource Detail View
@bp.route('/<int:id>/view', methods=['GET'])
@login_required
def resource_view(id):
    """ Resource View Section"""
    resource = Resource.query.filter_by(id=id).first()
    properties = Property.query.filter_by(resource_id=id)
    return render_template('resources/detail_view.html', resource=resource,properties=properties)


#Create Resource
@bp.route('/create', methods=('GET', 'POST'))
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
                return redirect(url_for('resource.resources_index'))
           
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('resources/create.html')



#Update Resource
@bp.route('/update/<int:id>', methods=('GET', 'POST'))
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
                db.session.delete(resource)
                db.session.commit()                
                flash("The Resource was removed")
                return redirect(url_for('resource.resources_index'))

            except Exception as e:
                print(e)
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Resource Not Found")

    return render_template('resources/delete.html',resource=resource)



#Create Property Resource
@bp.route('/add_property/<int:id>', methods=('GET', 'POST'))
@login_required
def create_property(id):
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
                return redirect(url_for('resource.resource_view',id=resource.id))
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('resources/add_property.html',resource=resource)



#Delete Property
@bp.route('/delete_property/<int:id>', methods=['GET','POST'])
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
                flash("The property was removed")
                return redirect(url_for('resource.resource_view',id=resource_id))

            except Exception as e:
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Device Not Found")

    return render_template('resources/delete_property.html',property=property_d)