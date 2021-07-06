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
# along with Planet CRS Registry.  If not, see <https://www.gnu.org/licenses/>.
"""Web site router"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import http3
import time
import os
import json
import math
import logging
from typing import Union

logger = logging.getLogger(__name__)

router = APIRouter()
client = http3.AsyncClient()


def get_root_directory():
    PATH_TO_CONF = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(PATH_TO_CONF, "..", "..", "..")


templates = Jinja2Templates(
    directory=os.path.join(get_root_directory(), "templates")
)


async def call_api(url: str):
    r = await client.get(url)
    result = r.text
    return result


@router.get("/")
async def root():
    """Root path if the web server"""
    return RedirectResponse(url="/web")


async def requery_wkts(base_url, page, limit):
    count_records: int
    result: json
    is_over = False
    while not is_over:
        try:
            count_records = int(await call_api(f"{base_url}ws/wkts/count"))
            offset = limit * (page - 1)
            result = json.loads(
                await call_api(
                    f"{base_url}ws/wkts?offset={offset}&limit={limit}"
                )
            )
            is_over = True
        except Exception as exp:
            logging.error(exp)
            time.sleep(0.2)
    return count_records, result


async def requery_version(base_url: str, version: int, page: int, limit: int):
    count_records: int
    result: json
    is_over = False
    while not is_over:
        try:
            count_records = int(
                await call_api(f"{base_url}ws/versions/{version}/count")
            )
            offset = limit * (page - 1)
            result = json.loads(
                await call_api(
                    f"{base_url}ws/versions/{version}?offset={offset}&limit={limit}"
                )
            )
            is_over = True
        except Exception as exp:
            logging.error(exp)
            time.sleep(0.2)
    return count_records, result


async def requery_name(base_url: str, name: str, page: int, limit: int):
    count_records: int
    result: json
    is_over = False
    while not is_over:
        try:
            print(f"{base_url}ws/solar_bodies/{name}/count")
            count_records = int(
                await call_api(f"{base_url}ws/solar_bodies/{name}/count")
            )
            offset = limit * (page - 1)
            print(
                f"{base_url}ws/solar_bodies/{name}?offset={offset}&limit={limit}"
            )
            result = json.loads(
                await call_api(
                    f"{base_url}ws/solar_bodies/{name}?offset={offset}&limit={limit}"
                )
            )
            is_over = True
        except Exception as exp:
            logging.error(exp)
            time.sleep(0.2)
    return count_records, result


@router.get("/web/all_ids.html")
async def get_all_wkts(request: Request, page: int = 1, limit: int = 100):
    """Create a table of the all WKTs"""
    base_url = request.base_url
    count, result = await requery_wkts(base_url, page, limit)
    pages = range(1, math.ceil(count / limit) + 1)
    current_page = page
    previous_pages = pages[0 : current_page - 1]
    next_pages = pages[current_page : len(pages)]
    columns_name = result[0].keys()
    return templates.TemplateResponse(
        "results-table.html",
        {
            "title": "List all WKTs",
            "request": request,
            "navigation": columns_name,
            "records": result,
            "previous_pages": previous_pages,
            "next_pages": next_pages,
            "page_current": current_page,
            "previous_page": page - 1,
            "next_page": page + 1 if (page + 1) * limit <= count else -1,
        },
    )


async def get_all_wkts_version(
    request: Request, version_id: int, page: int = 1, limit: int = 100
):
    """Create a table of the all WKTs"""
    base_url = request.base_url
    count, result = await requery_version(base_url, version_id, page, limit)
    pages = range(1, math.ceil(count / limit) + 1)
    current_page = page
    previous_pages = pages[0 : current_page - 1]
    next_pages = pages[current_page : len(pages)]
    columns_name = result[0].keys()
    return templates.TemplateResponse(
        "results-table.html",
        {
            "title": f"List all WKTs for {version_id}",
            "request": request,
            "navigation": columns_name,
            "records": result,
            "previous_pages": previous_pages,
            "next_pages": next_pages,
            "page_current": current_page,
            "previous_page": page - 1,
            "next_page": page + 1 if (page + 1) * limit <= count else -1,
        },
    )


async def get_all_wkts_name(
    request: Request, name: str, page: int = 1, limit: int = 100
):
    """Create a table of the all WKTs"""
    base_url = request.base_url
    count, result = await requery_name(base_url, name, page, limit)
    pages = range(1, math.ceil(count / limit) + 1)
    current_page = page
    previous_pages = pages[0 : current_page - 1]
    next_pages = pages[current_page : len(pages)]
    columns_name = result[0].keys()
    return templates.TemplateResponse(
        "results-table.html",
        {
            "title": f"List all WKTs for {name}",
            "request": request,
            "navigation": columns_name,
            "records": result,
            "previous_pages": previous_pages,
            "next_pages": next_pages,
            "page_current": current_page,
            "previous_page": page - 1,
            "next_page": page + 1 if (page + 1) * limit <= count else -1,
        },
    )


@router.get("/web/{name_or_version}.html")
async def get_all_wkts_name_or_version(
    request: Request,
    name_or_version: str,
    page: int = 1,
    limit: int = 100,
):
    if name_or_version.isnumeric() and int(name_or_version) == 404:
        return templates.TemplateResponse("404.html", {"request": request})
    elif name_or_version.isnumeric():
        return await get_all_wkts_version(
            request, int(name_or_version), page, limit
        )
    else:
        return await get_all_wkts_name(request, name_or_version, page, limit)
