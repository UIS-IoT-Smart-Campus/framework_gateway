from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)



from auth import login_required
from models import Topic
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
    return render_template('topics/topic_detail.html', topic=topic)



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