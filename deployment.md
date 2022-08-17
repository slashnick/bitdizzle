# Deployment instructions

I set this up on a Digital Ocean box. Here are the steps I went through:

## Create a droplet

I created an Ubuntu 22.04 droplet in the SFO2 region, with IPv6 enabled.

## DNS

Go to a registrar, buy a domain, and point the NS records to:

* `ns1.digitalocean.com.`
* `ns2.digitalocean.com.`
* `ns3.digitalocean.com.`

Log into Digital Ocean, go to the Networking tab, and create a zone for this
domain.

Add these DNS records:

* `CNAME` `www` -> `@`
* `CNAME` `accounts` -> `@`
* `CNAME` `journal` -> `@`
* `A` `@` -> droplet ip
* `AAAA` `@` -> droplet ip

For good measure, let's restrict CAs and prevent email spoofing:

* `CAA` `@` -> `0 issue "letsencrypt.org"`
* `TXT` `@` -> `v=spf1 -all`
* `TXT` `_dmarc` -> `v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s`

## nginx

Install nginx and certbot

```
sudo apt-get install -y nginx
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Get a TLS cert

```
DOMAIN=bitdizzle.xyz
sudo certbot certonly --nginx --email [my email] --agree-tos --no-eff-email \
 -d $DOMAIN -d www.$DOMAIN -d accounts.$DOMAIN -d journal.$DOMAIN
```

Copy the included `infra/nginx.conf` file to `/etc/nginx/nginx.conf`.

```
sudo nginx -s reload
```

## Headless Chrome + Selenium (for CSRF/XSS "victim")

Install Chrome

```
curl -O https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# This will fail with dependency errors. That's okay
sudo dpkg -i google-chrome-stable_current_amd64.deb
# This will install any dependencies we're missing
sudo apt-get install -y --fix-broken
rm google-chrome-stable_current_amd64.deb
```

Check your Chrome version before proceeding.

```
google-chrome --version
```

## ChromeDriver

Choose a ChromeDriver version. Read the "Current Releases" section of
https://chromedriver.chromium.org/downloads to pick the right one. When I
installed Chrome, I got Chrome 103.x.x.x. As of now, that webpage tells me I
should install ChromeDriver 103.0.5060.53.

(Chrome updates come out often, so you might get a different version)

```
sudo apt-get install -y unzip
curl -O https://chromedriver.storage.googleapis.com/103.0.5060.53/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
rm chromedriver_linux64.zip
sudo chown root:root chromedriver
sudo mv chromedriver /usr/bin/
```

## Python apps & dependencies

```
sudo mkdir /var/ctf
```

- Copy the included directory `accounts` to `/var/ctf/accounts`
- Copy the included directory `journal` to `/var/ctf/journal`
- Copy the included directory `victim` to `/var/ctf/victim`

Set up the directory structure and install Python requirements.

```
sudo apt-get install -y python3-pip
sudo useradd -r -d /nonexistent -s /usr/sbin/nologin app
sudo bash -c "cd /var/www/accounts && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt"
sudo bash -c "cd /var/www/journal && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt"
sudo bash -c "cd /var/www/victim && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt"
sudo mkdir /var/ctf/db
sudo chown app:app /var/ctf/db
```

## uwsgi

```
sudo apt-get install -y uwsgi uwsgi-plugin-python3
sudo ln -s ../apps-available/accounts.ini /etc/uwsgi/apps-enabled/accounts.ini
sudo ln -s ../apps-available/journal.ini /etc/uwsgi/apps-enabled/journal.ini
```

- Copy the included `infra/accounts-uwsgi.ini` to `/etc/uwsgi/apps-available/accounts.ini`
- Copy the included `infra/journal-uwsgi.ini` to `/etc/uwsgi/apps-available/journal.ini`

```
sudo systemctl restart uwsgi
```

## Victim service

Copy the included `infra/victim@.service` file to `/etc/systemd/system/victim@.service`.

Reload systemd, and run 3 process of the Victim service.

```
sudo systemctl daemon-reload
sudo systemctl enable victim@{1..3}
sudo systemctl start victim@{1..3}
```
