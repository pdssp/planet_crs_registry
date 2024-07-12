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
"""Serialization of the data model"""
from pydantic import field_validator
from tortoise.contrib.pydantic import pydantic_model_creator

from ..tortoise import WKT

Wkt_Pydantic = pydantic_model_creator(WKT, name="WKT")


class Wkt_Pydantic_With_Cleaned_WKT(Wkt_Pydantic):
    @field_validator("wkt", mode="before")
    def clean_wkt(cls, value):
        # Remove line breaks and tabs, and extra spaces, \" and " at the being/end
        value = value.replace("\n", "").replace("\t", "")
        value = " ".join(value.split())
        return value
