# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
import zipfile
from re import findall

import jpype
import requests
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
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        jpype.shutdownJVM()


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
        return False, [apache_sis_directory]

    input_apache_sis_directory = _get_input_apache_sis_directory()

    if input_apache_sis_directory is not None:
        return False, [input_apache_sis_directory]

    _APACHE_URL = f"https://dlcdn.apache.org/sis/{apache_sis_version}/apache-sis-{apache_sis_version}-bin.zip"
    try:
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            print(f"Downloading Apache SIS version {apache_sis_version}...")
            response = requests.get(_APACHE_URL)
            response.raise_for_status()  # Raise an exception for bad response status codes
            print("Download complete.")

            temp_zip_file = os.path.join(temp_dir, "apache.zip")
            with open(temp_zip_file, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(temp_zip_file, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            os.remove(temp_zip_file)

            return True, [temp_dir, apache_sis_directory]

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
    # TODO: Placeholder replace(). Remove when ApacheSIS is updated.
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

    if override_file_flag is False:
        if os.path.exists(path_to_file):
            return

    try:
        # Apache SIS conversion from WKT to GML
        crs = apache_jvm.CRS.fromWKT(wkt)
        result = str(apache_jvm.XML.marshal(crs))

        with open(path_to_file, mode="w") as output_file:
            output_file.write(result)

    except jpype.JException as ex:
        raise RuntimeError(f"Java error: {ex.message()}")

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

    if reset_flag is True:
        _remove_xml_files_in_directory(output_directory)

    with open(wkt_file, mode="r") as file:
        wkts = file.read().split("\n\n")

    # tqdm for visual representation of the process
    for wkt_content in tqdm(wkts, desc="Generating GML files", unit="files"):
        generate_gml_file_from_wkt(
            apache_jvm, output_directory, wkt_content, override_flag
        )


def main() -> None:
    # Using Apache SIS to generate the GML files
    _APACHE_SIS_VERSION = "1.4"
    _APACHE_SIS_DIRECTORY = f"apache-sis-{_APACHE_SIS_VERSION}"
    _APACHE_SIS_LIB_PATH = ["lib", "*"]

    temp_dir_flag, _apache_sis_path = get_apache_sis_path(
        _APACHE_SIS_DIRECTORY, _APACHE_SIS_VERSION
    )

    apache_libs = os.path.join(*_apache_sis_path, *_APACHE_SIS_LIB_PATH)

    try:
        with ApacheJVM(apache_libs) as apache_jvm:
            generate_all_gml_files(apache_jvm, "result.wkts", "gml")
    finally:
        if temp_dir_flag:
            shutil.rmtree(_apache_sis_path[0])


if __name__ == "__main__":
    main()
