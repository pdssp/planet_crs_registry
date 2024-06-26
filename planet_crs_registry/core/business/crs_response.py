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
"""Handles the IAU responses of the IAU web services."""
import os
from typing import Any

from fastapi import Response

from ..models import ExceptionItem
from ..models import ExceptionReport
from ..models import ExceptionText
from ..models import Identifiers
from planet_crs_registry.config.cfg import IS_PROD  # pylint: disable=C0411


class IdentifiersResponse(Response):
    """Creates the Identifiers response of the IAU web service."""

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


class ExceptionReportResponse(Response):
    """Creates the ExceptionReport response of the IAU web service."""

    media_type = "application/xml"

    def render(self, content: Any) -> bytes:
        # self.status_code = 404
        result: bytes
        if content is None:
            result = b""
        elif isinstance(content, bytes):
            result = content
        elif isinstance(content, ExceptionReport):
            result = content.to_xml()
        else:
            result = ExceptionReport(
                exception=ExceptionItem(
                    exceptionCode="InternalComponentError",
                    exceptionText=ExceptionText(text=content),
                )
            ).to_xml()
        return result


class GmlResponse(Response):
    """Creates the GML response of the IAU web service."""

    media_type = "application/xml"

    def render(self, content: str) -> bytes:
        """Render the GML response from stored data.

        Args:
            content (str): IAU identifier (separated by underscore)

        Returns:
            bytes: the response in GML
        """
        content = content + ".xml"

        gml_path = os.environ.get("GML_PATH")
        if gml_path is None:
            gml_path = os.path.join("planet_crs_registry", "data", "gml")
        gml_file_path = os.path.join(gml_path, f"{content}")

        try:
            with open(gml_file_path, mode="rb") as gml_file:
                data: bytes = gml_file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File '{content}' not found.")
        except IOError as e:
            raise IOError(
                f"Error: An I/O error occurred while opening '{content}': {e}"
            )

        data_str: str = data.decode("utf-8")

        return Response(content=data_str, media_type="application/xml").render(
            data_str
        )
