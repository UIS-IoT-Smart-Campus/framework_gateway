from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    """ Index de la app"""
    db = get_db()
    devices = db.execute(
        'SELECT p.id, tagGlobal, device_name, device_description'
        ' FROM device p'
        ' ORDER BY device_name DESC'
    ).fetchall()

    return render_template('index.html', devices=devices)