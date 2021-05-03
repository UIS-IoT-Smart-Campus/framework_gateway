from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from auth import login_required
from app import db

bp = Blueprint('index', __name__)


@bp.route('/')
@login_required
def index():
    """ Index de la app"""
    return render_template('index.html')