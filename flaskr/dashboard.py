from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from auth import login_required



bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


#Index
@bp.route('/')
@login_required
def index():
    """ Dashboard Index Section"""
    return render_template('dashboard/index.html')