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
"""Config of DB"""
from pydantic import Field

from .base import BaseSettings
from .cfg import IS_TEST

DB_MODELS = ["planet_crs_registry.core.models.tortoise"]
POSTGRES_DB_URL = "postgres://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"  # pylint: disable=line-too-long
SQLITE_DB_URL = "sqlite://{sqlite_db}"  # sqlite://:memory:"


class SqlLiteSettings(BaseSettings):  # pylint: disable=too-few-public-methods
    """SQL list env values"""

    sqlite_db: str = Field("db.sqlite3", env="SQLITE_DB")


class PostgresSettings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Postgres env values"""

    postgres_user: str = Field("postgres", env="POSTGRES_USER")
    postgres_password: str = Field("postgres", env="POSTGRES_PASSWORD")
    postgres_db: str = Field("mydb", env="POSTGRES_DB")
    postgres_port: str = Field("5432", env="POSTGRES_PORT")
    postgres_host: str = Field("postgres", env="POSTGRES_HOST")


class TortoiseSettings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Tortoise-ORM settings"""

    db_url: str
    modules: dict
    generate_schemas: bool

    @classmethod
    def generate(cls):
        """Generate Tortoise-ORM settings (with sqlite if tests)"""

        if IS_TEST:
            sqlite = SqlLiteSettings()
            db_url = SQLITE_DB_URL.format(**sqlite.dict())
            del sqlite
        else:
            postgres = PostgresSettings()
            db_url = POSTGRES_DB_URL.format(**postgres.dict())
            del postgres
        modules = {"models": DB_MODELS}
        return TortoiseSettings(
            db_url=db_url, modules=modules, generate_schemas=True
        )
