# videoflix-backend
A simple backend for accepting user-uploaded videos via the Admin panel, converting them into multiple resolutions with FFmpeg using django-rq for processing in the background.
Processing a video is compute-intensive so it will take a while before the video is available in the frontend.
Video format is HLS. Capable browsers/video players will select the appropriate resolution based on the available bandwidth.