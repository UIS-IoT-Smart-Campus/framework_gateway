from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from auth import login_required

from app import db
from models import Device



bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


#Index
@bp.route('/')
@login_required
def index():
    """ Dashboard Index Section"""
    nodes = []
    links = []
    devices_count = 0

    #Add self-node
    node = {"name":"Gateway","type":"Gateway"}
    nodes.append(node)

    devices = db.session.query(Device).all()
    for device in devices:
        node = {"name":device.name,"type":"Device"}
        nodes.append(node)
        devices_count+=1
        links.append({"source":0,"target":devices_count})        

    return render_template('dashboard/index.html', nodes = nodes, links = links)