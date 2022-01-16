FROM python:3.7.12-slim-buster

WORKDIR /usr/src/app

EXPOSE 5000

ENV FLASK_ENV=prod
ENV FLASK_APP=app
ENV FLASK_DEBUG=0



RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./flaskr /usr/src/app/

#Gunicorn 
CMD ["gunicorn","--bind","0.0.0.0:5000","wsgi:app"]