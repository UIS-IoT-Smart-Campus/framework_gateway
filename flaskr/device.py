from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('device', __name__)



@bp.route('/')
def index():
    """ Index de la app"""
    db = get_db()
    devices = db.execute(
        'SELECT p.id, tagGlobal, device_name, device_description'
        ' FROM device p'
        ' ORDER BY device_name DESC'
    ).fetchall()
    return render_template('device/index.html', devices=devices)



@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """View for create devices"""
    if request.method == 'POST':
        tag = request.form['tag']
        name = request.form['name']
        description = request.form['description']
        error = None

        if not tag:
            error = 'Tag is required.'
        else:
            print(tag)
            db = get_db()
            tag_repeated = db.execute(
                'SELECT tagGlobal'
                ' FROM device'
                ' WHERE tagGlobal == ?',(tag,)
            ).fetchone()

            if tag_repeated is not None:
                error = "The tag is already exist."
        
        if not name:
            error = "Name is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO device (tagGlobal, device_name, device_description)'
                ' VALUES (?, ?, ?)',
                (tag, name, description)
            )
            db.commit()
            return redirect(url_for('device.index'))

    return render_template('device/create.html')