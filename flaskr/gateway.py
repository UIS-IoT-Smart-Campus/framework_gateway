from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from auth import login_required
from persistence import Persistence
from app import db

from flask import jsonify
from flask import request
import json
from tinydb import TinyDB, Query

import os

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
        return render_template('gateway/settings.html')