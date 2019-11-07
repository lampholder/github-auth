# github-auth

Simple service to direct users via GitHub OAuth login and write their GitHub login and access token to a cookie. It is designed to be the one non-static part of an otherwise static application. Most options (everything?) that you would want to change can be configured with environment variables (see `example.env` for hints).

Having made it, I'm surprised it doesn't exist already, which probably means it either _does_ exist already or there's something fundamentally flawed about the idea.

## How it works

This service serves a Python3 Flask app that exposes two endpoints:

- `/login` that directs you via GitHub's OAuth login UX, and
- `/callback` the endpoint that the GitHub app/OAuth flow is configured to return you to after the permission has been granted

`/login` accepts a query param, `?target_url=` which expects a URL-encoded URL, to which the browser will be redirected after `/callback` has been handled.

**EXTREME CAVEAT**

I don't really know what I'm doing with Docker, nginx, OAuth, Flask or waitress, so please take everything in this repo with a big pinch of salt. Friendly feedback is _hugely_ appreciated.

## How I have used this thing I have made.

I've used it alongside another docker container in which an nginx serves a static JS application using the following nginx.conf:

```
# nginx.conf

user  nginx;
worker_processes 1;

error_log  /var/log/nginx/error.log debug;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
        '$status $body_bytes_sent "$http_referer" '
        '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;

    keepalive_timeout  65;

    upstream app {
        server auth:5000;
    }

    server {
        listen 80;
        server_name localhost;
        index index.html;
        charset utf-8;

        root /usr/share/nginx/html;

        location = /_auth {
            return 302 /_auth/;
        }

        location /_auth/ {
            proxy_pass http://app/;
        }

        # Handle noisy favicon.ico messages
        location = /favicon.ico {
            return 204;
            access_log     off;
            log_not_found  off;
        }
    }
}
```
