# -*- coding: utf-8 -*-
import subprocess
from typing import Any

from fastapi import Response

from ..models import Identifiers
from ..models import Identifiers_Pydantic
from planet_crs_registry.config.cfg import IS_PROD


class IdentifiersResponse(Response):
    media_type = "application/xml"

    def render(self, content: Any) -> bytes:
        result: bytes
        if content is None:
            result = b""
        elif isinstance(content, bytes):
            result = content
        elif isinstance(content, Identifiers):
            result = content.to_xml()
        else:
            result = Identifiers(identifiers=content).to_xml()
        return result


class GmlResponse(Response):
    media_type = "application/xml"

    def render(self, content: str) -> bytes:
        data: bytes
        if IS_PROD:
            data = subprocess.check_output(
                [
                    "gdalsrsinfo",
                    content,
                    "-o",
                    "xml",
                ]
            )
        else:
            data = subprocess.check_output(
                [
                    "docker",
                    "run",
                    "--rm",
                    "osgeo/gdal",
                    "gdalsrsinfo",
                    content,
                    "-o",
                    "xml",
                ]
            )
        data = data.decode("utf-8")
        data = data.replace(
            "<gml:GeographicCRS",
            '<gml:GeographicCRS xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gmd="http://www.isotc211.org/2005/gmd"',
        )
        data = data.replace(
            "<gml:ProjectedCRS",
            '<gml:ProjectedCRS xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gmd="http://www.isotc211.org/2005/gmd"',
        )
        data = data.replace("\n", "")
        return Response(content=data, media_type="application/xml").render(
            data
        )
