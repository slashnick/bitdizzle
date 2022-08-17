import flask
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import sqlite3
import time
import traceback
import types

ACCOUNTS_CONFIG = '/var/ctf/accounts/config.py'
JOURNAL_CONFIG = '/var/ctf/journal/config.py'

ACCOUNTS_DB = '/var/ctf/db/accounts.sqlite'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)-10s %(ip_address)-15s [%(username)s] %(message)s',
)
logger = logging.getLogger(__name__)


def main():
    driver = create_driver()
    con = None
    try:
        con = sqlite3.connect(ACCOUNTS_DB)
        cursor = con.cursor()
        while True:
            # Visit one link per IP each round. If a single IP is submitting
            # lots of links, we'll still visit other people's links.
            result = cursor.execute(
                'update link set is_visited=1 '
                'where id in (select min(id) from link where is_visited=0 group by ip_address) '
                'returning link, username, ip_address'
            )
            links = result.fetchall()
            con.commit()

            if len(links) == 0:
                time.sleep(3)
            else:
                for link, username, ip_address in links:
                    log_extra = {'username': username, 'ip_address': ip_address}
                    visit_csrf_url(link, driver, log_extra)
    finally:
        if con is not None:
            con.close()
        driver.quit()


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    service = Service(executable_path='/usr/bin/chromedriver')
    return webdriver.Chrome(service=service, options=options)


def visit_csrf_url(url, driver, log_extra):
    try:
        logger.info('Visiting {}'.format(url), extra=log_extra)
        driver.set_page_load_timeout(5)
        driver.delete_all_cookies()
        # You have to visit the domain to be able to set cookies
        driver.get('https://accounts.bitdizzle.xyz/404')
        set_flask_session_cookie({'accounts_user': 'admin'}, driver, ACCOUNTS_CONFIG)
        driver.get('https://journal.bitdizzle.xyz/404')
        set_flask_session_cookie({'journal_user': 'admin'}, driver, JOURNAL_CONFIG)

        driver.get(url)
        driver.implicitly_wait(5)
    except Exception as e:
        e_oneline = str(e).split('\n', 1)[0]
        logger.warning('Error: {}'.format(e_oneline), extra=log_extra)


def set_flask_session_cookie(session_dict, driver, flask_config_path):
    # Sign our own session cookie using the SECRET_KEY from an an app's config,
    # and set it
    fake_app = flask.Flask(__name__)
    fake_app.config.from_pyfile(flask_config_path)
    session_interface = fake_app.session_interface
    session_cookie = session_interface.get_signing_serializer(fake_app).dumps(session_dict)
    driver.add_cookie({
        'name': session_interface.get_cookie_name(fake_app),
        'value': session_cookie,
        'path': '/',
        'secure':  session_interface.get_cookie_secure(fake_app),
        'sameSite': 'Lax',
        'httpOnly': True,
    })


if __name__ == '__main__':
    main()
