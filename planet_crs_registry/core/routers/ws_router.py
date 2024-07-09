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
"""Services router"""
import logging
from typing import List
from typing import Optional

from fastapi import APIRouter
from fastapi import Path
from fastapi import Query
from fastapi import status
from starlette.exceptions import HTTPException
from tortoise import Tortoise
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.functions import Lower

from ..business import ExceptionReportResponse
from ..business import GmlResponse
from ..business import IdentifiersResponse
from ..business import query_search
from ..models import ExceptionReport_Pydantic
from ..models import Identifiers_Pydantic
from ..models import WKT_model
from ..models import Wkt_Pydantic

logger = logging.getLogger(__name__)

router: APIRouter = APIRouter()

LIMIT_QUERY = Query(
    50, description="Number of records to display", gt=-1, le=100
)
OFFSET_QUERY = Query(
    0, description="Number of records from which we start to display", gt=-1
)


# ------------------
#    WKTs routes
# ------------------
@router.get(
    "/wkts",
    summary="Get information about WKTs.",
    response_model=List[Wkt_Pydantic],  # type: ignore
    description="Lists all WKTs regardless of version",
    tags=["Browse by WKT"],
)
async def get_wkts(
    limit: Optional[int] = LIMIT_QUERY, offset: Optional[int] = OFFSET_QUERY
) -> List[Wkt_Pydantic]:  # type: ignore
    """Lists all WKTs regardless of version.

    The number of WKTs to display is paginated.

    Args:
        limit (Optional[int], optional): Number of records to display.
        Defaults to 50.
        offset (Optional[int], optional): Number of record from which we start
        to display. Defaults to 0.

    Returns:
        List[Wkt_Pydantic]: The JSON representation of the list of all WKTs
    """
    return await Wkt_Pydantic.from_queryset(
        WKT_model.all().limit(limit).offset(offset)  # type: ignore
    )


@router.get(
    "/wkts/count",
    summary="Count the number of WKTs.",
    response_model=int,
    description="Count the number of WKT regardless of version",
    tags=["Browse by WKT"],
)
async def wkts_count() -> int:
    """Count the number of WKTs.

    Returns:
        int: The number of WKTs
    """
    return await WKT_model.all().count()


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
        title="ID of the WKT.",
        description="ID of the WKT following this pattern : IAU:<version>:<code>",
        regex="^.*:\d*:\d*",  # noqa: W605  # pylint: disable=W1401
    ),
) -> str:
    """Get a WKT representation for a given WKT identifier.

    Args:
        wkt_id (str, optional): ID of the WKT.

    Returns:
        str: The WKT representation
    """
    wkt_obj: WKT_model = await query_search.get_wkt_obj(wkt_id)
    return wkt_obj.wkt


# ------------------
#    Versions routes
# ------------------
@router.get(
    "/versions",
    summary="Get the list of WKTs version.",
    response_model=List[int],
    description="List all available versions of the WKT based on IAU reports.",
    tags=["Browse by WKT version"],
)
async def get_versions() -> List[int]:
    """List all available versions of the WKT based on IAU reports

    Returns:
        List[int]: the list of versions
    """
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
    response_model=List[Wkt_Pydantic],  # type: ignore
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
    description="List WKTs for a given version",
    tags=["Browse by WKT version"],
)
async def get_version(
    version_id: int = Path(description="Version of the WKT", gt=2014),
    limit: Optional[int] = LIMIT_QUERY,
    offset: Optional[int] = OFFSET_QUERY,
) -> List[WKT_model]:
    """List WKTs for a given version.

    Args:
        version_id (int, optional): Version of the WKT to search.
        limit (Optional[int], optional): Number of records to display.
        Defaults to 50.
        offset (Optional[int], optional): Number of records from which we
        start to display. Defaults to 0.

    Raises:
        HTTPException: Version not found

    Returns:
        List[WKT_model]: List of WKTs for a given version
    """
    obj = (
        await WKT_model.filter(version=version_id).limit(limit).offset(offset)  # type: ignore
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
        description="Count the number of WKTs for a given version",
        gt=2014,
    )
) -> int:
    """Count the number of WKTs for a given version.

    Args:
        version_id (int, optional): version.

    Returns:
        int: The number of WKTs for a given version
    """
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
    version_id: int = Path(description="Version of the WKT", gt=2014),
    wkt_id: str = Path(
        description="Identifier of the WKT",
        regex="^.*:\d*:\d*$",  # noqa: W605  # pylint: disable=W1401
    ),
) -> str:
    """Get a WKT representation for both a given version and WKT ID

    Args:
        version_id (int, optional): Version of the WKT.
        wkt_id (str, optional): Identifier of the WKT.

    Raises:
        HTTPException: Version or WKT ID not found

    Returns:
        str: The WKT representation
    """
    wkt_obj: WKT_model = await query_search.get_wkt_obj(wkt_id)
    if wkt_obj.version != version_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong version {version_id} for this WKT {wkt_id}",
        )
    return wkt_obj.wkt


# -----------------------
#    Solar bodies routes
# -----------------------
@router.get(
    "/solar_bodies",
    summary="Get solar bodies",
    description="Lists all available solar bodies",
    response_model=List[str],
    tags=["Browse by solar body"],
)
async def get_solar_bodies() -> List[str]:
    """List all solar bodies.

    Returns:
        List[str]: all solar bodies
    """
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
async def solar_bodies_count() -> int:
    """Count the number of solar bodies.

    Returns:
        int: The number of solar bodies
    """
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
    response_model=List[Wkt_Pydantic],  # type: ignore
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
    tags=["Browse by solar body"],
)
async def get_solar_body(
    solar_body: str,
    limit: Optional[int] = LIMIT_QUERY,
    offset: Optional[int] = OFFSET_QUERY,
) -> List[WKT_model]:
    """Lists all WKTs for a given solar body.

    Args:
        solar_body (str): solar body to search
        limit (Optional[int], optional): Number of records to display.
        Defaults to 50.
        offset (Optional[int], optional): Number of records from which we
        start to display. Defaults to 0.

    Raises:
        HTTPException: Solar body not found

    Returns:
        List[WKT_model]: all WKTs for a given solar body
    """
    obj = (
        await WKT_model.annotate(solar_body_lower=Lower("solar_body"))
        .filter(solar_body_lower=solar_body.lower())
        .limit(limit)  # type: ignore
        .offset(offset)  # type: ignore
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
    limit: Optional[int] = LIMIT_QUERY,
    offset: Optional[int] = OFFSET_QUERY,
) -> int:
    """Count the number of WKT for a give solar body.

    Args:
        solar_body (str): solar body to search
        limit (Optional[int], optional): Number of records to display.
        Defaults to 50.
        offset (Optional[int], optional): Number of records from which we
        start to display. Defaults to 0.

    Returns:
        int: the number of WKT for a give solar body
    """
    obj = (
        await WKT_model.annotate(solar_body_lower=Lower("solar_body"))
        .filter(solar_body_lower=solar_body.lower())
        .limit(limit)  # type: ignore
        .offset(offset)  # type: ignore
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
        description="Identifier of the WKT",
        regex="^.*:\d*:\d*$",  # noqa: W605  # pylint: disable=W1401
    ),
) -> str:
    """Get a WKT representation for both a given solar body and a WKT identifier.

    Args:
        solar_body (str): solar body
        wkt_id (str, optional): Identifier of the WKT.

    Raises:
        HTTPException: solar body not found

    Returns:
        str: The WKT representation
    """
    wkt_obj: WKT_model = await query_search.get_wkt_obj(wkt_id)
    if wkt_obj.solar_body.lower() != solar_body.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{wkt_id} not found for {solar_body}",
        )
    return wkt_obj.wkt


# ------------------
#    Search routes
# ------------------
@router.get(
    "/search",
    summary="Search a WKT by keyword",
    description="Search a WKT by keyword",
    tags=["Search"],
    response_model=List[Wkt_Pydantic],  # type: ignore
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def search(
    search_term_kw: str,
    limit: int = LIMIT_QUERY,
    offset: int = OFFSET_QUERY,
) -> List[WKT_model]:
    """Search WKTs for a given keyword.

    Args:
        search_term_kw (str): Term to search
        limit (int, optional):  Number of records to display. Defaults to LIMIT_QUERY.
        offset (int, optional): Number of records from which we start to display. \
            Defaults to OFFSET_QUERY.

    Returns:
        List[WKT_model]: WKTs matching the keyword
    """
    return await query_search.search_term(search_term_kw, limit, offset)


@router.get(
    "/search/count",
    summary="Count WKT by keyword",
    description="Count WKT by keyword",
    tags=["Search"],
    response_model=int,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def search_count(
    search_term_kw: str,
) -> int:
    """Count the number of results matching WKTs for a given keyword.

    Args:
        search_term_kw (str): keyword

    Returns:
        int: The number of results matching WKTs for a given keyword
    """
    return await query_search.search_term_count(search_term_kw)


# ------------------
#    OGC routes
# ------------------
@router.get(
    "/IAU",
    summary="Get the list of IAU versions",
    description="Lists the IAU versions",
    response_class=IdentifiersResponse,
    responses={
        status.HTTP_200_OK: {"model": Identifiers_Pydantic},
    },
    include_in_schema=True,
    tags=["OGC Bridge"],
)
async def get_iau_versions() -> IdentifiersResponse:
    """Returns the list of IAU versions.

    Returns:
        IdentifiersResponse: IAU versions
    """
    versions: List[int] = await get_versions()
    identifier_list: List = list()
    for version in versions:
        identifier_list.append(f"http://www.opengis.net/def/crs/IAU/{version}")
    return IdentifiersResponse(content=identifier_list)


@router.get(
    "/IAU/{iau_version}",
    summary="Get the list of bodies for a given IAU version",
    description="Lists of bodies for a given IAU version",
    response_class=IdentifiersResponse,
    responses={
        status.HTTP_200_OK: {"model": Identifiers_Pydantic},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionReport_Pydantic},
    },
    tags=["OGC Bridge"],
)
async def get_iau_wkts(
    iau_version: int = Path(description="Version of the WKT", gt=2014),
) -> IdentifiersResponse:
    """Returns the list of IAU CRS code for a given version.
    Note: Triaxial Axis are ignored in this list.

    Args:
        iau_version (int, optional): IAU version. \
            Defaults to Path( description="Version of the WKT", gt=2014 ).

    Returns:
        IdentifiersResponse: the list of IAU CRS code as XML response
    """
    try:
        number: int = await version_count(iau_version)
        wkts: List[WKT_model] = await get_version(iau_version, number, 0)
        identifier_list = list()
        for wkt in wkts:
            if "TRIAXIAL" not in wkt.wkt:
                identifier_list.append(
                    f"http://www.opengis.net/def/crs/IAU/{iau_version}/{wkt.code}"
                )
        return IdentifiersResponse(content=identifier_list)
    except HTTPException as http_err:
        return ExceptionReportResponse(
            content=http_err.detail, status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as http_err:
        return ExceptionReportResponse(
            content=http_err.detail, status_code=status.HTTP_404_NOT_FOUND
        )


@router.get(
    "/IAU/{iau_version}/{code}",
    summary="Get the GML representation for a given WKT",
    description="The GML representation for a given WKT",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ExceptionReport_Pydantic},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ExceptionReport_Pydantic
        },
    },
    tags=["OGC Bridge"],
)
async def get_iau_gml(
    iau_version: int = Path(description="Version of the WKT", gt=2014),
    code: str = Path(
        description="Identifier of the WKT",
        regex="^\d*$",  # noqa: W605  # pylint: disable=W1401
    ),
) -> GmlResponse:
    """Returns the GML response for a given IAU crs.

    Args:
        iau_version (int, optional): version of the IAU CRS. \
            Defaults to Path( description="Version of the WKT", gt=2014 ).
        code (_type_, optional): IAU CRS code. \
            Defaults to Path( description="Identifier of the WKT", \
                regex="^\\d*$",).

    Raises:
        HTTPException: 404 - IAU CRS Not found
        HTTPException: 500 - Error when retrieving the IAU CRS as GML

    Returns:
        GmlResponse: IAU crs as GML representation
    """
    iau_version_code = f"IAU:{iau_version}:{code}"
    try:
        return GmlResponse(content=iau_version_code.replace(":", "_"))
    except Exception as error:
        if "crs not found" in str(error):
            return ExceptionReportResponse(
                content="{iau_version_code} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return ExceptionReportResponse(
            content=f"Error when retrieving {iau_version_code} as GML - {error}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.on_event("startup")
async def startup_event():
    """Startup the server."""
    logger.info("loading the db")


@router.on_event("shutdown")
async def close_orm():
    """Shutdown the server"""
    await Tortoise.close_connections()
