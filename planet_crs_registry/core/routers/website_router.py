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
"""Web site router"""
import logging
import smtplib
from email.mime.text import MIMEText
from typing import Any
from typing import List
from typing import Union

from fastapi import APIRouter
from fastapi import Request
from fastapi import status
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse
from starlette.responses import RedirectResponse
from tortoise.contrib.fastapi import HTTPNotFoundError

from ..business import query_rep
from ..models import ContactEmail
from ..models import WKT_model
from planet_crs_registry.config import cfg  # pylint: disable=C0411

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    """Root path if the web server"""
    return RedirectResponse(url="/web")


@router.post(
    "/email/",
    summary="Send an email to planetary CRS.",
    description="Send an email to planetary CRS.",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPNotFoundError}
    },
    tags=["Users"],
)
async def send_email(contact: ContactEmail):
    """Send Email to contactEmail

    Args:
        contact (ContactEmail): Information about the contact

    Raises:
        HTTPException: SMTP error
    """
    hostname = cfg.SMTP_HOST
    port = cfg.SMTP_PORT
    user = cfg.SMTP_LOGIN
    password = cfg.SMTP_PASSWD
    try:
        sender = contact.email
        receiver = cfg.CONTACT_EMAIL
        msg = MIMEText(contact.comments)
        msg["Subject"] = f"[Planetery CRS] {contact.firstName} {contact.name}"
        msg["From"] = contact.email
        msg["To"] = [receiver]
        with smtplib.SMTP(hostname, port) as server:
            server.set_debuglevel(1)
            if user is not None and password is not None:
                server.login(user, password)
            server.sendmail(sender, receiver, msg.as_string())
            logger.info("mail successfully sent")
    except ConnectionRefusedError as err:
        logger.error(  # pylint: disable=W1203
            f"SMTP error ({hostname}:{port}): {err}"
        )
        raise HTTPException(
            status_code=500, detail="Cannot connect to SMTP server !"
        ) from err


@router.get("/ping")
async def ping():
    """Ping the server to check it is up"""
    return HTMLResponse("I am here !")


@router.get("/web/about_us.html")
async def about_us(request: Request):
    """About us page"""
    return query_rep.get_about_us(request)


@router.get("/web/index.html")
@router.get("/web/")
async def web_index(request: Request):
    """Root path if the web server"""
    return await query_rep.get_versions(request)


@router.get("/web/all_ids.html")
async def get_all_wkts(request: Request, page: int = 1, limit: int = 100):
    """Create a table of the all WKTs"""
    return await query_rep.get_all_wkts(request, page, limit)


@router.get("/web/search")
async def search(
    request: Request,
    search_term_kw: str,
    page: int = 1,
    limit: int = 100,
) -> object:
    """Returns the representation related to the ouput of the search query.

    Args:
        request (Request): Request
        search_term_kw (str): term to search
        page (int, optional): Current page to display. Defaults to 1.
        limit (int, optional): number of records per page. Defaults to 100.

    Returns:
        object : The representation related to the ouput of the search query
    """
    return await query_rep.get_all_wkts_search(
        request, search_term_kw, page, limit
    )


@router.get("/web/{name_or_version}.html")
async def get_all_wkts_name_or_version(
    request: Request,
    name_or_version: str,
    page: int = 1,
    limit: int = 100,
):
    """Retrive the error page, the WKTs for a given version of planet name.

    Args:
        request (Request): Request
        name_or_version (str): planet name or version
        page (int, optional): Current page to display. Defaults to 1.
        limit (int, optional): Number of records per page. Defaults to 100.
    """
    result: Union[List[int], Any, List[WKT_model]]
    if name_or_version.isnumeric() and int(name_or_version) == 404:
        result = query_rep.get_404(request)
    elif name_or_version.isnumeric():
        result = await query_rep.get_all_wkts_version(
            request, int(name_or_version), page, limit
        )
    else:
        result = await query_rep.get_all_wkts_name(
            request, name_or_version, page, limit
        )
    return result
