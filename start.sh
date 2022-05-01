#!/bin/sh

/app/tailscaled --tun=userspace-networking --outbound-http-proxy-listen=localhost:1055 &
/app/tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=heroku-app
echo Tailscale started
cd tweetsforsats
HTTP_PROXY=http://localhost:1055/ gunicorn tweetsforsats.wsgi