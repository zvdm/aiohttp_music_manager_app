#!/bin/sh

ln -sf /home/mint/PycharmProjects/aiohttp_music_manager_app/nginx.conf /etc/nginx/sites-enabled/nginx.conf

systemctl restart nginx

#/usr/sbin/nginx -g "daemon off;"

gunicorn3 entry:crapp --bind localhost:8000 --worker-class aiohttp.GunicornUVLoopWebWorker

exit 0