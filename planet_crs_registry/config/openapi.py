# -*- coding: utf-8 -*-
# Planet CRS Registry - The coordinates reference system registry for solar bodies
# Copyright (C) 2021-2022 - CNES (Jean-Christophe Malapert for PDSSP)
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
"""OpenAPI-schema"""
from .._version import __description__
from .._version import __title__
from .._version import __version__
from .base import BaseSettings

OPENAPI_API_NAME = __title__
OPENAPI_API_VERSION = __version__
OPENAPI_API_DESCRIPTION = __description__


class OpenAPISettings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Open API settings."""

    name: str
    version: str
    description: str

    @classmethod
    def generate(cls):
        """Generate the settings of the OpenAPI

        Returns:
            OpenAPISettings: the settings of the OpenAPI
        """
        return OpenAPISettings(
            name=OPENAPI_API_NAME,
            version=OPENAPI_API_VERSION,
            description=OPENAPI_API_DESCRIPTION,
        )
