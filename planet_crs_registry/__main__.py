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
"""Main program."""
import argparse
import asyncio
import configparser
import logging
import os
import signal
from multiprocessing import Process
from typing import List

from .planet_crs_registry import PlanetCrsRegistryLib
from planet_crs_registry import __author__
from planet_crs_registry import __copyright__
from planet_crs_registry import __description__
from planet_crs_registry import __version__
from planet_crs_registry.core.business import SqlDatabase

logger = logging.getLogger(__name__)


class SmartFormatter(argparse.HelpFormatter):
    """Smart formatter for argparse - The lines are split for long text"""

    def _split_lines(self, text, width):
        if text.startswith("R|"):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


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


def run_http(options_cli):
    """Main function that instanciates the library with http."""
    logger.info("Starting Planet Crs Registry with http")
    planet_crs_registry = PlanetCrsRegistryLib(
        options_cli.conf_file,
        level=options_cli.level,
    )
    planet_crs_registry.start_http()


def run_https(options_cli):
    """Main function that instanciates the library with https."""
    logger.info("Starting Planet Crs Registry with https")
    planet_crs_registry = PlanetCrsRegistryLib(
        options_cli.conf_file,
        level=options_cli.level,
    )
    planet_crs_registry.start_https()


def handle_cache(options_cli):
    """Handle the cache of the SQL lite database."""
    sql_db = SqlDatabase()
    if os.path.exists(sql_db.db_path):
        if options_cli.use_cache:
            logger.info(
                f"Using cache: {sql_db.db_path}"
            )  # pylint: disable=W1203
        else:
            logger.info(f"removing {sql_db.db_path}")  # pylint: disable=W1203
            os.remove(sql_db.db_path)
            asyncio.run(sql_db.create_db())
    else:
        asyncio.run(sql_db.create_db())


def run():
    """Main function that instanciates the library."""
    logger.info("*** Welcome to Planet Crs Registry ***")
    handler = SigintHandler()
    signal.signal(signal.SIGINT, handler.signal_handler)
    try:
        options_cli = parse_cli()
        handle_cache(options_cli)
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(os.path.abspath(options_cli.conf_file))

        if "HTTP" in config and "HTTPS" in config:
            http_process: Process = Process(
                target=run_http, args=(options_cli,)
            )
            http_process.start()
            https_process: Process = Process(
                target=run_https, args=(options_cli,)
            )
            https_process.start()
            handler.add_process(http_process)
            handler.add_process(https_process)
        elif "HTTP" in config:
            http_process: Process = Process(
                target=run_http, args=(options_cli,)
            )
            http_process.start()
            handler.add_process(http_process)
        elif "HTTPS" in config:
            https_process: Process = Process(
                target=run_https, args=(options_cli,)
            )
            https_process.start()
            handler.add_process(https_process)
        else:
            raise Exception("Unknown protocol to start the server")
    except Exception as error:  # pylint: disable=broad-except
        logging.exception(error)


if __name__ == "__main__":
    # execute only if run as a script
    run()
