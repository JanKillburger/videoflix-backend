FROM python:3
RUN apt update && apt install ffmpeg -y
ENV PYTHONUNBUFFERED=1
WORKDIR /django
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DJANGO_DEVELOPMENT='true'
RUN python3 manage.py collectstatic --noinput
