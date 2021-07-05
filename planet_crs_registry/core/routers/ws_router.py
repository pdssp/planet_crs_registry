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
"""Services router"""

import logging
import pathlib

from tortoise.queryset import ExistsQuery, QuerySet
from planet_crs_registry.core.models.pydantic import wkt
import re
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query, status
from fastapi.responses import RedirectResponse
from planet_crs_registry.config import tortoise_config
from starlette.status import HTTP_400_BAD_REQUEST
from tortoise import Tortoise
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.functions import Lower

from ..business import WktDatabase
from ..models import WKT_model, Wkt_Pydantic
from ..models import CenterCs

logger = logging.getLogger(__name__)

router = APIRouter()
# https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html


async def get_wkt_obj(wkt_id: str) -> WKT_model:
    """Retrieves the WKT representation from the database based on its id.

    Args:
        wkt_id (str): WKT id

    Raises:
        HTTPException: WKT not found in the database

    Returns:
        WKT_model: WKT object
    """
    obj = await WKT_model.get_or_none(id=wkt_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{wkt_id} not found"
        )
    wkt_obj: WKT_model = await Wkt_Pydantic.from_tortoise_orm(obj)
    return wkt_obj


@router.get(
    "/wkts",
    summary="Get information about WKTs.",
    response_model=List[Wkt_Pydantic],
    description="Lists all WKTs regardless of version",
    tags=["Browse by WKT"],
)
async def get_wkts(
    limit: Optional[int] = Query(
        50, description="Number of records to display", gt=-1, le=101
    ),
    offset: Optional[int] = Query(
        0, description="Number of record from which we start to display", gt=-1
    ),
):
    return await Wkt_Pydantic.from_queryset(
        WKT_model.all().limit(limit).offset(offset)
    )


@router.get(
    "/wkts/count",
    summary="Count the number of WKTs.",
    response_model=int,
    description="Count the number of WKT regardless of version",
    tags=["Browse by WKT"],
)
async def wkts_count():
    return await WKT_model.all().count()


@router.get(
    "/versions",
    summary="Get versions of the WKTs.",
    response_model=List[int],
    description="List all available versions of the WKT based on IAU reports.",
    tags=["Browse by WKT version"],
)
async def get_versions():
    objs = (
        await WKT_model.all()
        .group_by("version")
        .order_by("version")
        .values("version")
    )
    versions = list()
    for obj in objs:
        versions.append(obj["version"])
    return versions


@router.get(
    "/versions/{version_id}",
    summary="Get information about WKTs for a given version",
    response_model=List[Wkt_Pydantic],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
    description="List WKTs for a given version",
    tags=["Browse by WKT version"],
)
async def get_version(
    version_id: int = Path(
        default=2015, description="Version of the WKT", gt=2014
    ),
    limit: Optional[int] = Query(
        50, description="Number of records to display", gt=-1, le=101
    ),
    offset: Optional[int] = Query(
        0, description="Number of record from which we start to display", gt=-1
    ),
):
    obj = (
        await WKT_model.filter(version=version_id).limit(limit).offset(offset)
    )
    if len(obj) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{version_id} not found",
        )
    return obj


@router.get(
    "/versions/{version_id}/count",
    summary="Count the number of WKTs for a given version",
    response_model=int,
    description="Count the number of WKTs for a given version",
    tags=["Browse by WKT version"],
)
async def version_count(
    version_id: int = Path(
        default=2015,
        description="Count the number of WKTs for a given version",
        gt=2014,
    )
):
    return await WKT_model.filter(version=version_id).count()


@router.get(
    "/versions/{version_id}/{wkt_id}",
    summary="Get a WKT for a given version.",
    description="Retrieve a WKT",
    tags=["Browse by WKT version"],
    response_model=str,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPNotFoundError},
    },
)
async def get_wkt_version(
    version_id: int = Path(
        default=2015, description="Version of the WKT", gt=2014
    ),
    wkt_id: str = Path(
        default="IAU:2015:1000",
        description="Identifier of the WKT",
        regex="^.*:\d*:\d*$",
    ),
):
    wkt_obj: WKT_model = await get_wkt_obj(wkt_id)
    if wkt_obj.version != version_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong version {version_id} for this WKT {wkt_id}",
        )
    return wkt_obj.wkt


@router.get(
    "/wkts/{wkt_id}",
    summary="Get a WKT",
    response_model=str,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
    description="Retrieve a WKT for a given WKT ID.",
    tags=["Browse by WKT"],
)
async def get_wkt(
    wkt_id: str = Path(
        default="IAU:2015:1000",
        title="ID of the WKT.",
        description="ID of the WKT following this pattern : IAU:<version>:<code>",
        regex="^.*:\d*:\d*",
    ),
):
    wkt_obj: WKT_model = await get_wkt_obj(wkt_id)
    return wkt_obj.wkt


@router.get(
    "/solar_bodies",
    summary="Get solar bodies",
    description="Lists all available solar bodies",
    response_model=List[str],
    tags=["Browse by solar body"],
)
async def get_solar_bodies():
    objs = (
        await WKT_model.all()
        .group_by("solar_body")
        .order_by("solar_body")
        .values("solar_body")
    )
    solar_bodies = list()
    for obj in objs:
        solar_bodies.append(obj["solar_body"])
    return solar_bodies


@router.get(
    "/solar_bodies/count",
    summary="Count the number of solar bodies",
    description="Count all available solar bodies",
    response_model=int,
    tags=["Browse by solar body"],
)
async def solar_bodies_count():
    objs = (
        await WKT_model.all()
        .group_by("solar_body")
        .order_by("solar_body")
        .values("solar_body")
    )
    solar_bodies = list()
    for obj in objs:
        solar_bodies.append(obj["solar_body"])
    return len(solar_bodies)


@router.get(
    "/solar_bodies/{solar_body}",
    summary="Get information about WKTs for a given solar body",
    description="Lists all WKTs for a given solar body",
    response_model=List[Wkt_Pydantic],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
    tags=["Browse by solar body"],
)
async def get_solar_body(
    solar_body: str,
    limit: Optional[int] = Query(
        50, description="Number of records to display", gt=-1, le=101
    ),
    offset: Optional[int] = Query(
        0, description="Number of record from which we start to display", gt=-1
    ),
):
    obj = (
        await WKT_model.annotate(solar_body_lower=Lower("solar_body"))
        .filter(solar_body_lower=solar_body.lower())
        .limit(limit)
        .offset(offset)
    )
    if len(obj) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{solar_body} not found",
        )
    return obj


@router.get(
    "/solar_bodies/{solar_body}/count",
    summary="Count the number of WKTs for a given solar body",
    description="Count the number of WKTs for a given solar body",
    response_model=int,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
    tags=["Browse by solar body"],
)
async def get_solar_body_count(
    solar_body: str,
    limit: Optional[int] = Query(
        50, description="Number of records to display", gt=-1, le=101
    ),
    offset: Optional[int] = Query(
        0, description="Number of record from which we start to display", gt=-1
    ),
):
    obj = (
        await WKT_model.annotate(solar_body_lower=Lower("solar_body"))
        .filter(solar_body_lower=solar_body.lower())
        .limit(limit)
        .offset(offset)
        .count()
    )
    return obj


@router.get(
    "/solar_bodies/{solar_body}/{wkt_id}",
    summary="Get a WKT for a given solar body.",
    description="Retrieve a WKT",
    tags=["Browse by solar body"],
    response_model=str,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPNotFoundError},
    },
)
async def get_wkt_body(
    solar_body: str,
    wkt_id: str = Path(
        default="IAU:2015:1000",
        description="Identifier of the WKT",
        regex="^.*:\d*:\d*$",
    ),
):
    wkt_obj: WKT_model = await get_wkt_obj(wkt_id)
    if wkt_obj.solar_body.lower() != solar_body.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{wkt_id} not found for {solar_body}",
        )
    return wkt_obj.wkt


@router.on_event("startup")
async def startup_event():
    pattern = "sqlite://(?P<db_name>.*)"
    m = re.match(pattern, tortoise_config.db_url)
    file = None
    if m is not None:
        file = pathlib.Path(m.group("db_name"))

    if file is None or not file.exists():
        await Tortoise.init(
            db_url=tortoise_config.db_url, modules=tortoise_config.modules
        )
        await Tortoise.generate_schemas()
        wkt = WktDatabase()
        index = wkt.index
        logger.info(f"nb records : {len(index)}")
        for record in index:
            wkt_data = {
                "id": f"IAU:{record.iau_version}:{record.iau_code}",
                "version": int(record.iau_version),
                "code": int(record.iau_code),
                "center_cs": CenterCs.find_enum(record.origin_crs),
                "solar_body": re.match(r"[^\s]+", record.datum).group(0),
                "datum_name": record.datum,
                "ellipsoid_name": record.ellipsoid,
                "projection_name": record.projcrs,
                "wkt": record.wkt,
            }
            await WKT_model.create(**wkt_data)
        logger.info("Database loaded")
    else:
        logger.info("loading the db")


@router.on_event("shutdown")
async def close_orm():
    await Tortoise.close_connections()
