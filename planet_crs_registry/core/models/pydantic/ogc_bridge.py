# -*- coding: utf-8 -*-
from typing import Any
from typing import List

from pydantic import create_model
from pydantic import HttpUrl
from pydantic_xml import attr
from pydantic_xml import BaseXmlModel
from pydantic_xml import element
from pydantic_xml import wrapped


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
