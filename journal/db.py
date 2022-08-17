import flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.Index(username, id),
    )


def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def create_entry(username, title, body):
    if username == 'admin':
        raise Exception('Not supported for the admin')
    db.session.add(JournalEntry(username=username, title=title, body=body))
    db.session.commit()


def delete_all_entries(username):
    db.session.query(JournalEntry).filter_by(username=username).delete()
    db.session.commit()


def get_entries(username):
    if username == 'admin':
        return [
            {
                'title': 'Flag',
                'body': flask.current_app.config['FLAG'],
            },
        ]

    entries = JournalEntry.query \
        .filter_by(username=username) \
        .order_by(JournalEntry.id.desc()) \
        .all()
    return [
        {
            'title': entry.title,
            'body': entry.body,
        } for entry in entries
    ] + [
        {
            'title': 'Hello World',
            'body': 'This new Jounal site is great! It seems like the perfect ' \
                    'place to write down all my deepest secrets.',
        },
    ]
