FROM arm32v7/python:3.7.10-buster

WORKDIR /usr/src/app

EXPOSE 5000

ENV FLASK_ENV=prod
ENV FLASK_APP=app
ENV FLASK_DEBUG=0



RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./flaskr /usr/src/app/

#copy database
RUN mkdir /instance
COPY ./flaskr/db.sqlite3 /usr/src/app/instance/db.sqlite3


#Gunicorn 
CMD ["gunicorn","--bind","0.0.0.0:5000","wsgi:app"]