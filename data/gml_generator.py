# -*- coding: utf-8 -*-
import os
from re import findall

import jpype.imports
from tqdm import tqdm


def _remove_xml_files_in_directory(path_to_directory: str) -> None:
    """Internal function: Delete all XML files in a given directory.

    :param path_to_directory: String of the directory
    """
    for file_name in os.listdir(path_to_directory):
        file_path = os.path.join(path_to_directory, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".xml"):
            os.remove(file_path)


def _get_yes_no_input(prompt: str) -> bool:
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


def _get_user_choices() -> tuple[bool, bool]:
    """Internal function: Prompt the user for reset and override flags.

    :return: Two booleans: reset and override flags
    """
    reset_directory_flag = _get_yes_no_input(
        "Do you want to remove all existing GML files?"
    )
    if reset_directory_flag is True:
        return True, True

    override_file_flag = _get_yes_no_input(
        "Do you want to override existing GML files?"
    )

    return reset_directory_flag, override_file_flag


def generate_gml_file_from_wkt(
    path_to_directory: str, wkt: str, override_file_flag: bool
) -> None:
    """Using ApacheSIS and from a given WKT, create a GML file in the XML format.
    Name of the file follows this format: ``IAU_(iau_version)_(code).xml``

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
        # ApacheSIS: getting the GML from WKT
        crs = CRS.fromWKT(wkt)
        result = str(XML.marshal(crs))

        with open(path_to_file, mode="w") as output_file:
            output_file.write(result)

    except jpype.JException as ex:
        raise RuntimeError(f"Java error: {ex.message()}")

    except FileNotFoundError:
        raise FileNotFoundError("Error: File or directory not found.")

    except Exception as e:
        raise RuntimeError(f"Error: An unexpected error occurred - {str(e)}")


def generate_all_gml_files(path_to_directory: str) -> None:
    """Generate all GML files using the ``generate_gml_file_from_wkt()`` function.

    :param path_to_directory: Where the GML files are generated
    """
    directory_has_files = len(os.listdir(path_to_directory)) > 0
    if directory_has_files:
        reset_flag, override_flag = _get_user_choices()
    else:
        reset_flag, override_flag = False, False

    if reset_flag is True:
        _remove_xml_files_in_directory(path_to_directory)

    with open("result.wkts", mode="r") as file:
        wkts = file.read().split("\n\n")

    # tqdm for visual representation of the process
    for wkt_content in tqdm(wkts, desc="Generating GML files", unit="files"):
        generate_gml_file_from_wkt(
            path_to_directory, wkt_content, override_flag
        )


if __name__ == "__main__":
    # Using ApacheSIS to generate the GML files
    _APACHE_SIS_VERSION = "1.4"
    _APACHE_SIS_PATH = f"apache-sis-{_APACHE_SIS_VERSION}-bin/apache-sis-{_APACHE_SIS_VERSION}/lib/*"
    jpype.startJVM(classpath=[_APACHE_SIS_PATH])
    from org.apache.sis.referencing import CRS
    from org.apache.sis.xml import XML

    _GENERATED_GML_PATH = "gml"
    generate_all_gml_files(_GENERATED_GML_PATH)

    jpype.shutdownJVM()
