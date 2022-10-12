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
"""This module contains the library."""
import configparser
import logging.config

import uvicorn  # type: ignore
from fastapi import FastAPI

from ._version import __name_soft__
from .config import openapi_config
from .initializer import init

logger = logging.getLogger(__name__)


class PlanetCrsRegistryLib:
    """The library"""

    def __init__(self, path_to_conf: str, *args, **kwargs):
        # pylint: disable=unused-argument
        if "level" in kwargs:
            PlanetCrsRegistryLib._parse_level(kwargs["level"])

        self.__config = configparser.ConfigParser()
        self.__config.optionxform = str  # type: ignore
        logger.info("Reading the configuration file from %s", path_to_conf)
        self.__config.read(path_to_conf)
        self.__app = FastAPI(
            title=openapi_config.name,
            version=openapi_config.version,
            description=openapi_config.description,
        )

    @staticmethod
    def _parse_level(level: str):
        """Parse level name and set the rigt level for the logger.
        If the level is not known, the INFO level is set

        Args:
            level (str): level name
        """
        logger_main = logging.getLogger(__name_soft__)
        if level == "INFO":
            logger_main.setLevel(logging.INFO)
        elif level == "DEBUG":
            logger_main.setLevel(logging.DEBUG)
        elif level == "WARNING":
            logger_main.setLevel(logging.WARNING)
        elif level == "ERROR":
            logger_main.setLevel(logging.ERROR)
        elif level == "CRITICAL":
            logger_main.setLevel(logging.CRITICAL)
        elif level == "TRACE":
            logger_main.setLevel(logging.TRACE)  # type: ignore # pylint: disable=no-member
        else:
            logger_main.warning(
                "Unknown level name : %s - setting level to INFO", level
            )
            logger_main.setLevel(logging.INFO)

    @property
    def config(self) -> configparser.ConfigParser:
        """The configuration file.

        :getter: Returns the configuration file
        :type: configparser.ConfigParser
        """
        return self.__config

    @property
    def app(self) -> FastAPI:
        """The fast API app.

        :getter: Returns the Fast API app
        :type: FastAPI
        """
        return self.__app

    def start(self):
        """Starts the server."""
        logger.info("Starting application initialization...")
        init(self.app)
        logger.info("Successfully initialized!")
        host: str = self.config["MAIN"]["host"]
        port: int = int(self.__config["MAIN"]["port"])
        uvicorn.run(self.app, host=host, port=port)
