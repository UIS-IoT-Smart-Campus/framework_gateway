FROM python:3.7.12-slim-buster

WORKDIR /usr/src/app

EXPOSE 5000

ENV FLASK_ENV=prod

RUN pip install --upgrade pip
COPY ./requierements.txt /usr/src/app/requierements.txt
RUN pip install -r requierements.txt

COPY . /usr/src/app/

#Gunicorn 
CMD ["gunicorn","--bind","0.0.0.0:5000","run:app"]