# unfbackup

[![GitHub Releases](https://img.shields.io/github/v/release/octivi/unfbackup?sort=semver)](https://github.com/octivi/unfbackup/releases)
[![License: MIT](https://img.shields.io/github/license/octivi/unfbackup)](https://choosealicense.com/licenses/mit/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org/)
[![Semantic Versioning](https://img.shields.io/badge/SemVer-2.0.0-blue)](https://semver.org/spec/v2.0.0.html)

`unfbackup` is a small Python tool that logs in to a UniFi OS controller, downloads the controller
backup file, and stores it in a destination directory.

It can be run directly with Python, in Docker, through Docker Compose, or from a systemd timer. On
success it prints the saved backup path.

## Tested Versions

The script has been tested on CloudKey Gen 2 with:

- UniFi OS UCK G2: `5.0.16`
- UniFi Network: `10.3.58`
- InnerSpace: `1.3.14`

## Quick Start

The configured UniFi OS user must have the `Super Admin` role. Accounts with lower privileges cannot
create and download the controller backup.

Create a virtual environment and install dependencies:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Create the destination directory and run one backup:

```sh
mkdir -p backup

UNFBACKUP_USERNAME='user' \
UNFBACKUP_PASSWORD='secret' \
UNFBACKUP_CONTROLLER_URL='https://controller.example.com' \
UNFBACKUP_DEST_DIR="$PWD/backup" \
.venv/bin/python unfbackup.py
```

`UNFBACKUP_CONTROLLER_URL` must be an `https://` URL. The destination directory must already exist.
Backup filenames come from the controller's `Filename` header and are saved with a
`YYYY.MM.DD-HHMMSS-` prefix unless `UNFBACKUP_DEST_FILENAME` is set.

## Configuration

Required variables:

```sh
UNFBACKUP_USERNAME='user'
UNFBACKUP_PASSWORD='secret'
UNFBACKUP_CONTROLLER_URL='https://controller.example.com'
UNFBACKUP_DEST_DIR='/var/backups/unfbackup'
```

Optional variables:

```sh
# UNFBACKUP_DEST_FILENAME='unifi-backup.unf'
UNFBACKUP_ALLOW_INSECURE_TLS='1'
```

Set `UNFBACKUP_DEST_FILENAME` to store the backup under a fixed file name inside
`UNFBACKUP_DEST_DIR`. The value must be a file name, not a path. If it is not set, the script keeps
the timestamped naming behavior.

Set `UNFBACKUP_ALLOW_INSECURE_TLS` to `1`, `true`, or `yes` to ignore TLS certificate verification
errors. This is useful for HTTPS controllers with self-signed certificates, but it lowers connection
security and should only be used when you trust the controller and network path.

You can load variables from `.env` for a single local run:

```sh
(set -a; . ./.env; set +a; .venv/bin/python unfbackup.py)
```

`set -a` exports variables loaded from `.env`, so the Python process can read them from the
environment. The parentheses run the command in a subshell, so those variables do not stay in your
current shell session after the script exits.

## Docker

Build the image:

```sh
docker build -t unfbackup .
```

Run it:

```sh
mkdir -p backup
docker run --rm \
  -e UNFBACKUP_USERNAME='user' \
  -e UNFBACKUP_PASSWORD='secret' \
  -e UNFBACKUP_CONTROLLER_URL='https://controller.example.com' \
  -e UNFBACKUP_DEST_DIR='/backup' \
  -v "$PWD/backup:/backup" \
  unfbackup
```

The container runs as the non-root user `unfbackup` with UID/GID `10001`. The mounted destination
directory must be writable by that UID/GID. You can change the image UID/GID at build time so it
matches the owner of the host backup directory:

```sh
docker build \
  --build-arg UNFBACKUP_UID="$(id -u)" \
  --build-arg UNFBACKUP_GID="$(id -g)" \
  -t unfbackup .
```

## Docker Compose

Create a `.env` file:

```sh
cp .env.example .env
```

Set the controller credentials in `.env`. For Compose, backups are written to `UNFBACKUP_OUTPUT_DIR`
on the host and mounted as `/backup` inside the container.

If you use a bind-mounted host directory, make sure it is writable by the image UID/GID. Setting
ownership for `/backup` in the Dockerfile only affects the image directory; a bind mount replaces it
with the host directory at runtime.

The easiest option is to run the container with your local UID/GID and create the backup directory
as your user. Use numeric values in `.env`; command substitutions such as `$(id -u)` are not
evaluated inside `.env` files.

```sh
mkdir -p backup
printf 'UNFBACKUP_UID=%s\nUNFBACKUP_GID=%s\n' "$(id -u)" "$(id -g)" >> .env
docker compose build
```

Run one backup:

```sh
docker compose run --rm unfbackup
```

Run on a fixed interval as a Compose service:

```sh
docker compose up -d scheduler
docker compose logs -f scheduler
```

The scheduler service runs the same one-shot backup command in a small loop and waits
`UNFBACKUP_INTERVAL` between runs. For production systems where you already have host-level systemd,
the cleaner option is usually to keep scheduling in a systemd timer or host cron and call
`docker compose run --rm unfbackup`. That keeps the application container one-shot and avoids
embedding a cron daemon inside it.

## systemd

The shipped unit files are ready to use with these fixed paths:

- script: `/opt/unfbackup/unfbackup.py`
- virtualenv: `/opt/unfbackup/.venv`
- env file: `/opt/unfbackup/.env`
- service user: `unfbackup`
- backup directory: `/var/backups/unfbackup`

From a source checkout or extracted release package, install for systemd-based hosts:

```sh
id -u unfbackup >/dev/null 2>&1 || sudo useradd --system --home-dir /opt/unfbackup --shell /usr/sbin/nologin unfbackup
sudo install -d -o unfbackup -g unfbackup -m 0755 /opt/unfbackup
sudo install -d -o unfbackup -g unfbackup -m 0700 /var/backups/unfbackup
sudo install -m 0755 unfbackup.py /opt/unfbackup/unfbackup.py
sudo python3 -m venv /opt/unfbackup/.venv
sudo /opt/unfbackup/.venv/bin/pip install -r requirements.txt
sudo install -m 0600 .env.example /opt/unfbackup/.env
sudo chown root:unfbackup /opt/unfbackup/.env
sudo chmod 0640 /opt/unfbackup/.env
sudo install -m 0644 systemd/unfbackup.service /etc/systemd/system/unfbackup.service
sudo install -m 0644 systemd/unfbackup.timer /etc/systemd/system/unfbackup.timer
sudo systemctl daemon-reload
```

Edit `/opt/unfbackup/.env`:

```sh
UNFBACKUP_USERNAME=user
UNFBACKUP_PASSWORD=secret
UNFBACKUP_CONTROLLER_URL=https://controller.example.com
UNFBACKUP_DEST_DIR=/var/backups/unfbackup
# UNFBACKUP_DEST_FILENAME=unifi-backup.unf
# UNFBACKUP_ALLOW_INSECURE_TLS=1
```

Enable the timer:

```sh
sudo systemctl enable --now unfbackup.timer
```

Run once manually:

```sh
sudo systemctl start unfbackup.service
sudo journalctl -u unfbackup.service
```

The difference from an example template is that these unit files contain real installation paths.
They can be copied directly to `/etc/systemd/system/` when the files are installed as shown above.

## Controller API Details

The script uses fixed UniFi OS controller paths:

- login: `POST /api/auth/login`
- download: `GET /api/backup/download`
- logout: `POST /api/auth/logout`
- login body: `{"username":"...","password":"..."}`
- logout CSRF: `X-CSRF-Token` returned by login and sent to the logout request
