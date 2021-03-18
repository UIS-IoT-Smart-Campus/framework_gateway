from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('service', __name__, url_prefix='/service')



@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """View for create services"""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None
        
        if not name:
            error = "Name is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO service (service_name, service_description)'
                ' VALUES (?, ?)',
                (name, description)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('service/create.html')