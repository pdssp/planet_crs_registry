# -*- coding: utf-8 -*-
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
"""Some vars"""
from os import environ

IS_TEST = bool(environ.get("API_TEST"))
SMTP_HOST = environ.get("SMTP_HOST", "localhost")
SMTP_PORT = int(environ.get("SMTP_PORT", 25))
SMTP_LOGIN = environ.get("SMTP_LOGIN", None)
SMTP_PASSWD = environ.get("SMTP_PASSWD", None)
CONTACT_EMAIL = "jean-christophe.malapert@cnes.fr"
