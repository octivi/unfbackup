# SPDX-FileCopyrightText: 2026  IMAGIN sp. z o.o.
# SPDX-FileContributor: Marcin Engelmann <mengelmann@octivi.com>
# SPDX-License-Identifier: MIT
#
# This file is part of the unfbackup UniFi OS controller backup tool.
# https://github.com/octivi/unfbackup

FROM python:3-slim

ARG UNFBACKUP_UID=10001
ARG UNFBACKUP_GID=10001

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/unfbackup

RUN groupadd --gid "${UNFBACKUP_GID}" unfbackup \
    && useradd --uid "${UNFBACKUP_UID}" --gid "${UNFBACKUP_GID}" --home-dir /nonexistent --shell /usr/sbin/nologin unfbackup \
    && mkdir -p /backup \
    && chown unfbackup:unfbackup /backup

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY unfbackup.py .
RUN chmod 0755 /opt/unfbackup/unfbackup.py \
    && chown -R unfbackup:unfbackup /opt/unfbackup

USER unfbackup:unfbackup

ENV UNFBACKUP_DEST_DIR=/backup

CMD ["python", "/opt/unfbackup/unfbackup.py"]
