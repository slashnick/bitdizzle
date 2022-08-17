JOURNAL_CLIENT_ID = 'f45735d5a3b056b6'
JOURNAL_CLIENT_SECRET = 'x8LBrbXVq4ZB0RgM43TTxuto8Y352s-JcSXo8xsk2xc'
JOURNAL_ORIGIN = 'https://journal.bitdizzle.xyz'
# Flask uses this for session cookie signing
SECRET_KEY = 'jVNUYswjY1R-6hnwYuPAeJpcPipGkhmReLbXl-Ojmz4'
SESSION_COOKIE_NAME = '__Host-session'
SESSION_COOKIE_SECURE = True
SQLALCHEMY_DATABASE_URI = 'sqlite:////var/ctf/db/accounts.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Enable these for local development
#JOURNAL_ORIGIN = 'http://journal.localhost:8081'
#SESSION_COOKIE_DOMAIN = 'accounts.localhost'
#SESSION_COOKIE_NAME = 'accounts_session'
#SESSION_COOKIE_SECURE = False
#SQLALCHEMY_DATABASE_URI = 'sqlite:///../accounts.sqlite'
