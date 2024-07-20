FROM python:3
ENV PYTHONUNBUFFERED=1
ENV DJANGO_DEVELOPMENT='true'
WORKDIR /django
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt update && apt install ffmpeg -y
COPY . .
RUN python3 manage.py collectstatic --noinput
