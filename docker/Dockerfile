# Planet CRS Registry - The coordinates reference system registry for solar bodies
# Copyright (C) 2021-2024 - CNES (Jean-Christophe Malapert for PDSSP)
#
# This file is part of Planet CRS Registry.
#
# Planet CRS Registry is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License v3  as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Planet CRS Registry is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License v3  for more details.
#
# You should have received a copy of the GNU Lesser General Public License v3
# along with Planet CRS Registry.  If not, see <https://www.gnu.org/licenses/>.
FROM python:3.10 as python-base

LABEL maintainer="Jean-Christophe Malapert <jean-christophe.malapert@cnes.fr>"

# Runtime distribution filename
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
ARG SMTP_HOST
ARG SMTP_PORT
ARG SMTP_LOGIN
ARG SMTP_PASSWD
ARG SLACK_TOKEN
ARG SLACK_CHANNEL_ID
ARG OTEL_EXPORTER_OTLP_ENDPOINT

ARG DEBIAN_FRONTEND=noninteractive

# Environment variables
ENV API_TEST="True" \
    USE_DOCKER="True" \
    GML_PATH="/planet_crs_registry/data/gml" \
    PATH="${PATH}:/root/.local/bin/"



# Labels (based on http://label-schema.org/rc1/)
LABEL \
    org.label-schema.schema-version="1.0" \
    org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.name="planet_crs_registry" \
    org.label-schema.description="The coordinates reference system registry for solar bodies" \
    org.label-schema.url="https://github.com/pdssp/planet_crs_registry" \
    org.label-schema.vcs-url="https://github.com/pdssp/planet_crs_registry" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vendor="PDSSP" \
    org.label-schema.version=$VERSION

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y \
    software-properties-common apt-transport-https curl git && \
    git clone "https://github.com/pdssp/planet_crs_registry.git"

WORKDIR /planet_crs_registry

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry check && \
    poetry install --no-interaction --no-cache --only=main && \
    mkdir -p /conf && \
    cp planet_crs_registry/conf/planet_crs_registry.conf /conf/


# Expose the http server on 8080
EXPOSE 8080 5000

# Mount config file
VOLUME ["/conf"]

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/ping || exit 1

CMD /planet_crs_registry/.venv/bin/planet_crs_registry --conf_file /conf/planet_crs_registry.conf
