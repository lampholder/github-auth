import os
from sys import stderr

from requests_oauthlib import OAuth2Session

from flask import Flask, request, redirect, session, url_for, make_response
from flask.json import jsonify

from waitress import serve

CLIENT_ID = os.environ['GITHUB_CLIENT_KEY']
CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']

LOGIN_PATH = os.environ.get('PATH_LOGIN', '/login')
CALLBACK_PATH = os.environ.get('PATH_CALLBACK', '/callback')

SCOPES = [scope.strip() for scope in os.environ.get('SCOPES', '').split(',')]

FLASK_SECRET_KEY = os.environ['FLASK_SECRET_KEY']

GITHUB_TOKEN_COOKIE = os.environ.get('GITHUB_TOKEN_COOKIE', 'github_token')
GITHUB_LOGIN_COOKIE = os.environ.get('GITHUB_LOGIN_COOKIE', 'github_login')

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = os.environ.get('PORT', 5000)

AUTHORIZATION_BASE_URL = 'https://github.com/login/oauth/authorize'
TOKEN_URL = 'https://github.com/login/oauth/access_token'
USER_URL = 'https://api.github.com/user'

app = Flask(__name__)
app.secret_key = str.encode(FLASK_SECRET_KEY)

@app.route(LOGIN_PATH)
def login():
    scopes = SCOPES
    github = OAuth2Session(CLIENT_ID, scope=scopes)
    authorization_url, state = github.authorization_url(AUTHORIZATION_BASE_URL)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    if request.args.get('target_url'):
        print('Setting target_url to %s' % request.args.get('target_url'), file=stderr)
        session['target_url'] = request.args.get('target_url')
    elif session.get('target_url'):
        del session['target_url']

    return redirect(authorization_url)

@app.route(CALLBACK_PATH)
def callback():
    github = OAuth2Session(CLIENT_ID, state=session['oauth_state'])
    token = github.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET,
                               authorization_response=request.url)

    user = github.get(USER_URL).json()

    print('Target url redirect to %s' % session.get('target_url'), file=stderr)
    response = make_response(redirect(session.get('target_url', '/'), 302))
    response.set_cookie(GITHUB_TOKEN_COOKIE, token.get('access_token'))
    response.set_cookie(GITHUB_LOGIN_COOKIE, user.get('login'))
    return response

serve(app, host=HOST, port=PORT)
