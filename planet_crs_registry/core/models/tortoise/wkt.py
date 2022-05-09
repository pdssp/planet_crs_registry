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
# along with Planet CRS Registry.  If not, see <https://www.gnu.org/licenses/>.-
"""ORM"""
from enum import Enum

from tortoise import fields
from tortoise import models


class CenterCs(str, Enum):
    """Center of the coordinate system."""

    OCENTRIC = "OCENTRIC"
    OGRAPHIC = "OGRAPHIC"

    @staticmethod
    def find_enum(name: str):
        """Find enum based on its value

        Args:
            name (str): enum value

        Raises:
            ValueError: Unknown value

        Returns:
            PF: Enum
        """
        result = None
        for pf_name in CenterCs.__members__:
            val = str(CenterCs[pf_name].value)
            if val == name.upper():
                result = CenterCs[pf_name]
                break
        if result is None:
            raise ValueError(f"Unknown enum value for {name}")
        return result


class WKT(models.Model):
    """
    This references a WKT
    """

    # pyright: reportPrivateImportUsage=false
    #: The date where the record has been inserted
    created_at = fields.DatetimeField(auto_now_add=True)

    id = fields.CharField(
        pk=True,
        max_length=100,
        description="ID of WKT. Pattern of the ID is the following IAU:<version>:<code>",
    )
    version = fields.IntField(index=True, description="Version of the WKT")
    code = fields.IntField(indexed=True, description="WKT code")
    solar_body = fields.CharField(
        max_length=100,
        indexed=True,
        description="Solar body such as Mercury, Venus, ...",
    )
    datum_name = fields.CharField(
        max_length=100, indexed=True, description="Datum name"
    )
    ellipsoid_name = fields.CharField(
        max_length=100, indexed=True, description="Ellispoid name"
    )
    projection_name = fields.CharField(
        max_length=100, indexed=True, null=True, description="Projection name"
    )
    wkt = fields.CharField(max_length=3072, description="WKT")
