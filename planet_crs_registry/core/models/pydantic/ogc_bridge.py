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
from typing import List

from pydantic import create_model
from pydantic import HttpUrl
from pydantic_xml import BaseXmlModel
from pydantic_xml import element


class Identifiers(
    BaseXmlModel,
    tag="identifiers",
    nsmap={
        "": "http://www.opengis.net/crs-nts/1.0",
        "gco": "http://www.isotc211.org/2005/gco",
        "gmd": "http://www.isotc211.org/2005/gmd",
        "at": "http://www.opengis.net/def/crs/IAU/",
    },
):
    identifiers: List[HttpUrl] = element(tag="identifier")


Identifiers_Pydantic = create_model(
    "identifiers",
    __base__=Identifiers,
)
