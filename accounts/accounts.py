import flask
import json
import hmac
import secrets
import urllib.parse
import werkzeug

import db

app = flask.Flask(__name__)
app.config.from_object('config')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db.init_app(app)

JOURNAL_ORIGIN = app.config['JOURNAL_ORIGIN'] # 'https://journal.bitdizzle.xyz'


@app.route('/')
def home():
    if 'accounts_user' not in flask.session:
        return flask.render_template('login.html')
    else:
        return flask.render_template('home.html')


@app.route('/login', methods=['POST'])
def login():
    username = flask.request.form.get('username', '')
    if not username:
        return 'Missing username', 400
    if username == 'admin':
        return 'lol nice try', 403
    flask.session['accounts_user'] = username
    return flask.redirect(flask.url_for('.home'))


@app.route('/logout', methods=['POST'])
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('.home'))


@app.route('/submit_link', methods=['POST'])
def submit_link():
    link = flask.request.form['link']
    if urllib.parse.urlparse(link).scheme not in ('http', 'https'):
        return flask.redirect(flask.url_for('.home', msg='link-invalid'))
    db.create_link(link, flask.session['accounts_user'], flask.request.remote_addr)
    return flask.redirect(flask.url_for('.home', msg='link-thanks'))


@app.route('/oauth_authorize')
def oauth_authorize():
    client_id = flask.request.args.get('client_id', '')
    redirect_uri = flask.request.args.get('redirect_uri', '')

    if client_id != app.config['JOURNAL_CLIENT_ID']:
        return 'Invalid client_id', 400

    # I bet the whole Journal site is safe to redirect to
    if not redirect_uri.startswith(JOURNAL_ORIGIN + '/'):
        return 'Invalid redirect_uri', 400

    if 'accounts_user' not in flask.session:
        return flask.redirect(flask.url_for('.home'))

    code = secrets.token_urlsafe()
    db.create_auth_code(code, flask.session['accounts_user'])

    parsed_redirect_uri = urllib.parse.urlparse(redirect_uri)
    if parsed_redirect_uri.query:
        query = parsed_redirect_uri.query + '&code=' + code
    else:
        query = 'code=' + code
    return flask.redirect(parsed_redirect_uri._replace(query=query).geturl())


@app.route('/oauth_token', methods=['POST'])
def oauth_token():
    code = flask.request.form.get('code', '')
    client_id = flask.request.form.get('client_id', '')
    client_secret = flask.request.form.get('client_secret', '')

    if client_id != app.config['JOURNAL_CLIENT_ID']:
        return 'Incorrect client_id', 401
    if not hmac.compare_digest(client_secret, app.config['JOURNAL_CLIENT_SECRET']):
        return 'Incorrect client_secret', 401

    username = db.get_user_for_code(code)
    if username is None:
        return 'Unrecognized code', 404
    db.mark_code_used(code)
    return {
        'username': username,
    }


if __name__ == '__main__':
    app.run(debug=True, port=8080)
