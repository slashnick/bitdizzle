from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class AuthorizationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text, unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    username = db.Column(db.Text, nullable=False)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.Text, nullable=False)
    is_visited = db.Column(db.Boolean, default=False, nullable=False)


def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def create_auth_code(code, username):
    db.session.add(AuthorizationCode(code=code, username=username))
    db.session.commit()


def get_user_for_code(code):
    auth_code = AuthorizationCode.query.filter_by(code=code, is_used=False).one_or_none()
    if auth_code is not None:
        return auth_code.username
    else:
        return None


def mark_code_used(code):
    auth_code = AuthorizationCode.query.filter_by(code=code).one_or_none()
    if auth_code:
        auth_code.is_used = True
        db.session.add(auth_code)
        db.session.commit()


def create_link(link, username, ip_address):
    db.session.add(Link(link=link, username=username, ip_address=ip_address))
    db.session.commit()
