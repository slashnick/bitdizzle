ACCOUNTS_ORIGIN = 'https://accounts.bitdizzle.xyz'
FLAG = 'ASV{m0re_lik3_N0AUTH_Am_i_r1GhT}'
JOURNAL_CLIENT_ID = 'f45735d5a3b056b6'
JOURNAL_CLIENT_SECRET = 'x8LBrbXVq4ZB0RgM43TTxuto8Y352s-JcSXo8xsk2xc'
# Flask uses this for session cookie signing
SECRET_KEY = 'o8ZCRzePe36kZFUh1cD-4eA0LeZX0gL15yqTr06D4Uw'
SESSION_COOKIE_NAME = '__Host-session'
SESSION_COOKIE_SECURE = True
SQLALCHEMY_DATABASE_URI = 'sqlite:////var/ctf/db/journal.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Enable these for local development
#ACCOUNTS_ORIGIN = 'http://accounts.localhost:8080'
#SESSION_COOKIE_DOMAIN = 'journal.localhost'
#SESSION_COOKIE_NAME = 'journal_session'
#SESSION_COOKIE_SECURE = False
#SQLALCHEMY_DATABASE_URI = 'sqlite:///../journal.sqlite'
