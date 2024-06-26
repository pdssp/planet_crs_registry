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
"""Models for making the OGC bridge from opengis to IAU CRS registry."""
from typing import List

import pydantic_xml
from pydantic import create_model  # pylint: disable=E0611
from pydantic import HttpUrl  # pylint: disable=E0611
from pydantic_xml import BaseXmlModel  # type: ignore
from pydantic_xml import element


class Identifiers(  # type: ignore
    BaseXmlModel,
    tag="identifiers",
    nsmap={
        "": "http://www.opengis.net/crs-nts/1.0",
        "gco": "http://www.isotc211.org/2005/gco",
        "gmd": "http://www.isotc211.org/2005/gmd",
        "at": "http://www.opengis.net/def/crs/IAU/",
    },
):
    """Model for identifiers response."""

    identifiers: List[HttpUrl] = element(tag="identifier")


class ExceptionText(
    BaseXmlModel,
    ns="ows",
    tag="ExceptionText",
    nsmap={
        "ows": "http://www.opengis.net/ows/2.0",
    },
):
    text: str


class ExceptionItem(
    BaseXmlModel,
    tag="Exception",
    nsmap={
        "ows": "http://www.opengis.net/ows/2.0",
    },
):
    exceptionCode: str = pydantic_xml.attr()
    exceptionText: ExceptionText


class ExceptionReport(
    BaseXmlModel,
    ns="ows",
    tag="ExceptionReport",
    nsmap={
        "ows": "http://www.opengis.net/ows/2.0",
        "xsd": "http://www.w3.org/2001/XMLSchema-instance",
        "xlink": "http://www.w3.org/1999/xlink",
    },
):
    version: str = pydantic_xml.attr(default="2.0.0")
    schema_location: str = pydantic_xml.attr(
        name="schemaLocation",
        ns="xsd",
        default="http://www.opengis.net/ows/2.0 http://schemas.opengis.net/ows/2.0/owsExceptionReport.xsd",
    )
    exception: ExceptionItem


Identifiers_Pydantic = create_model(
    "identifiers",
    __base__=Identifiers,
)

ExceptionReport_Pydantic = create_model(
    "ExceptionReport",
    __base__=ExceptionReport,
)
