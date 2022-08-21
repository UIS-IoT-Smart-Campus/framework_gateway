from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from auth import login_required
from models import Application
import selfconfig as sc
from app import db
from datetime import date

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
@bp.route('/<int:id>/view', methods=['GET'])
@login_required
def application_view(id):
    """ Application View Section"""
    application = Application.query.filter_by(id=id).first()
    return render_template('applications/detail_app.html', application=application)



#Create Application
@bp.route('/create', methods=('GET', 'POST'))
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
                return redirect(url_for('applications.applications_index'))
           
            except Exception as e:
                flash("DB Creation Failed")

    return render_template('applications/create_app.html')


#Edit Application
@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
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
                flash("The Application was removed")
                return redirect(url_for('applications.applications_index'))

            except Exception as e:
                print(e)
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Application Not Found")

    return render_template('applications/delete_app.html',application=application)