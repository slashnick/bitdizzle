import flask
import json
import requests
import secrets
import urllib.parse
import traceback

import db

app = flask.Flask(__name__)
app.config.from_object('config')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db.init_app(app)

ACCOUNTS_ORIGIN = app.config['ACCOUNTS_ORIGIN'] # 'https://accounts.bitdizzle.xyz'
OAUTH_CLIENT_ID = app.config['JOURNAL_CLIENT_ID']
OAUTH_CLIENT_SECRET = app.config['JOURNAL_CLIENT_SECRET']


@app.route('/')
def journal_home():
    username = flask.session.get('journal_user')
    if not username:
        return flask.redirect(ACCOUNTS_ORIGIN + '/')

    entries = db.get_entries(username)

    return ('''\
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>BitDizzle Journal</title>
    <link rel="stylesheet" href="/static/main.css">
  </head>
  <body>
    <div id="root"></div>
    <script src="https://unpkg.com/react@18.2.0/umd/react.production.min.js" integrity="sha384-tMH8h3BGESGckSAVGZ82T9n90ztNXxvdwvdM6UoR56cYcf+0iGXBliJ29D+wZ/x8" crossorigin="anonymous"></script>
    <script src="https://unpkg.com/react-dom@18.2.0/umd/react-dom.production.min.js" integrity="sha384-bm7MnzvK++ykSwVJ2tynSE5TRdN+xL418osEVF2DE/L/gfWHj91J2Sphe582B1Bh" crossorigin="anonymous"></script>
    <script>window.initialProps = '''
    # Eh, seems fine. JSON will escape this data, right?
    + json.dumps({'entries': entries})
    + ''';</script>
    <script src="/static/app.js"></script>
  </body>
</html>
''')


@app.route('/entries/', methods=['POST'])
def create_entry():
    if flask.session['journal_user'] is None:
        return 'Unauthorized', 401
    entry = flask.request.get_json()
    title, body = entry['title'], entry['body']
    db.create_entry(flask.session['journal_user'], title, body)
    return '', 204


@app.route('/entries/', methods=['DELETE'])
def delete_all_entries():
    if flask.session['journal_user'] is None:
        return 'Unauthorized', 401
    db.delete_all_entries(flask.session['journal_user'])
    return '', 204


@app.route('/oauth_callback')
def oauth_callback():
    code = flask.request.args.get('code', '')

    token_response = None
    try:
        token_response = requests.post(
            ACCOUNTS_ORIGIN + '/oauth_token',
            data={
                'client_id': OAUTH_CLIENT_ID,
                'client_secret': OAUTH_CLIENT_SECRET,
                'code': code,
            },
            timeout=1,
        )
        if token_response.status_code == 404:
            return 'Invalid code', 400
        token_response.raise_for_status()
    except:
        if token_response is not None:
            print('Error fetching token:', token_response.status_code, token_response.text)
        traceback.print_exc()
        return "O_O Couldn't talk to the accounts server. Consider messaging the organizers", 503

    username = token_response.json()['username']
    if username is None:
        return 'Invalid code', 400

    flask.session['journal_user'] = username
    return flask.redirect('/')



if __name__ == '__main__':
    app.run(debug=True, port=8081)
