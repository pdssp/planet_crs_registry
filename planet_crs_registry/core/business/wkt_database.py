# -*- coding: utf-8 -*-
import logging
import re
from dataclasses import dataclass
from typing import List
from enum import Enum

logger = logging.getLogger(__name__)


class WktDatabase:

    OGRAPHIC = "Ographic"
    OCENTRIC = "Ocentric"

    GEOCENTRIC_CRS_TEMPLATE = """GEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", ELLIPSOID\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<flattening>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0.0, ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\], CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["Planetocentric latitude \(U\)", (?P<latitude_asc>.*), ORDER\[1\], ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\], AXIS\["Planetocentric longitude \(V\)", (?P<longitude_asc>.*), ORDER\[2\], ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\], AXIS\["Radius \(R\)", up, ORDER\[3\], LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\], REMARK\["(?P<remark>).*"\]\]"""
    GEOGRAPHIC_CRS_TEMPLATE = """GEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", ELLIPSOID\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<flattening>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0.0, ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\], CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["Latitude \(B\)", (?P<latitude_asc>.*), ORDER\[1\]\], AXIS\["Longitude \(L\)", (?P<longitude_asc>.*), ORDER\[2\]\], ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\], REMARK\["(?P<remark>).*"\]\]"""
    GEOCENTRIC_TRIAXIAL_TEMPLATE = """GEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", TRIAXIAL\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<semi_median>.*), (?P<semi_minor>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0.0, ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\], CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["Planetocentric latitude \(U\)", (?P<latitude_asc>.*), ORDER\[1\], ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\], AXIS\["Planetocentric longitude \(V\)", (?P<longitude_asc>.*), ORDER\[2\], ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\], AXIS\["Radius \(R\)", up, ORDER\[3\], LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\], REMARK\["(?P<remark>).*"\]\]"""
    GEOGRAPHIC_TRIAXIAL_TEMPLATE = """GEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", TRIAXIAL\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<semi_median>.*), (?P<semi_minor>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0.0, ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\], CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["Latitude \(B\)", (?P<latitude_asc>.*), ORDER\[1\]\], AXIS\["Longitude \(L\)", (?P<longitude_asc>.*), ORDER\[2\]\], ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\], REMARK\["(?P<remark>).*"\]\]"""
    PROJ_CRS_BI_OCEN_TEMPLATE = """PROJCRS\["(?P<projcrs>.*)", BASEGEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", ELLIPSOID\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<flattening>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0.0, ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\]\],(?P<conversion>.*), CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["(?P<longitude_name>.*)", (?P<longitude_asc>.*), ORDER\[1\]\], AXIS\["Northing \(N\)", (?P<latitude_asc>.*), ORDER\[2\]\], LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\]\]"""
    PROJ_CRS_BI_OGRA_TEMPLATE = """PROJCRS\["(?P<projcrs>.*)", BASEGEOGCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", ELLIPSOID\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<flattening>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0.0, ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\]\],(?P<conversion>.*), CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["(?P<longitude_name>.*)", (?P<longitude_asc>.*), ORDER\[1\]\], AXIS\["Northing \(N\)", (?P<latitude_asc>.*), ORDER\[2\]\], LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\]\]"""
    PROJ_CRS_TRI_OCEN_TEMPLATE = """PROJCRS\["(?P<projcrs>.*)", BASEGEODCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", TRIAXIAL\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<semi_median>.*), (?P<semi_minor>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0.0, ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\]\],(?P<conversion>.*), CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["(?P<longitude_name>.*)", (?P<longitude_asc>.*), ORDER\[1\]\], AXIS\["Northing \(N\)", (?P<latitude_asc>.*), ORDER\[2\]\], LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\]\]"""
    PROJ_CRS_TRI_OGRA_TEMPLATE = """PROJCRS\["(?P<projcrs>.*)", BASEGEOGCRS\["(?P<geodcrs>.*)", DATUM\["(?P<datum>.*)", TRIAXIAL\["(?P<ellipsoid>.*)", (?P<semi_major>.*), (?P<semi_median>.*), (?P<semi_minor>.*), LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\]\](?P<anchor>.*)\], PRIMEM\["Reference Meridian", 0.0, ANGLEUNIT\["degree", 0.017453292519943295, ID\["EPSG", 9122\]\]\]\],(?P<conversion>.*), CS\[(?P<cs>.*), (?P<cs_nb>.*)\], AXIS\["(?P<longitude_name>.*)", (?P<longitude_asc>.*), ORDER\[1\]\], AXIS\["Northing \(N\)", (?P<latitude_asc>.*), ORDER\[2\]\], LENGTHUNIT\["metre", 1, ID\["EPSG", 9001\]\], ID\["IAU", (?P<iau_code>.*), (?P<iau_version>.*)\]\]"""

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
        wkts: List[str]
        logger.info("Create database based on data/result.wkts")
        with open("data/result.wkts", "r") as file:
            wkts_content = file.read()
            wkts = wkts_content.split("\n\n")
            for idx, wkt in enumerate(wkts):
                wkts[idx] = re.sub(r"\n\s*", " ", wkt)
                wkts[idx] = re.sub(r"] ]", "]]", wkts[idx])
        for wkt in wkts:
            match: re.Match
            origin_ref: str
            for template in WktDatabase.TEMPLATES:
                m = re.match(template, wkt)
                if m is None:
                    origin_ref = None
                    match = None
                    pass
                else:
                    origin_ref = WktDatabase.MAPPING_TPL_ORICRS[template]
                    match = m
                    break
            if match is None:
                logger.error(wkt)
            else:
                proj: str
                try:
                    proj = match.group("projcrs")
                except:
                    proj = None
                record = DatabaseRecord(
                    match.group("geodcrs"),
                    match.group("datum"),
                    match.group("ellipsoid"),
                    match.group("cs"),
                    match.group("cs_nb"),
                    match.group("latitude_asc"),
                    match.group("longitude_asc"),
                    origin_ref,
                    match.group("iau_code"),
                    match.group("iau_version"),
                    proj,
                    wkt,
                )
                self.__index.append(record)

    @property
    def index(self):
        return self.__index


@dataclass
class DatabaseRecord:
    geodcrs: str
    datum: str
    ellipsoid: str
    cs: str
    cs_nb: str
    latitude_asc: str
    longitude_asc: str
    origin_crs: str
    iau_code: str
    iau_version: str
    projcrs: str
    wkt: str
