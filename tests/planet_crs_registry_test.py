# -*- coding: utf-8 -*-
import argparse
import json
import logging
import os
import time

import pytest
import requests
import xmltodict

import planet_crs_registry
from planet_crs_registry import __author__  # pylint: disable=C0411
from planet_crs_registry import __copyright__  # pylint: disable=C0411
from planet_crs_registry import __description__  # pylint: disable=C0411
from planet_crs_registry import __version__  # pylint: disable=C0411
from planet_crs_registry.server import Server


class SmartFormatter(argparse.HelpFormatter):
    """Smart formatter for argparse - The lines are split for long text"""

    def _split_lines(self, text, width):
        if text.startswith("R|"):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def str2bool(string_to_test: str) -> bool:
    """Checks if a given string is a boolean

    Args:
        string_to_test (str): string to test

    Returns:
        bool: True when the string is a boolean otherwise False
    """
    return string_to_test.lower() in ("yes", "true", "t", "1")


def parse_cli() -> argparse.Namespace:
    """Parse command line inputs.

    Returns
    -------
    argparse.Namespace
        Command line options
    """
    path_to_file = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser(
        description=__description__,
        formatter_class=SmartFormatter,
        epilog=__author__ + " - " + __copyright__,
    )

    parser.register("type", "bool", str2bool)  # add type keyword to registries

    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    parser.add_argument(
        "--conf_file",
        default=os.path.join(path_to_file, "conf/planet_crs_registry.conf"),
        help="The location of the configuration file (default: %(default)s)",
    )

    parser.add_argument(
        "--level",
        choices=[
            "INFO",
            "DEBUG",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "TRACE",
        ],
        default="INFO",
        help="set Level log (default: %(default)s)",
    )

    parser.add_argument(
        "--use_cache",
        type="bool",  # type: ignore
        choices=[True, False],
        default=True,
        help="Use the created WKT database if True (default: %(default)s)",
    )
    return parser.parse_args([])


@pytest.fixture(scope="module")
def conn():
    options_cli = parse_cli()
    server = Server(options_cli)
    server.start()
    time.sleep(2)

    print("open connection")
    yield
    print("close connection")
    server.stop()


def test_name():
    print("Test name")
    name = planet_crs_registry.__name_soft__
    assert name == "planet_crs_registry"


def test_logger():
    print("Test logger")
    loggers = [logging.getLogger()]
    loggers = loggers + [
        logging.getLogger(name) for name in logging.root.manager.loggerDict
    ]
    assert loggers[0].name == "root"


def test_iau(conn):
    try:
        response = requests.get("http://localhost:8080/ws/IAU")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = response.content.decode("UTF-8")
        result = xmltodict.parse(content)
        assert (
            result["ns0:identifiers"]["ns0:identifier"]
            == "http://www.opengis.net/def/crs/IAU/2015"
        )
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_iau_2015(conn):
    try:
        response = requests.get("http://localhost:8080/ws/IAU/2015")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = response.content.decode("UTF-8")
        result = xmltodict.parse(content)
        assert (
            result["ns0:identifiers"]["ns0:identifier"][0]
            == "http://www.opengis.net/def/crs/IAU/2015/1000"
        )
        assert len(result["ns0:identifiers"]["ns0:identifier"]) == 2397
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_iau_2015_gml(conn):
    xml_2015_1000 = """
<gml:GeographicCRS xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gmd="http://www.isotc211.org/2005/gmd" gml:id="ogrcrs1">
   <gml:srsName>Sun (2015) - Sphere / Ocentric</gml:srsName>
   <gml:srsID>
      <gml:name codeSpace="urn:ogc:def:crs:IAU::">1000</gml:name>
   </gml:srsID>
   <gml:usesEllipsoidalCS>
      <gml:EllipsoidalCS gml:id="ogrcrs2">
         <gml:csName>ellipsoidal</gml:csName>
         <gml:csID>
            <gml:name codeSpace="urn:ogc:def:cs:EPSG::">6402</gml:name>
         </gml:csID>
         <gml:usesAxis>
            <gml:CoordinateSystemAxis gml:id="ogrcrs3" gml:uom="urn:ogc:def:uom:EPSG::9102">
               <gml:name>Geodetic latitude</gml:name>
               <gml:axisID>
                  <gml:name codeSpace="urn:ogc:def:axis:EPSG::">9901</gml:name>
               </gml:axisID>
               <gml:axisAbbrev>Lat</gml:axisAbbrev>
               <gml:axisDirection>north</gml:axisDirection>
            </gml:CoordinateSystemAxis>
         </gml:usesAxis>
         <gml:usesAxis>
            <gml:CoordinateSystemAxis gml:id="ogrcrs4" gml:uom="urn:ogc:def:uom:EPSG::9102">
               <gml:name>Geodetic longitude</gml:name>
               <gml:axisID>
                  <gml:name codeSpace="urn:ogc:def:axis:EPSG::">9902</gml:name>
               </gml:axisID>
               <gml:axisAbbrev>Lon</gml:axisAbbrev>
               <gml:axisDirection>east</gml:axisDirection>
            </gml:CoordinateSystemAxis>
         </gml:usesAxis>
      </gml:EllipsoidalCS>
   </gml:usesEllipsoidalCS>
   <gml:usesGeodeticDatum>
      <gml:GeodeticDatum gml:id="ogrcrs5">
         <gml:datumName>Sun (2015) - Sphere</gml:datumName>
         <gml:datumID>
            <gml:name codeSpace="urn:ogc:def:datum:IAU::">1000</gml:name>
         </gml:datumID>
         <gml:usesPrimeMeridian>
            <gml:PrimeMeridian gml:id="ogrcrs6">
               <gml:meridianName>Reference Meridian</gml:meridianName>
               <gml:meridianID>
                  <gml:name codeSpace="urn:ogc:def:meridian:IAU::">1000</gml:name>
               </gml:meridianID>
               <gml:greenwichLongitude>
                  <gml:angle uom="urn:ogc:def:uom:EPSG::9102">0</gml:angle>
               </gml:greenwichLongitude>
            </gml:PrimeMeridian>
         </gml:usesPrimeMeridian>
         <gml:usesEllipsoid>
            <gml:Ellipsoid gml:id="ogrcrs7">
               <gml:ellipsoidName>Sun (2015) - Sphere</gml:ellipsoidName>
               <gml:ellipsoidID>
                  <gml:name codeSpace="urn:ogc:def:ellipsoid:IAU::">1000</gml:name>
               </gml:ellipsoidID>
               <gml:semiMajorAxis uom="urn:ogc:def:uom:EPSG::9001">695700000</gml:semiMajorAxis>
               <gml:secondDefiningParameter>
                  <gml:inverseFlattening uom="urn:ogc:def:uom:EPSG::9201">0</gml:inverseFlattening>
               </gml:secondDefiningParameter>
            </gml:Ellipsoid>
         </gml:usesEllipsoid>
      </gml:GeodeticDatum>
   </gml:usesGeodeticDatum>
</gml:GeographicCRS>
    """
    try:
        response = requests.get("http://localhost:8080/ws/IAU/2015/1000")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = response.content.decode("UTF-8")
        result = xmltodict.parse(content)
        assert result == xmltodict.parse(xml_2015_1000)
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_wkts(conn):
    json_response = [
        {
            "created_at": "2022-10-16T08:24:50.274147+00:00",
            "id": "IAU:2015:1000",
            "version": 2015,
            "code": 1000,
            "solar_body": "Sun",
            "datum_name": "Sun (2015) - Sphere",
            "ellipsoid_name": "Sun (2015) - Sphere",
            "projection_name": "No projection",
            "wkt": 'GEOGCRS["Sun (2015) - Sphere / Ocentric",\n    DATUM["Sun (2015) - Sphere",\n    \tELLIPSOID["Sun (2015) - Sphere", 695700000, 0,\n\t\tLENGTHUNIT["metre", 1, ID["EPSG", 9001]]]],\n    \tPRIMEM["Reference Meridian", 0,\n            ANGLEUNIT["degree", 0.0174532925199433, ID["EPSG", 9122]]],\n\tCS[ellipsoidal, 2],\n\t    AXIS["geodetic latitude (Lat)", north,\n\t        ORDER[1],\n\t        ANGLEUNIT["degree", 0.0174532925199433]],\n\t    AXIS["geodetic longitude (Lon)", east,\n\t        ORDER[2],\n\t        ANGLEUNIT["degree", 0.0174532925199433]],\n\tID["IAU", 1000, 2015],\n\tREMARK["Source of IAU Coordinate systems: doi://10.1007/s10569-017-9805-5"]]',
        }
    ]
    try:
        response = requests.get(
            "http://localhost:8080/ws/wkts?limit=1&offset=0"
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = json.loads(response.text)
        assert content[0]["id"] == json_response[0]["id"]
        assert len(content) == 1
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_wkts_count(conn):
    try:
        response = requests.get("http://localhost:8080/ws/wkts/count")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = int(response.text)
        assert content == 4029
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_version(conn):
    json_response = [2015]
    try:
        response = requests.get("http://localhost:8080/ws/versions")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = json.loads(response.text)
        assert content[0] == json_response[0]
        assert len(content) == 1
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_version_2015(conn):
    json_response = [
        {
            "created_at": "2022-10-16T08:24:50.274147+00:00",
            "id": "IAU:2015:1000",
            "version": 2015,
            "code": 1000,
            "solar_body": "Sun",
            "datum_name": "Sun (2015) - Sphere",
            "ellipsoid_name": "Sun (2015) - Sphere",
            "projection_name": "No projection",
            "wkt": 'GEOGCRS["Sun (2015) - Sphere / Ocentric",\n    DATUM["Sun (2015) - Sphere",\n    \tELLIPSOID["Sun (2015) - Sphere", 695700000, 0,\n\t\tLENGTHUNIT["metre", 1, ID["EPSG", 9001]]]],\n    \tPRIMEM["Reference Meridian", 0,\n            ANGLEUNIT["degree", 0.0174532925199433, ID["EPSG", 9122]]],\n\tCS[ellipsoidal, 2],\n\t    AXIS["geodetic latitude (Lat)", north,\n\t        ORDER[1],\n\t        ANGLEUNIT["degree", 0.0174532925199433]],\n\t    AXIS["geodetic longitude (Lon)", east,\n\t        ORDER[2],\n\t        ANGLEUNIT["degree", 0.0174532925199433]],\n\tID["IAU", 1000, 2015],\n\tREMARK["Source of IAU Coordinate systems: doi://10.1007/s10569-017-9805-5"]]',
        }
    ]
    try:
        response = requests.get(
            "http://localhost:8080/ws/versions/2015?limit=1&offset=0"
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = json.loads(response.text)
        assert content[0]["id"] == json_response[0]["id"]
        assert len(content) == 1
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_version_2015_count(conn):
    try:
        response = requests.get("http://localhost:8080/ws/versions/2015/count")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = int(response.text)
        assert content == 4029
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_solar_bodies(conn):
    try:
        response = requests.get("http://localhost:8080/ws/solar_bodies")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = json.loads(response.text)
        print()
        assert "Mars" in content
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_solar_bodies_count(conn):
    try:
        response = requests.get("http://localhost:8080/ws/solar_bodies/count")
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = int(response.text)
        assert content == 97
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_solar_bodies_mars(conn):
    result_json = [
        {
            "created_at": "2022-10-16T08:24:57.603765+00:00",
            "id": "IAU:2015:49900",
            "version": 2015,
            "code": 49900,
            "solar_body": "Mars",
            "datum_name": "Mars (2015) - Sphere",
            "ellipsoid_name": "Mars (2015) - Sphere",
            "projection_name": "No projection",
            "wkt": 'GEOGCRS["Mars (2015) - Sphere / Ocentric",\n    DATUM["Mars (2015) - Sphere",\n    \tELLIPSOID["Mars (2015) - Sphere", 3396190, 0,\n\t\tLENGTHUNIT["metre", 1, ID["EPSG", 9001]]],\n\t\tANCHOR["Viking 1 lander : 47.95137 W"]],\n    \tPRIMEM["Reference Meridian", 0,\n            ANGLEUNIT["degree", 0.0174532925199433, ID["EPSG", 9122]]],\n\tCS[ellipsoidal, 2],\n\t    AXIS["geodetic latitude (Lat)", north,\n\t        ORDER[1],\n\t        ANGLEUNIT["degree", 0.0174532925199433]],\n\t    AXIS["geodetic longitude (Lon)", east,\n\t        ORDER[2],\n\t        ANGLEUNIT["degree", 0.0174532925199433]],\n\tID["IAU", 49900, 2015],\n\tREMARK["Use semi-major radius as sphere radius for interoperability. Source of IAU Coordinate systems: doi://10.1007/s10569-017-9805-5"]]',
        }
    ]
    try:
        response = requests.get(
            "http://localhost:8080/ws/solar_bodies/mars?limit=1&offset=0"
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = json.loads(response.text)
        assert content[0]["id"] == result_json[0]["id"]
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_solar_bodies_mars_count(conn):
    try:
        response = requests.get(
            "http://localhost:8080/ws/solar_bodies/mars/count"
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = int(response.text)
        assert content == 50
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_search_mars(conn):
    result_json = [
        {
            "created_at": "2022-10-16T08:24:57.603765+00:00",
            "id": "IAU:2015:49900",
            "version": 2015,
            "code": 49900,
            "solar_body": "Mars",
            "datum_name": "Mars (2015) - Sphere",
            "ellipsoid_name": "Mars (2015) - Sphere",
            "projection_name": "No projection",
            "wkt": 'GEOGCRS["Mars (2015) - Sphere / Ocentric",\n    DATUM["Mars (2015) - Sphere",\n    \tELLIPSOID["Mars (2015) - Sphere", 3396190, 0,\n\t\tLENGTHUNIT["metre", 1, ID["EPSG", 9001]]],\n\t\tANCHOR["Viking 1 lander : 47.95137 W"]],\n    \tPRIMEM["Reference Meridian", 0,\n            ANGLEUNIT["degree", 0.0174532925199433, ID["EPSG", 9122]]],\n\tCS[ellipsoidal, 2],\n\t    AXIS["geodetic latitude (Lat)", north,\n\t        ORDER[1],\n\t        ANGLEUNIT["degree", 0.0174532925199433]],\n\t    AXIS["geodetic longitude (Lon)", east,\n\t        ORDER[2],\n\t        ANGLEUNIT["degree", 0.0174532925199433]],\n\tID["IAU", 49900, 2015],\n\tREMARK["Use semi-major radius as sphere radius for interoperability. Source of IAU Coordinate systems: doi://10.1007/s10569-017-9805-5"]]',
        }
    ]
    try:
        response = requests.get(
            "http://localhost:8080/ws/search?search_term_kw=mars&limit=1&offset=0"
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = json.loads(response.text)
        assert content[0]["id"] == result_json[0]["id"]
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")


def test_search_mars_count(conn):
    try:
        response = requests.get(
            "http://localhost:8080/ws/search/count?search_term_kw=mars"
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        content = int(response.text)
        assert content == 51
    except requests.RequestException as e:
        raise ValueError(f"Error occurred during request: {str(e)}")
