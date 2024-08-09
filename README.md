# Videoflix Backend

A simple Django backend for accepting user-uploaded videos via the Admin panel, converting them into multiple resolutions with FFmpeg using django-rq for processing in the background.
Processing a video is compute-intensive so it will take a while before the video is available on the frontend.
Video format is HLS. Capable browsers/video players will select the appropriate resolution/quality based on the available bandwidth.

## Installation

This project uses dotenv for providing environment variables. The provided '.sample-env' file contains the required environment variables. Rename the file to '.env', populate it with actual values and make sure it is EXCLUDED from your repository to prevent leaking sensitive information. The provided .gitignore file already contains an entry to ignore the .env file so it should be excluded by default after renaming it.

### Development environment

The repository contains a Docker container setup to run the application locally. This requires Docker to be installed. Then you can run `docker compose up --build` at the command prompt within the project folder to build and run the setup:

- Nginx web server
- Django app served with gunicorn
- background tasks in a dedicated container
- PostgreSQL
- Redis Server

