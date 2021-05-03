from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flask import request
from flaskr.persistence import Persistence

from flask import jsonify
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