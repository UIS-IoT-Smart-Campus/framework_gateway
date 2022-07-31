from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from auth import login_required

from app import db
from models import Device,Resource



bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def add_device(device,nodes,links,parent_node, nodes_count):
    print("device")
    print(device.id)
    print("nodes")
    print(nodes)
    print("links")
    print(links)
    #Agregar nodo dispositivo
    if device.is_gateway:
        node = {"name":device.name,"type":"Gateway"}
    else:
        node = {"name":device.name,"type":"Device"}
    nodes.append(node)

    if device.id != 1:
        nodes_count+=1
        links.append({"source":parent_node,"target":nodes_count})
    
    device_node = nodes_count
    
    #Agregar recursos dispositivo
    resources = Resource.query.filter_by(device_id=device.id)
    for resource in resources:
        #Agregar nodo recurso
        if resource.resource_type == "SENSOR":
            node = {"name":resource.name,"type":"Sensor"}
        else:
            node = {"name":resource.name,"type":"Actuator"}
        nodes.append(node)
        nodes_count+=1
        links.append({"source":device_node,"target":nodes_count})
    devices = Device.query.filter_by(device_parent=device.id)
    for device_s in devices:
        nodes_count = add_device(device_s,nodes,links,device_node,nodes_count)
    return nodes_count


#Index
@bp.route('/')
@login_required
def index():
    """ Dashboard Index Section"""
    nodes = []
    links = []
    nodes_count = 0
    parent_node = 0

    #Add self-node
    #node = {"name":"Gateway","type":"Gateway"}
    #nodes.append(node)

    devices = Device.query.filter_by(device_parent=None)
    for device in devices:
        nodes_count = add_device(device,nodes,links,parent_node,nodes_count) 

    print(nodes_count)           

    return render_template('dashboard/index.html', nodes = nodes, links = links)