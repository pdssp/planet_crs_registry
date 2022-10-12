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
"""Business module"""
import json
import logging
import math
import os
import time
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Tuple

import http3  # type: ignore
from fastapi import Request
from fastapi import status
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException
from tortoise.expressions import Q

from ..models import WKT_model
from ..models import Wkt_Pydantic


@dataclass
class Navigation:
    """Class that is responsible for handling the pagination"""

    count: int
    page: int
    limit: int


class QuerySearch:
    """Class that implements a set of query to the router of the web services."""

    def __init__(self):
        """Initialization"""
        self.__client = http3.AsyncClient()

    @property
    def client(self):
        """The HTTP client.

        :getter: Returns the client
        :type: Any
        """
        return self.__client

    async def _call_api(self, url: str) -> str:
        """Call the API and returns the result.

        Args:
            url (str): URL to query

        Returns:
            str: result of query response
        """
        result = await self.client.get(url)
        return result.text

    def _filter_records(self, response: str) -> List:
        """Filters the records by removing version and code.

        Args:
            response (str): response

        Returns:
            List: filtered response
        """
        keys_to_remove: List[str] = ["version", "code"]
        filtered_result: List = list()
        for record in json.loads(response):
            res: Dict = {
                key: record[key]
                for key in record.keys()
                if key not in keys_to_remove
            }
            res["created_at"] = res["created_at"][0:10]
            filtered_result.append(res)
        return filtered_result

    async def query_wkts(
        self, base_url: str, page: int, limit: int
    ) -> Tuple[int, List]:
        """Query the WKTs using the web service

        Args:
            base_url (str): base URL of the web service
            page (int): current page
            limit (int): number of elements in a page

        Returns:
            Tuple[int, List]: total number of records, results in the page
        """
        count_records: int = 0
        result: List = list()
        is_over = False
        while not is_over:
            try:
                count_records = int(
                    await self._call_api(f"{base_url}ws/wkts/count")
                )
                offset = limit * (page - 1)
                result = self._filter_records(
                    await self._call_api(
                        f"{base_url}ws/wkts?offset={offset}&limit={limit}"
                    )
                )
                is_over = True
            except Exception as exp:  # pylint: disable=W0703
                logging.error(exp)
                time.sleep(0.2)
        return count_records, result

    async def query_version(
        self, base_url: str, version: int, page: int, limit: int
    ) -> Tuple[int, List]:
        """Get WKTs for a given version from the web service.

        Args:
            base_url (str): base URL
            version (int): version
            page (int): current page
            limit (int): Number of records per page.

        Returns:
            Tuple[int, List]: total number of records, results in the page
        """
        count_records: int = 0
        result: List = list()
        is_over = False
        while not is_over:
            try:
                count_records = int(
                    await self._call_api(
                        f"{base_url}ws/versions/{version}/count"
                    )
                )
                offset = limit * (page - 1)
                result = self._filter_records(
                    await self._call_api(
                        f"{base_url}ws/versions/{version}?offset={offset}&limit={limit}"
                    )
                )
                is_over = True
            except Exception as exp:  # pylint: disable=W0703
                logging.error(exp)
                time.sleep(0.2)
        return count_records, result

    async def query_name(
        self, base_url: str, name: str, page: int, limit: int
    ) -> Tuple[int, List]:
        """Get WKTs for a given solar body using the web service.

        Args:
            base_url (str): base URL of the web service
            name (str): solar body name
            page (int): current page
            limit (int): number of elements in the page

        Returns:
            Tuple[int, List]: total number of records, results in the page
        """
        count_records: int = 0
        result: List = list()
        is_over = False
        while not is_over:
            try:
                count_records = int(
                    await self._call_api(
                        f"{base_url}ws/solar_bodies/{name}/count"
                    )
                )
                offset = limit * (page - 1)
                result = self._filter_records(
                    await self._call_api(
                        f"{base_url}ws/solar_bodies/{name}?offset={offset}&limit={limit}"
                    )
                )
                is_over = True
            except Exception as exp:  # pylint: disable=W0703
                logging.error(exp)
                time.sleep(0.2)
        return count_records, result

    async def query_search_terms(
        self, base_url: str, search_term_kw: str, page: int, limit: int
    ) -> Tuple[int, List]:
        """Query the WKTs for a given keyword using the web service.

        Args:
            base_url (str): base URL of the web service
            search_term_kw (str): keyword to search
            page (int): current page
            limit (int): number of elements in the page

        Returns:
            Tuple[int, List]: total number of records, results in the page
        """
        count_records: int = 0
        result: List = list()
        is_over = False
        while not is_over:
            try:
                count_records = int(
                    await self._call_api(
                        f"{base_url}ws/search/count?search_term_kw={search_term_kw}"
                    )
                )
                offset = limit * (page - 1)
                result = self._filter_records(
                    await self._call_api(
                        f"{base_url}ws/search?search_term_kw={search_term_kw}&offset={offset}&limit={limit}"  # pylint: disable=C0301
                    )
                )
                is_over = True
            except Exception as exp:  # pylint: disable=W0703
                logging.error(exp)
                time.sleep(0.2)
        return count_records, result

    async def query_version_list(self, base_url: str) -> List[int]:
        """Get the different version numbers using the web service.

        Args:
            base_url (str): base URL of the web service

        Returns:
            List[int]: list of versions
        """
        result: List[int] = list()
        is_over = False
        while not is_over:
            try:
                result = json.loads(
                    await self._call_api(f"{base_url}ws/versions")
                )
                is_over = True
            except Exception as exp:  # pylint: disable=W0703
                logging.error(exp)
                time.sleep(0.2)
        return result

    async def search_term(
        self, search_term_kw: str, limit: int = 50, offset: int = 0
    ) -> List[WKT_model]:
        """Search term in wkt ot id.

        Args:
            search_term_kw (str): keyword to search
            limit (int, optional): number of records in the page. Defaults to 50.
            offset (int, optional): Number of records to skip at the beginning.
            Defaults to 0.

        Returns:
            List[WKT_model]: Lost of WKTs matching the keyword
        """
        return (
            await WKT_model.filter(
                Q(wkt__contains=search_term_kw)
                | Q(id__contains=search_term_kw)
            )
            .limit(limit)
            .offset(offset)
        )

    async def search_term_count(self, search_term_kw: str) -> int:
        """Count the result of the search term.

        Args:
            search_term_kw (str): keyword to search

        Returns:
            int: number of elements in the result
        """
        return await WKT_model.filter(
            Q(wkt__contains=search_term_kw) | Q(id__contains=search_term_kw)
        ).count()

    async def get_wkt_obj(self, wkt_id: str) -> WKT_model:
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{wkt_id} not found",
            )
        wkt_obj: WKT_model = await Wkt_Pydantic.from_tortoise_orm(obj)  # type: ignore
        return wkt_obj


class QueryRepresentation:
    """Class thats handles the representation of a template."""

    def __init__(self):
        """Initialization."""
        self.__templates = Jinja2Templates(
            directory=os.path.join(
                QueryRepresentation.get_root_directory(), "templates"
            )
        )
        self.__search = QuerySearch()

    @property
    def templates(self):
        """The templates.

        :getter: Returns the templates object that allow to access to template
        files
        :type: Any
        """
        return self.__templates

    @property
    def search(self):
        """The HTTP client.

        :getter: Returns the HTTP client
        :type: Any
        """
        return self.__search

    @staticmethod
    def get_root_directory() -> str:
        """Returns the root directory.

        From the root directory, it is possible to access to both templates and
        web directories.

        Returns:
            str: Root directory of the package
        """
        path_to_conf = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(path_to_conf, "..", "..", "..")

    async def _replace_in_template(
        self,
        request: Request,
        result: List,
        pagination: Navigation,
        title: str,
        **kwargs,
    ):
        """Replace the object in the template.

        Args:
            request (Request): request
            result (List): result
            pagination (Navigation): navigation throw the pages
            title (str): title
            web_service (str): URL of the web_service without pagination parameters

        Returns:
            object: template rendering
        """
        web_service: str
        if "ws" in kwargs:
            web_service = kwargs["ws"]
        else:
            raise Exception("ws parameter is not provided")

        pages = range(1, math.ceil(pagination.count / pagination.limit) + 1)
        current_page = pagination.page
        previous_pages = pages[0 : current_page - 1]
        next_pages = pages[current_page : len(pages)]
        columns_name = result[0].keys() if len(result) > 0 else list()
        url_ws = web_service + "&" if "?" in web_service else web_service + "?"

        return self.templates.TemplateResponse(
            "results-table.html",
            {
                "title": title,
                "request": request,
                "navigation": columns_name,
                "records": result,
                "previous_pages": previous_pages,
                "next_pages": next_pages,
                "page_current": current_page,
                "previous_page": pagination.page - 1,
                "next_page": pagination.page + 1
                if pagination.page * pagination.limit <= pagination.count
                else -1,
                "url_ws": url_ws,
            },
        )

    def get_404(self, request: Request):
        """404 error page"""
        return self.templates.TemplateResponse(
            "404.html", {"request": request}
        )

    async def get_versions(self, request: Request):
        """Set the versions in the index.html"""
        base_url = request.base_url
        versions = await self.search.query_version_list(str(base_url))
        return self.templates.TemplateResponse(
            "index.html", {"request": request, "versions": versions}
        )

    async def get_all_wkts(
        self, request: Request, page: int = 1, limit: int = 100
    ):
        """Create a table of the all WKTs in the results-table.html

        Args:
            request (Request): request
            page (int, optional): current page. Defaults to 1.
            limit (int, optional): number of elements in the page. Defaults to 100.

        Returns:
            object: Representation of the template output
        """
        base_url = request.base_url
        count, result = await self.search.query_wkts(
            str(base_url), page, limit
        )
        pagination = Navigation(count, page, limit)
        return await self._replace_in_template(
            request,
            result,
            pagination,
            "List all WKTs",
            ws="/web/all_ids.html",
        )

    async def get_all_wkts_version(
        self,
        request: Request,
        version_id: int,
        page: int = 1,
        limit: int = 100,
    ):
        """Create a table of the all WKTs for a given version in the
        results-table.html

        Args:
            request (Request): request
            version_id (int): version
            page (int, optional): current page. Defaults to 1.
            limit (int, optional): number of elements in the page. Defaults to 100.

        Returns:
            object: Representation of the template output
        """
        base_url = request.base_url
        count, result = await self.search.query_version(
            str(base_url), version_id, page, limit
        )
        pagination = Navigation(count, page, limit)
        return await self._replace_in_template(
            request,
            result,
            pagination,
            f"List all WKTs for {version_id}",
            ws=f"/web/{version_id}.html",
        )

    async def get_all_wkts_name(
        self, request: Request, name: str, page: int = 1, limit: int = 100
    ):
        """Create a table of the all WKTs for a given solar body in the
        results-table.html

        Args:
            request (Request): request
            name (str): solar body
            page (int, optional): current page. Defaults to 1.
            limit (int, optional): number of elements in the page. Defaults to 100.

        Returns:
            object: Representation of the template output
        """
        base_url = request.base_url
        count, result = await self.search.query_name(
            str(base_url), name, page, limit
        )
        pagination = Navigation(count, page, limit)
        return await self._replace_in_template(
            request,
            result,
            pagination,
            f"List all WKTs for {name}",
            ws=f"/web/{name}.html",
        )

    async def get_all_wkts_search(
        self,
        request: Request,
        search_term_kw: str,
        page: int = 1,
        limit: int = 100,
    ):
        """Create a table of the all WKTs for a given keyword in the
        results-table.html

        Args:
            request (Request): request
            name (str): solar body
            page (int, optional): current page. Defaults to 1.
            limit (int, optional): number of elements in the page. Defaults to 100.

        Returns:
            object: Representation of the template output
        """
        base_url = request.base_url
        count, result = await self.search.query_search_terms(
            str(base_url), search_term_kw, page, limit
        )
        pagination = Navigation(count, page, limit)
        return await self._replace_in_template(
            request,
            result,
            pagination,
            f"List all WKTs for {search_term_kw}",
            ws=f"/web/search?search_term_kw={search_term_kw}",
        )


root_directory = QueryRepresentation.get_root_directory()
query_rep = QueryRepresentation()
query_search = query_rep.search
