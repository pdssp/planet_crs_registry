# -*- coding: utf-8 -*-
import logging
import os
import shutil
import tempfile
import zipfile
from re import findall

import jpype
import requests
from lxml import etree
from tqdm import tqdm


class ApacheJVM:
    """Apache JVM class containing the Java classes needed for GML generation,
    as well as the methods to start and stop the JVM."""

    def __init__(self, apache_sis_path):
        self.apache_sis_path = apache_sis_path
        self.CRS = None
        self.XML = None

    def __enter__(self):
        jpype.startJVM(classpath=[self.apache_sis_path])
        self.CRS = jpype.JClass("org.apache.sis.referencing.CRS")
        self.XML = jpype.JClass("org.apache.sis.xml.XML")
        logging.debug("Opened Apache JVM")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        jpype.shutdownJVM()
        logging.debug("Closed Apache JVM")


class GMLDataFiller:
    def __init__(self, gml: str, iau_version: str, code: str) -> None:
        self.root_tree = etree.fromstring(gml.encode("utf-8"))
        self.gml_ns = "{" + self.root_tree.nsmap["gml"] + "}"
        self.iau_version = iau_version
        self.code = code

    def get_gml(self) -> bytes:
        return etree.tostring(self.root_tree, pretty_print=True)

    def add_necessary_data(self) -> None:
        """Adds ``<gml:identifier>``,  ``<gml:scope>``, and ``<gml:formulaCitation>``
        to certain elements for GML validation."""
        logging.debug("Adding necessary data to GML...")

        self._add_scope_if_missing(
            self.root_tree,
            ["domainOfValidity", "remarks", "name", "identifier"],
        )

        conversion = self.root_tree.find(
            f"{self.gml_ns}conversion/{self.gml_ns}Conversion"
        )
        if conversion is not None:
            logging.debug("Found Conversion element")
            root_identifier = self.root_tree.find(f"{self.gml_ns}identifier")
            # Copies root identifier without moving it
            identifier = etree.fromstring(etree.tostring(root_identifier))
            conversion.insert(0, identifier)
            logging.debug("Copied identifier from root_tree to Conversion")

            self._add_scope_if_missing(
                conversion,
                ["domainOfValidity", "remarks", "name", "identifier"],
            )

            operation_method = conversion.find(
                f"{self.gml_ns}method/{self.gml_ns}OperationMethod"
            )
            if operation_method is not None:
                logging.debug("Found OperationMethod element")
                self._add_identifier_if_missing(operation_method, "method")
                self._add_formula_citation_if_missing(
                    operation_method, ["remarks", "name", "identifier"]
                )
                self._remove_erroneous_parameters(operation_method)

        cartesian_cs = self.root_tree.find(
            f"{self.gml_ns}cartesianCS/{self.gml_ns}CartesianCS"
        )
        if cartesian_cs is not None:
            logging.debug("Found CartesianCS element")
            self._add_identifier_if_missing(cartesian_cs, "cs")
            self._add_identifier_on_axis(cartesian_cs)

        spherical_cs = self.root_tree.find(
            f"{self.gml_ns}sphericalCS/{self.gml_ns}SphericalCS"
        )
        if spherical_cs is not None:
            logging.debug("Found SphericalCS element")
            self._add_identifier_if_missing(spherical_cs, "cs")
            self._add_identifier_on_axis(spherical_cs)

        geodetic_prefix = ""

        geodetic_crs_str = (
            f"{self.gml_ns}baseGeodeticCRS/{self.gml_ns}GeodeticCRS"
        )
        geodetic_crs = self.root_tree.find(geodetic_crs_str)
        if geodetic_crs is not None:
            logging.debug("Found GeodeticCRS element")
            self._add_scope_if_missing(
                geodetic_crs,
                ["domainOfValidity", "remarks", "name", "identifier"],
            )
            geodetic_prefix = f"{geodetic_crs_str}/"

        ellipsoidal_cs = self.root_tree.find(
            f"{geodetic_prefix}{self.gml_ns}ellipsoidalCS/{self.gml_ns}EllipsoidalCS"
        )
        if ellipsoidal_cs is not None:
            logging.debug("Found EllipsoidalCS element")
            self._add_identifier_if_missing(ellipsoidal_cs, "cs")
            self._add_identifier_on_axis(ellipsoidal_cs)

        geodetic_datum = self.root_tree.find(
            f"{geodetic_prefix}{self.gml_ns}geodeticDatum/{self.gml_ns}GeodeticDatum"
        )
        if geodetic_datum is not None:
            logging.debug("Found GeodeticDatum element")
            self._add_identifier_if_missing(geodetic_datum, "datum")
            self._add_scope_if_missing(
                geodetic_datum,
                ["domainOfValidity", "remarks", "name", "identifier"],
            )

            prime_meridian = geodetic_datum.find(
                f"{self.gml_ns}primeMeridian/{self.gml_ns}PrimeMeridian"
            )
            if prime_meridian is not None:
                logging.debug("Found PrimeMeridian element")
                self._add_identifier_if_missing(prime_meridian, "meridian")

            ellipsoid = geodetic_datum.find(
                f"{self.gml_ns}ellipsoid/{self.gml_ns}Ellipsoid"
            )
            if ellipsoid is not None:
                logging.debug("Found Ellipsoid element")
                self._add_identifier_if_missing(ellipsoid, "ellipsoid")

    def _insert_element_after(
        self,
        element: etree.Element,
        element_to_insert: etree.Element,
        prev_elem_name_list: list[str],
    ) -> None:
        """Internal function: Insert a given element into another element after a given element.

        :param element: lxml.etree.Element to add the element into
        :param element_to_insert: Element to insert
        :param prev_elem_name_list: List of elements (str) you want to insert the element after,
            picks whichever is there first, and pick the last iteration of the element
        """
        for previous_element_name in prev_elem_name_list:
            all_elems = element.findall(self.gml_ns + previous_element_name)
            if len(all_elems) >= 1:
                index = element.index(all_elems[-1]) + 1
                break
        else:
            index = 0

        element.insert(index, element_to_insert)

    def _add_scope_if_missing(
        self, element: etree.Element, prev_elem_name_list: list[str]
    ) -> None:
        """Internal function: Adds ``<gml:scope>`` in the given element if it is missing.

        :param element: lxml.etree.Element to add the scope into
        :param prev_elem_name_list: List of elements (str) you want to insert the element after,
            picks whichever is there first, and pick the last iteration of the element
        """
        scope = element.find(f"{self.gml_ns}scope")
        if scope is not None:
            return

        # TODO: Replace with a non-placeholder scope
        scope_element = etree.Element(f"{self.gml_ns}scope")
        scope_element.text = "not known"

        self._insert_element_after(element, scope_element, prev_elem_name_list)
        logging.debug(f"Added scope to {element.tag.split('}')[1]}")

    def _add_formula_citation_if_missing(
        self, element: etree.Element, prev_elem_name_list: list[str]
    ) -> None:
        """Internal function: Adds ``<gml:formulaCitation>`` in the given element if it doesn't contain
        either ``<gml:formula>`` or ``<gml:formulaCitation>``.

        :param element: lxml.etree.Element to add the formulaCitation into
        :param prev_elem_name_list: List of elements (str) you want to insert the element after,
            picks whichever is there first, and pick the last iteration of the element
        """
        formula = element.find(f"{self.gml_ns}formula")
        formula_citation = element.find(f"{self.gml_ns}formulaCitation")
        if formula is not None or formula_citation is not None:
            return

        formula_citation_xml_str = f"""<gml:formulaCitation
        xmlns:gml="{self.root_tree.nsmap["gml"]}"
        xmlns:gmd="{self.root_tree.nsmap["gmd"]}"
        xmlns:gco="{self.root_tree.nsmap["gcol"]}">
<gmd:CI_Citation>
  <gmd:title>
    <gco:CharacterString>Planetary CRS formulas</gco:CharacterString>
  </gmd:title>
  <gmd:date>
    <gmd:CI_Date>
      <gmd:date>
        <gco:DateTime>2024-04-25T09:00:00+02:00</gco:DateTime>
      </gmd:date>
      <gmd:dateType>
        <gmd:CI_DateTypeCode codeList="https://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_DateTypeCode" codeListValue="publication">publication</gmd:CI_DateTypeCode>
      </gmd:dateType>
    </gmd:CI_Date>
  </gmd:date>
  <gmd:otherCitationDetails>
    <gco:CharacterString>Document available online at http://voparis-vespa-crs.obspm.fr:8080/web/formula.html</gco:CharacterString>
  </gmd:otherCitationDetails>
</gmd:CI_Citation>
</gml:formulaCitation>"""

        formula_citation_element = etree.fromstring(
            formula_citation_xml_str, etree.XMLParser(remove_blank_text=True)
        )

        self._insert_element_after(
            element, formula_citation_element, prev_elem_name_list
        )
        logging.debug(f"Added formulaCitation to {element.tag.split('}')[1]}")

    def _add_identifier_if_missing(
        self, element: etree.Element, elem_type: str
    ) -> None:
        """Internal function: Adds ``<gml:identifier>`` in the given element if it is missing.

        :param element: lxml.etree.Element to add the identifier into
        :param elem_type: Type of element in the URN
        """
        identifier = element.find(f"{self.gml_ns}identifier")
        if identifier is not None:
            return

        identifier_element = etree.Element(
            f"{self.gml_ns}identifier", codeSpace="NAIF"
        )
        identifier_element.text = (
            f"urn:ogc:def:{elem_type}:NAIF:{self.iau_version}:{self.code[:-2]}"
        )
        element.insert(0, identifier_element)
        logging.debug(f"Added identifier to {element.tag.split('}')[1]}")

    def _add_identifier_on_axis(self, element: etree.Element) -> None:
        """Internal function: Adds ``<gml:identifier>`` to axis if they don't have it.

        :param element: lxml.etree.Element to add the identifier into
        """
        axis = element.findall(f"{self.gml_ns}axis")
        if len(axis) == 0:
            return
        for ax in axis:
            coord = ax.find(f"{self.gml_ns}CoordinateSystemAxis")
            if coord is None:
                continue
            identifier = coord.find(f"{self.gml_ns}identifier")
            if identifier is not None:
                continue

            # TODO: Find corresponding EPSG code for all axis
            axis_type = coord.get(f"{self.gml_ns}id")
            axis_to_epsg_code = {
                "GeodeticLatitude": "9901",  # 106
                "GeodeticLongitude": "9902",  # 107
                "Easting": "9906",  # 1
                "Northing": "9907",  # 2
                "Westing": "9908",
                "Southing": "9908",
                "planetocentricLatitude": "UNDEFINED",
                "planetocentricLongitude": "UNDEFINED",
            }
            epsg_code = axis_to_epsg_code[axis_type]
            identifier_element = etree.Element(
                f"{self.gml_ns}identifier", codeSpace="IOGP"
            )
            identifier_element.text = f"urn:ogc:def:axis:EPSG::{epsg_code}"
            coord.insert(0, identifier_element)
            logging.debug(
                f"Added identifier to {coord.tag.split('}')[1]} (axis)"
            )

    def _remove_erroneous_parameters(self, element: etree.Element) -> None:
        """Internal function: Removes parameters which do not contain an EPSG code.

        :param element: lxml.etree.Element to clean the parameters from
        """
        parameters = element.findall(f"{self.gml_ns}parameter")
        if len(parameters) == 0:
            return
        for param in parameters:
            operation_parameter = param.find(
                f"{self.gml_ns}OperationParameter"
            )
            if operation_parameter is None:
                continue

            param_id = operation_parameter.get(f"{self.gml_ns}id")
            if not param_id.startswith("epsg-parameter-"):
                element.remove(param)
                logging.debug(
                    f"Parameter removed for {element.tag.split('}')[1]}"
                )


def _remove_xml_files_in_directory(path_to_directory: str) -> None:
    """Internal function: Delete all XML files in a given directory.

    :param path_to_directory: String of the directory
    """
    for file_name in os.listdir(path_to_directory):
        file_path = os.path.join(path_to_directory, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".xml"):
            os.remove(file_path)


def _get_input_yes_no(prompt: str) -> bool:
    """Internal function: Prompt the user for a "yes / no" input.
    :param prompt: The input prompt message
    :return: Boolean indicating the user's choice
    """
    while True:
        user_input = input(f"{prompt} (yes/y/no/n): ").lower()
        if user_input in ["yes", "y"]:
            return True
        elif user_input in ["no", "n"]:
            return False
        else:
            print("Invalid input. Please enter 'yes' (y) or 'no' (n).")


def _get_input_apache_sis_directory() -> str | None:
    """Internal function: Prompt the user if they have a local installation of Apache SIS.
    If they do, ask for the path of the Apache SIS directory.

    :return: Path to Apache SIS directory or None
    """
    local_apache_sis_flag = _get_input_yes_no(
        "Do you have a local installation of Apache SIS?"
    )
    if local_apache_sis_flag is False:
        return None

    while True:
        user_input = input(
            "Enter the directory path to the local Apache SIS installation (the directory that contains 'lib'): "
        )
        if os.path.isdir(user_input):
            lib_path = os.path.join(user_input, "lib")
            if os.path.isdir(lib_path):
                return user_input
            else:
                print(
                    "The entered directory does not contain a 'lib' directory. Please try again."
                )
        else:
            print("Invalid directory path. Please try again.")


def _get_user_choices(output_directory: str) -> tuple[bool, bool]:
    """Internal function: Prompt the user for reset and override flags.

    :return: Two booleans: reset and override flags
    """
    directory_has_no_files = len(os.listdir(output_directory)) == 0
    if directory_has_no_files:
        return False, False

    reset_directory_flag = _get_input_yes_no(
        "Do you want to remove all existing GML files?"
    )
    if reset_directory_flag is True:
        return True, True

    override_file_flag = _get_input_yes_no(
        "Do you want to override existing GML files?"
    )

    return reset_directory_flag, override_file_flag


def get_apache_sis_path(
    apache_sis_directory: str, apache_sis_version: str
) -> tuple[bool, list[str]]:
    """Return the Apache SIS path, either from: directory already in current context,
    directory given as input, or downloaded via Apache's website.

    :param apache_sis_directory: Apache SIS directory name
    :param apache_sis_version: Apache SIS version
    :return: Boolean indicating if we created a temporary directory and a path to Apache SIS
    """
    if os.path.exists(apache_sis_directory):
        logging.info("Apache SIS obtained locally from existing directory")
        return False, [apache_sis_directory]

    input_apache_sis_directory = _get_input_apache_sis_directory()

    if input_apache_sis_directory is not None:
        logging.info("Apache SIS obtained locally from given directory")
        return False, [input_apache_sis_directory]

    _APACHE_URL = f"https://dlcdn.apache.org/sis/{apache_sis_version}/apache-sis-{apache_sis_version}-bin.zip"
    try:
        apache_download_msg = (
            f"Apache SIS version {apache_sis_version}: downloading..."
        )
        print(apache_download_msg)
        logging.info(apache_download_msg)

        response = requests.get(_APACHE_URL)
        response.raise_for_status()  # Raise an exception for bad response status codes

        apache_download_msg = (
            f"Apache SIS version {apache_sis_version}: download complete."
        )
        print(apache_download_msg)
        logging.info(apache_download_msg)

        temp_dir = tempfile.mkdtemp()

        temp_zip_file = os.path.join(temp_dir, "apache.zip")
        with open(temp_zip_file, "wb") as f:
            f.write(response.content)
        with zipfile.ZipFile(temp_zip_file, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        os.remove(temp_zip_file)

        return True, [temp_dir, f"apache-sis-{apache_sis_version}"]

    except Exception as e:
        shutil.rmtree(temp_dir)
        raise Exception(f"An unexpected error occurred: {e}")


def generate_gml_file_from_wkt(
    apache_jvm: ApacheJVM,
    path_to_directory: str,
    wkt: str,
    override_file_flag: bool,
) -> None:
    """Using ApacheSIS and from a given WKT, create a GML file in the XML format.
    Name of the file follows this format: ``IAU_(iau_version)_(code).xml``

    :param apache_jvm: Apache JVM containing the classes needed for GML generation
    :param path_to_directory: Where the GML is generated
    :param wkt: Input WKT
    :param override_file_flag: Whether the user wants to override the file if it already exists
    """
    # TODO: Placeholder "replace()" -> remove when ApacheSIS is updated.
    wkt = wkt.replace("GEOGCRS", "GEODCRS")

    try:
        # Matching the last iteration of "ID" in the WKT
        lines = wkt.split("\n")[::-1]
        for line in lines:
            line = line.strip()
            if line.startswith("ID["):
                matches = findall(r"\b\d+\b", line)
                if len(matches) == 2:
                    code, iau_version = matches
                    break
                else:
                    raise ValueError("Unexpected format in the 'ID' line.")
        else:
            raise ValueError("No 'ID' line found in the WKT.")
    except ValueError as e:
        raise ValueError(f"Error: {e}")

    path_to_file = f"{path_to_directory}/IAU_{iau_version}_{code}.xml"
    wkt_first_line = wkt.split("\n")[0]
    logging.debug(f"{path_to_file} // WKT: {wkt_first_line}")

    if override_file_flag is False:
        if os.path.exists(path_to_file):
            logging.debug(f"File {path_to_file} already exists")
            return

    try:
        logging.debug("Calling Apache SIS methods...")
        # Apache SIS conversion from WKT to GML
        crs = apache_jvm.CRS.fromWKT(wkt)
        gml = str(apache_jvm.XML.marshal(crs))
        logging.debug("Call to Apache SIS methods completed")

        logging.debug("Calling GMLDataFiller...")
        data_filler = GMLDataFiller(gml, iau_version, code)
        data_filler.add_necessary_data()
        logging.debug("Call to GMLDataFiller completed")

        gml = data_filler.get_gml()
        logging.debug(f"Return GML as type '{type(gml).__name__}'")

        with open(path_to_file, mode="wb") as output_file:
            output_file.write(gml)
            logging.debug("GML written to file")

    except jpype.JException as ex:
        logging.error(f"Java error: {ex.message()}")

    except FileNotFoundError:
        raise FileNotFoundError("Error: File or directory not found.")

    except Exception as e:
        raise RuntimeError(f"Error: An unexpected error occurred - {str(e)}")


def generate_all_gml_files(
    apache_jvm: ApacheJVM, wkt_file: str, output_directory: str
) -> None:
    """Generate all GML files using the ``generate_gml_file_from_wkt()`` function.

    :param apache_jvm: Apache JVM containing the classes needed for GML generation
    :param wkt_file: Path to the WKT file
    :param output_directory: Where the GML files are generated
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    reset_flag, override_flag = _get_user_choices(output_directory)
    logging.info(
        f"User choices - remove all: {reset_flag} / override files: {override_flag}"
    )

    if reset_flag is True:
        _remove_xml_files_in_directory(output_directory)
        logging.debug("Removed all XML files in directory")

    with open(wkt_file, mode="r") as file:
        wkts = file.read().split("\n\n")

    # tqdm for visual representation of the process
    for wkt_content in tqdm(wkts, desc="Generating GML files", unit="files"):
        generate_gml_file_from_wkt(
            apache_jvm, output_directory, wkt_content, override_flag
        )


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))

    logging.basicConfig(
        filename=os.path.join(script_dir, "gml_generator.log"),
        level=logging.INFO,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(module)s (%(funcName)s): %(message)s",
        datefmt="%Y/%m/%d-%H:%M:%S",
    )

    # Using Apache SIS to generate the GML files
    _APACHE_SIS_VERSION = "1.4"
    _APACHE_SIS_DIRECTORY = os.path.join(
        script_dir, f"apache-sis-{_APACHE_SIS_VERSION}"
    )
    _APACHE_SIS_LIB_PATH = ["lib", "*"]

    temp_dir_flag, _apache_sis_path = get_apache_sis_path(
        _APACHE_SIS_DIRECTORY, _APACHE_SIS_VERSION
    )

    apache_libs = os.path.join(*_apache_sis_path, *_APACHE_SIS_LIB_PATH)

    try:
        with ApacheJVM(apache_libs) as apache_jvm:
            logging.info("Generating all GML files...")
            generate_all_gml_files(
                apache_jvm,
                os.path.join(script_dir, "result.wkts"),
                os.path.join(script_dir, "gml"),
            )
            logging.info("All GML files generated")
    finally:
        if temp_dir_flag:
            shutil.rmtree(_apache_sis_path[0])
            logging.debug(
                "Deleted temporary directory used for downloaded Apache SIS"
            )


if __name__ == "__main__":
    main()
