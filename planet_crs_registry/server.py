# -*- coding: utf-8 -*-
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
"""Server."""
import argparse
import asyncio
import configparser
import logging
import os
import signal
from multiprocessing import Process
from typing import List

from .planet_crs_registry import PlanetCrsRegistryLib
from planet_crs_registry import __author__  # pylint: disable=C0411
from planet_crs_registry import __copyright__  # pylint: disable=C0411
from planet_crs_registry import __description__  # pylint: disable=C0411
from planet_crs_registry import __version__  # pylint: disable=C0411
from planet_crs_registry.core.business import (  # pylint: disable=C0411
    SqlDatabase,
)  # pylint: disable=C0411

logger = logging.getLogger(__name__)


class SmartFormatter(argparse.HelpFormatter):
    """Smart formatter for argparse - The lines are split for long text"""

    def _split_lines(self, text, width):
        if text.startswith("R|"):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def str2bool(string_to_test: str) -> bool:
    """Checks if a given string is a boolean

    Args:
        string_to_test (str): string to test

    Returns:
        bool: True when the string is a boolean otherwise False
    """
    return string_to_test.lower() in ("yes", "true", "True", "t", "1")


def parse_cli() -> argparse.Namespace:
    """Parse command line inputs.

    Returns
    -------
    argparse.Namespace
        Command line options
    """
    path_to_file = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser(
        description=__description__,
        formatter_class=SmartFormatter,
        epilog=__author__ + " - " + __copyright__,
    )

    parser.register("type", "bool", str2bool)  # add type keyword to registries

    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    parser.add_argument(
        "--conf_file",
        default=os.path.join(path_to_file, "conf/planet_crs_registry.conf"),
        help="The location of the configuration file (default: %(default)s)",
    )

    parser.add_argument(
        "--level",
        choices=[
            "INFO",
            "DEBUG",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "TRACE",
        ],
        default="INFO",
        help="set Level log (default: %(default)s)",
    )

    parser.add_argument(
        "--use_cache",
        type="bool",  # type: ignore
        choices=[True, False],
        default=True,
        help="Use the created WKT database if True (default: %(default)s)",
    )
    return parser.parse_args()


class SigintHandler:  # pylint: disable=too-few-public-methods
    """Handles the signal"""

    def __init__(self):
        self.__signint = False  # pylint: disable=invalid-name
        self.__process: List[Process] = list()

    @property
    def sigint(self) -> bool:
        """Check if signal has been activated.

        :getter: Returns the signal
        :type: boolean
        """
        return self.__signint

    @property
    def process(self) -> List[Process]:
        """The list of process (http & https).

        :getter: Returns the list of processes.
        :type: List[Process]
        """
        return self.__process

    def add_process(self, process: Process):
        """Add a new process

        Args:
            process (Process): object represent activity that is run in a separate process
        """
        self.__process.append(process)

    def signal_handler(self, sig: int, frame):
        """Trap the signal
        Args:
            sig (int): the signal number
            frame: the current stack frame
        """
        # pylint: disable=unused-argument
        logging.error("You pressed Ctrl+C")
        for process in self.process:
            process.terminate()
            process.join()
        self.__signint = True


class Server:
    """Server."""

    def __init__(self, options_cli: argparse.Namespace):
        """Init.

        Args:
            options_cli (argparse.Namespace): configuration file
        """
        logger.info("*** Welcome to Planet Crs Registry ***")
        self.__options_cli = options_cli
        self.__planet_crs_registry = PlanetCrsRegistryLib(
            options_cli.conf_file,
            level=options_cli.level,
        )
        self.__config = configparser.ConfigParser()
        self.__config.optionxform = str  # type: ignore
        self.__config.read(os.path.abspath(options_cli.conf_file))
        self.__handler = SigintHandler()
        signal.signal(signal.SIGINT, self.handler.signal_handler)

    @property
    def planet_crs_registry(self) -> PlanetCrsRegistryLib:
        """The PlanetCrsRegistryLib.

        :getter: Returns the PlanetCrsRegistryLib
        :type: PlanetCrsRegistryLib
        """
        return self.__planet_crs_registry

    @property
    def options_cli(self) -> argparse.Namespace:
        """The options of the command line.

        :getter: Returns the argparse.Namespace
        :type: argparse.Namespace
        """
        return self.__options_cli

    @property
    def config(self) -> configparser.ConfigParser:
        """The ConfigParser.

        :getter: Returns the ConfigParser
        :type: configparser.ConfigParser
        """
        return self.__config

    @property
    def handler(self) -> SigintHandler:
        """The Signal Handler.

        :getter: Returns the SigintHandler
        :type: SigintHandler
        """
        return self.__handler

    @staticmethod
    def __run_http(planet_crs_registry: PlanetCrsRegistryLib):
        """Main function that instantiates the library with http."""
        logger.info("Starting Planet Crs Registry with http")
        planet_crs_registry.start_http()

    @staticmethod
    def __run_https(planet_crs_registry: PlanetCrsRegistryLib):
        """Main function that instantiates the library with https."""
        logger.info("Starting Planet Crs Registry with https")
        planet_crs_registry.start_https()

    def handle_cache(self):
        """Handle the cache of the SQL lite database."""
        sql_db = SqlDatabase()
        if os.path.exists(sql_db.db_path):
            if self.options_cli.use_cache:
                logger.info(  # pylint: disable=W1203
                    f"Using cache: {sql_db.db_path}"
                )  # pylint: disable=W1203
            else:
                logger.info(  # pylint: disable=W1203
                    f"removing {sql_db.db_path}"
                )  # pylint: disable=W1203
                os.remove(sql_db.db_path)
                asyncio.run(sql_db.create_db())
        else:
            asyncio.run(sql_db.create_db())

    def __start_http(self):
        """Run http as a process"""
        http_process: Process = Process(
            target=Server.__run_http, args=(self.planet_crs_registry,)
        )
        http_process.start()
        self.handler.add_process(http_process)

    def __start_https(self):
        """Run https as a process"""
        https_process: Process = Process(
            target=Server.__run_https, args=(self.planet_crs_registry,)
        )
        https_process.start()
        self.handler.add_process(https_process)

    def start(self):
        """Starts the server."""
        try:
            self.handle_cache()
            if "HTTP" in self.config and "HTTPS" in self.config:
                self.__start_http()
                self.__start_https()
            elif "HTTP" in self.config:
                self.__start_http()
            elif "HTTPS" in self.config:
                self.__start_https()
            else:
                raise Exception("Unknown protocol to start the server")
        except Exception as error:  # pylint: disable=broad-except
            logging.exception(error)

    def stop(self):
        """Stops the server."""
        for process in self.handler.process:
            process.terminate()
            process.join()
