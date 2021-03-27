from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.models.models import DeviceModel

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    """ Index de la app"""
    devices = DeviceModel.get_all()
    return render_template('index.html', devices=devices)