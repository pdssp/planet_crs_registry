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
"""Initialization of the server"""
from fastapi import FastAPI
from tortoise.contrib.starlette import register_tortoise
from fastapi.staticfiles import StaticFiles
import os

from .config import tortoise_config
from .core.routers import router_web_site, router_ws


def init(app: FastAPI):
    """
    Init routers and etc.
    :return:
    """
    init_routers(app)
    init_db(app)


def init_db(app: FastAPI):
    """
    Init database models.
    :param app:
    :return:
    """
    register_tortoise(
        app,
        db_url=tortoise_config.db_url,
        generate_schemas=tortoise_config.generate_schemas,
        modules=tortoise_config.modules,
    )


def get_root_directory():
    PATH_TO_CONF = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(PATH_TO_CONF, "..", "web")


def init_routers(app: FastAPI):
    """
    Initialize routers defined in `app.api`
    :param app:
    :return:
    """
    app.include_router(
        router_ws,
        prefix="/ws",
        responses={404: {"description": "Not found"}},
    )
    app.include_router(
        router_web_site,
        tags=["Web site"],
        responses={404: {"description": "Not found"}},
    )
    app.mount(
        "/web",
        StaticFiles(
            directory=get_root_directory(),
            html=True,
        ),
        "web",
    )
