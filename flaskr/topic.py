from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)



from auth import login_required
from models import Topic,Device
from  persistence import Persistence
from flask import request
from app import db

bp = Blueprint('topic', __name__, url_prefix='/topic')



@bp.route('/')
@login_required
def topic_index():
    """ Topics Index Section"""
    topics = Topic.query.all()
    return render_template('topics/topics_index.html', topics=topics)


@bp.route('/<int:id>/view', methods=['GET'])
@login_required
def topic_view(id):
    """ Topic View Section"""
    topic = Topic.query.filter_by(id=id).first()
    devices = Device.query.with_parent(topic)
    return render_template('topics/topic_detail.html', topic=topic,devices=devices)



#Create Topic
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create_topic():
    """View for create topic"""
    if request.method == 'POST':

        topic_s = request.form['topic']
        error = None

        if not topic_s:
            error = 'No mandatory property is set.'
        else:
            topic = Topic.query.filter_by(topic=topic_s).first()
            if topic is not None:
                error = "The topic is already exist."      

        if error is not None:
            flash(error)
        else:            
            try:
                topic = Topic(topic=topic_s)
                db.session.add(topic)
                db.session.commit()
                return redirect(url_for('topic.topic_index'))

            except OSError as e:
                flash("Creation of the directory %s failed" % tag)
            except Exception as e:
                print(e)
                flash("DB Creation Failed")

    return render_template('topics/create.html')



#Delete Topic
@bp.route('/delete_topic/<int:id>', methods=['GET','POST'])
@login_required
def delete_topic(id):
    topic = Topic.query.filter_by(id=id).first()
    if topic is not None:
        if request.method == 'POST':
            try:
                devices = Device.query.with_parent(topic)
                for device in devices:
                    print(topic.topic)
                    delete = Persistence().delete_device_topic(device,topic)
                    if not delete:
                        flash("Problems deleting topic from the device")
                        return render_template('topics/delete.html',device=device)

                #Delete the database register
                db.session.delete(topic)
                db.session.commit()
                flash("The topic was removed")
                return redirect(url_for('topic.topic_index'))

            except Exception as e:
                print(e)
                flash("DB Deleted Failed - %s".format(e))
    else:
        flash("Topic Not Found")

    return render_template('topics/delete.html',topic=topic)