# Planet CRS Registry - The coordinates reference system registry for solar bodies
# Copyright (C) 2021 - CNES (Jean-Christophe Malapert for Pôle Surfaces Planétaires)
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
FROM ubuntu:latest

LABEL maintainer="Jean-Christophe Malapert <jean-christophe.malapert@cnes.fr>"

ARG BUILD_DATE
ARG VERSION
ARG DEBIAN_FRONTEND=noninteractive

# Labels (based on http://label-schema.org/rc1/)
LABEL \
    org.label-schema.schema-version="1.0" \
    org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.name="cdm" \
    org.label-schema.description="The coordinates reference system registry for solar bodies" \
    org.label-schema.url="https://github.com/pole-surfaces-planetaires/planet_crs_registry" \
    org.label-schema.vcs-url="https://github.com/pole-surfaces-planetaires/planet_crs_registry" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vendor="Pôle Surfaces Planétaires" \
    org.label-schema.version=$VERSION

RUN apt-get update && \
    apt-get install -y \
    software-properties-common apt-transport-https wget git\
    make python3-pip && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 && \
    pip install setuptools && \
    git clone "https://github.com/pole-surfaces-planetaires/planet_crs_registry.git" && \
    cd planet_crs_registry && \
    make

# Custom prompt
RUN echo 'export PS1="\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;31m\]\u@platoscope-dev\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$"' >> /etc/bash.bashrc

CMD ["planet_crs_registry"]
