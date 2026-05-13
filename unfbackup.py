#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026  IMAGIN sp. z o.o.
# SPDX-FileContributor: Marcin Engelmann <mengelmann@octivi.com>
# SPDX-License-Identifier: MIT
#
# This file is part of the unfbackup UniFi OS controller backup tool.
# https://github.com/octivi/unfbackup

import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from urllib3.exceptions import InsecureRequestWarning


TIMEOUT = 60
TRUTHY = {"1", "true", "yes"}


def fail(message):
    print(f"unfbackup: {message}", file=sys.stderr)
    raise SystemExit(1)


def env(name):
    value = os.environ.get(name)
    if not value:
        fail(f"missing required environment variable: {name}")
    return value


def base_url(value):
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        fail("UNFBACKUP_CONTROLLER_URL must be an https:// URL with a host")
    return value.rstrip("/") + "/"


def dest_filename(value):
    if not value:
        return None
    if "/" in value or "\\" in value or value in {".", ".."}:
        fail("UNFBACKUP_DEST_FILENAME must be a file name, not a path")
    return value


def request(session, method, url, **kwargs):
    try:
        response = session.request(method, url, timeout=TIMEOUT, **kwargs)
        response.raise_for_status()
    except requests.RequestException as error:
        fail(f"{method} {url} failed: {error}")
    return response


def main():
    username = env("UNFBACKUP_USERNAME")
    password = env("UNFBACKUP_PASSWORD")
    controller = base_url(env("UNFBACKUP_CONTROLLER_URL"))
    dest_dir = Path(env("UNFBACKUP_DEST_DIR"))
    configured_filename = dest_filename(os.environ.get("UNFBACKUP_DEST_FILENAME", ""))
    verify_tls = os.environ.get("UNFBACKUP_ALLOW_INSECURE_TLS", "").lower() not in TRUTHY

    if not dest_dir.is_dir():
        fail(f"UNFBACKUP_DEST_DIR is not an existing directory: {dest_dir}")

    if not verify_tls:
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    session = requests.Session()
    session.verify = verify_tls

    login = request(
        session,
        "POST",
        urljoin(controller, "api/auth/login"),
        json={"username": username, "password": password},
    )
    csrf_token = login.headers.get("X-CSRF-Token")
    if not csrf_token:
        fail("login response did not include X-CSRF-Token")

    try:
        backup = request(
            session,
            "GET",
            urljoin(controller, "api/backup/download"),
        )

        filename = backup.headers.get("Filename")
        if not filename:
            fail("download response did not include Filename")

        filename = Path(filename).name
        output_filename = configured_filename or f"{datetime.now():%Y.%m.%d-%H%M%S}-{filename}"
        output_path = dest_dir / output_filename
        output_path.write_bytes(backup.content)

        print(output_path)
    finally:
        had_error = sys.exc_info()[0] is not None
        try:
            request(
                session,
                "POST",
                urljoin(controller, "api/auth/logout"),
                headers={"X-CSRF-Token": csrf_token},
            )
        except SystemExit:
            if not had_error:
                raise


if __name__ == "__main__":
    main()
