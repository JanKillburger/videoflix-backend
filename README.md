# Videoflix Backend

A simple Django backend for
- accepting user-uploaded videos via the Admin panel,
- converting them into multiple resolutions with FFmpeg
- using django-rq for processing in the background.

Processing a video is compute-intensive so it will take a while before the video is available on the frontend.

Video format is HLS. Capable browsers/video players will select the appropriate resolution/quality based on the available bandwidth.

## Installation

### General setup

- Rename '.sample-env' file to '.env'
- populate it with actual values
- double-check it is included in the .gitignore file

### Development environment

The repository contains a Docker container setup to run the application locally. This requires Docker to be installed. Then you can run `docker compose up --build` at the command prompt within the project folder to build and run the setup:

- Nginx web server
- Django app served with gunicorn
- background tasks in a dedicated container
- PostgreSQL
- Redis Server

After first start of docker:
- `docker exec -it videoflix-backend-app-1 bash`
- within the container:
    - `python3 manage.py makemigrations`
    - `python3 manage.py migrate`
    - `python3 manage.py createsuperuser`: follow the instructions to create an admin user

Open your browser at "http://127.0.0.1/admin" to access the Admin panel and login with the user you just created.

### Production environment

You may choose any setup but in addition to what is listed in the requirements.txt file, you will need the following:
- Postgres database
- Redis server
- FFmpeg
- Nginx

### Test coverage

Test coverage is calculated by the coverage package. You can run it as follows:
- run `coverage run --source='.' manage.py test videoflix` to execute the tests
- run `coverage report` to see test coverage results