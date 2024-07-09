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
"""Handler for those exceptions."""
from fastapi import Request
from fastapi import status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import RedirectResponse

from ..business.crs_response import ExceptionReportResponse


async def custom_404_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    """Custom 404 page.

    Args:
        request (Request): Request
        exc (StarletteHTTPException): The specific handler for the exception

    Returns:
        Union[RedirectResponse, object]: Redirection to /web/404.html for 404 status or
        the handler of others http status
    """
    result: object
    if exc.status_code == status.HTTP_404_NOT_FOUND and (
        "/web" in request.url.path
        or "/email" in request.url.path
        or "/ping" in request.url.path
    ):
        result = RedirectResponse(url="/web/404.html")
    else:
        # Just use FastAPI's built-in handler for other errors
        result = await http_exception_handler(request, exc)
    return result


async def custom_ws_exception_handler(
    request: Request, exc: RequestValidationError
):
    """Custom 404 page.

    Args:
        request (Request): Request
        exc (RequestValidationError): The specific handler for the exception

    Returns:
        Union[ExceptionReportResponse, JSONResponse]: OGC IAU bridge error or JSON error
    """
    if "IAU" in request.url.path:
        return ExceptionReportResponse(
            content=exc.errors()[0]["msg"],
            status_code=status.HTTP_404_NOT_FOUND,
        )
    else:
        return await request_validation_exception_handler(request, exc)
