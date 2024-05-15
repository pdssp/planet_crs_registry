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
"""WKT database"""
import logging
import re
from dataclasses import dataclass
from os import getcwd
from os import path
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from tortoise import Tortoise

from planet_crs_registry.config import tortoise_config
from planet_crs_registry.core.models import WKT_model

logger = logging.getLogger(__name__)


class WktDatabase:  # pylint: disable=R0903
    """WKT database as WKT-crs standard"""

    OGRAPHIC = "Ographic"
    OCENTRIC = "Ocentric"

    GEOCENTRIC_CRS_TEMPLATE = """GEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", ELLIPSOID\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<flattening>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0, ANGLEUNIT\["degree", 0.0174532925199433, ID\["EPSG", 9122\]\]\], CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["planetocentric latitude \(U\)", (?P<latitude_asc>.*), ORDER\[1\], ANGLEUNIT\["degree", 0.0174532925199433\]\], AXIS\["planetocentric longitude \(V\)", (?P<longitude_asc>.*), ORDER\[2\], ANGLEUNIT\["degree", 0.0174532925199433\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\], REMARK\["(?P<remark>).*"\]\]"""  # noqa: W605  # pylint: disable=W1401,C0301
    GEOGRAPHIC_CRS_TEMPLATE = """GEOGCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", ELLIPSOID\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<flattening>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0, ANGLEUNIT\["degree", 0.0174532925199433, ID\["EPSG", 9122\]\]\], CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["geodetic latitude \(Lat\)", (?P<latitude_asc>.*), ORDER\[1\], ANGLEUNIT\["degree", 0.0174532925199433\]\], AXIS\["geodetic longitude \(Lon\)", (?P<longitude_asc>.*), ORDER\[2\], ANGLEUNIT\["degree", 0.0174532925199433\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\], REMARK\["(?P<remark>).*"\]\]"""  # noqa: W605  # pylint: disable=W1401,C0301
    GEOCENTRIC_TRIAXIAL_TEMPLATE = """GEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", TRIAXIAL\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<semi_median>.*), (?P<semi_minor>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0, ANGLEUNIT\["degree", 0.0174532925199433, ID\["EPSG", 9122\]\]\], CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["planetocentric latitude \(U\)", (?P<latitude_asc>.*), ORDER\[1\], ANGLEUNIT\["degree", 0.0174532925199433\]\], AXIS\["planetocentric longitude \(V\)", (?P<longitude_asc>.*), ORDER\[2\], ANGLEUNIT\["degree", 0.0174532925199433\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\], REMARK\["(?P<remark>).*"\]\]"""  # noqa: W605  # pylint: disable=W1401,C0301
    GEOGRAPHIC_TRIAXIAL_TEMPLATE = """GEOGCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", TRIAXIAL\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<semi_median>.*), (?P<semi_minor>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0, ANGLEUNIT\["degree", 0.0174532925199433, ID\["EPSG", 9122\]\]\], CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["geodetic latitude \(Lat\)", (?P<latitude_asc>.*), ORDER\[1\], ANGLEUNIT\["degree", 0.0174532925199433\]\], AXIS\["geodetic longitude \(Lon\)", (?P<longitude_asc>.*), ORDER\[2\], ANGLEUNIT\["degree", 0.0174532925199433\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\], REMARK\["(?P<remark>).*"\]\]"""  # noqa: W605  # pylint: disable=W1401,C0301
    PROJ_CRS_BI_OCEN_TEMPLATE = """PROJCRS\["(?P<projcrs>.*)", BASEGEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", ELLIPSOID\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<flattening>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0, ANGLEUNIT\["degree", 0.0174532925199433, ID\["EPSG", 9122\]\]\], ID\["IAU", (?P<iau_code_body>.*), (?P<iau_version_body>.*)\]\], (?P<conversion>.*), CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["(?P<longitude_name>.*)", (?P<longitude_asc>.*), ORDER\[1\], LENGTHUNIT\["metre", 1\]\], AXIS\["Northing \(N\)", (?P<latitude_asc>.*), ORDER\[2\], LENGTHUNIT\["metre", 1\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\]\]"""  # noqa: W605  # pylint: disable=W1401,C0301
    PROJ_CRS_BI_OGRA_TEMPLATE = """PROJCRS\["(?P<projcrs>.*)", BASEGEOGCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", ELLIPSOID\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<flattening>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0, ANGLEUNIT\["degree", 0.0174532925199433, ID\["EPSG", 9122\]\]\], ID\["IAU", (?P<iau_code_body>.*), (?P<iau_version_body>.*)\]\], (?P<conversion>.*), CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["(?P<longitude_name>.*)", (?P<longitude_asc>.*), ORDER\[1\], LENGTHUNIT\["metre", 1\]\], AXIS\["Northing \(N\)", (?P<latitude_asc>.*), ORDER\[2\], LENGTHUNIT\["metre", 1\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\]\]"""  # noqa: W605  # pylint: disable=W1401,C0301
    PROJ_CRS_TRI_OCEN_TEMPLATE = """PROJCRS\["(?P<projcrs>.*)", BASEGEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", TRIAXIAL\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<semi_median>.*), (?P<semi_minor>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0, ANGLEUNIT\["degree", 0.0174532925199433, ID\["EPSG", 9122\]\]\], ID\["IAU", (?P<iau_code_body>.*), (?P<iau_version_body>.*)\]\], (?P<conversion>.*), CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["(?P<longitude_name>.*)", (?P<longitude_asc>.*), ORDER\[1\], LENGTHUNIT\["metre", 1\]\], AXIS\["Northing \(N\)", (?P<latitude_asc>.*), ORDER\[2\], LENGTHUNIT\["metre", 1\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\]\]"""  # noqa: W605  # pylint: disable=W1401,C0301
    PROJ_CRS_TRI_OGRA_TEMPLATE = """PROJCRS\["(?P<projcrs>.*)", BASEGEOGCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", TRIAXIAL\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<semi_median>.*), (?P<semi_minor>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0, ANGLEUNIT\["degree", 0.0174532925199433, ID\["EPSG", 9122\]\]\], ID\["IAU", (?P<iau_code_body>.*), (?P<iau_version_body>.*)\]\], (?P<conversion>.*), CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["(?P<longitude_name>.*)", (?P<longitude_asc>.*), ORDER\[1\], LENGTHUNIT\["metre", 1\]\], AXIS\["Northing \(N\)", (?P<latitude_asc>.*), ORDER\[2\], LENGTHUNIT\["metre", 1\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\]\]"""  # noqa: W605  # pylint: disable=W1401,C0301

    MAPPING_TPL_ORICRS = {
        GEOCENTRIC_CRS_TEMPLATE: OCENTRIC,
        GEOGRAPHIC_CRS_TEMPLATE: OGRAPHIC,
        GEOCENTRIC_TRIAXIAL_TEMPLATE: OCENTRIC,
        GEOGRAPHIC_TRIAXIAL_TEMPLATE: OGRAPHIC,
        PROJ_CRS_BI_OCEN_TEMPLATE: OCENTRIC,
        PROJ_CRS_BI_OGRA_TEMPLATE: OGRAPHIC,
        PROJ_CRS_TRI_OCEN_TEMPLATE: OCENTRIC,
        PROJ_CRS_TRI_OGRA_TEMPLATE: OGRAPHIC,
    }

    TEMPLATES = MAPPING_TPL_ORICRS.keys()

    def __init__(self):
        self.__index: List[DatabaseRecord] = list()
        logger.info("Create database based on data/result.wkts")
        wkts: Dict[int, Dict[str, str]] = WktDatabase._load_wkts()
        for key in wkts:
            wkt = wkts[key]
            match, origin_ref = WktDatabase._parse(wkt)
            self._add_record(match, wkt, origin_ref)

    @property
    def index(self):
        """Records of the database"""
        return self.__index

    @staticmethod
    def _load_wkts() -> Dict[int, Dict[str, str]]:
        here = path.abspath(path.dirname(__file__))
        result: Dict[int, Dict[str, str]] = dict()
        with open(
            path.join(here, "..", "..", "..", "data/result.wkts"), "r"
        ) as file:
            wkts_content = file.read()
            wkts = wkts_content.split("\n\n")
            for idx, wkt in enumerate(wkts):
                result[idx] = dict()
                result[idx]["source"] = wkt
                wkt_processed = re.sub(r"\n\s*", " ", wkt)
                wkt_processed = re.sub(r"] ]", "]]", wkt_processed)
                result[idx]["db"] = wkt_processed
        return result

    @staticmethod
    def _parse(
        wkt: Dict[str, str]
    ) -> Tuple[Optional[re.Match], Optional[str]]:
        match: Optional[re.Match] = None
        origin_ref: Optional[str] = None
        for template in WktDatabase.TEMPLATES:
            m_regular = re.match(template, wkt["db"])
            if m_regular is None:
                origin_ref = None
                match = None
            else:
                origin_ref = WktDatabase.MAPPING_TPL_ORICRS[template]
                match = m_regular
                break
        return match, origin_ref

    def _add_record(
        self,
        match: Optional[re.Match],
        wkt: Dict[str, str],
        origin_ref: Optional[str],
    ):
        if match is None:
            logger.error(cast(Dict[str, str], wkt)["source"])
        else:
            proj: str
            try:
                proj = match.group("projcrs")
            except Exception:  # pylint: disable=W0703
                proj = "No projection"
            record = DatabaseRecord(
                match.group("geodcrs"),
                match.group("datum"),
                match.group("ellipsoid"),
                match.group("cs"),
                match.group("cs_nb"),
                match.group("latitude_asc"),
                match.group("longitude_asc"),
                "" if origin_ref is None else origin_ref,
                match.group("iau_code"),
                match.group("iau_version"),
                proj,
                cast(Dict[str, str], wkt)["source"],
            )
            self.__index.append(record)


@dataclass
class DatabaseRecord:  # pylint: disable=R0902
    """Columns of the database"""

    geodcrs: str
    datum: str
    ellipsoid: str
    cs: str  # pylint: disable=C0103
    cs_nb: str
    latitude_asc: str
    longitude_asc: str
    origin_crs: str
    iau_code: str
    iau_version: str
    projcrs: str
    wkt: str


class SqlDatabase:
    """WKT database as SQL"""

    def __init__(self):
        """Init"""
        self.__db_url: str = tortoise_config.db_url
        db_url_path: str = self.__db_url.replace("sqlite://", "")
        self.__db_path: str = path.abspath(path.join(getcwd(), db_url_path))

    @property
    def db_url(self) -> str:
        """The database URL.

        :getter: Returns the database URL
        :type: str
        """
        return self.__db_url

    @property
    def db_path(self) -> str:
        """The directory's path of the database.

        :getter: Returns directory's path
        :type: str
        """
        return self.__db_path

    async def create_db(self):
        """Create the WKT database"""
        await Tortoise.init(
            db_url=self.db_url, modules=tortoise_config.modules
        )
        await Tortoise.generate_schemas()
        wkt = WktDatabase()
        index = wkt.index
        logger.info("nb records : %s", len(index))
        for record in index:
            wkt_data = {
                "id": f"IAU:{record.iau_version}:{record.iau_code}",
                "version": int(record.iau_version),
                "code": int(record.iau_code),
                "solar_body": re.match(r"[^\s]+", record.datum).group(0),
                "datum_name": record.datum,
                "ellipsoid_name": record.ellipsoid,
                "projection_name": record.projcrs,
                "wkt": record.wkt,
            }
            await WKT_model.create(**wkt_data)
        await Tortoise.close_connections()
        logger.info("Database loaded")
