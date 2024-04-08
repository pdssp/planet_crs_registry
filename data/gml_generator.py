import os
from re import findall
from tqdm import tqdm

from _version import __apache_sis__

import jpype
import jpype.imports
from jpype.types import *


def _remove_files_in_directory(directory: str) -> None:
    """Internal function: Delete all files in a given directory.

    :param directory: String of the directory
    """
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)


def _get_user_input() -> tuple[bool, bool]:
    """Internal function: Prompt the user for reset and override flags.

    :return: Two booleans: reset and override flags
    """
    reset_directory_flag = None
    override_file_flag = None

    while reset_directory_flag is None:
        reset_directory_input = input("Do you want to remove all existing GML files? (yes/y/no/n): ").lower()
        if reset_directory_input in ['yes', 'y']:
            reset_directory_flag = True
        elif reset_directory_input in ['no', 'n']:
            reset_directory_flag = False
        else:
            print("Invalid input. Please enter 'yes' (y) or 'no' (n).")

    if reset_directory_flag is True:
        override_file_flag = True
    else:
        while override_file_flag is None:
            override_file_input = input("Do you want to override existing GML files? (yes/y/no/n): ").lower()
            if override_file_input in ['yes', 'y']:
                override_file_flag = True
            elif override_file_input in ['no', 'n']:
                override_file_flag = False
            else:
                print("Invalid input. Please enter 'yes' (y) or 'no' (n).")

    return reset_directory_flag, override_file_flag


def generate_gml_file_from_wkt(wkt: str, override_file_flag: bool) -> None:
    """Using ApacheSIS and from a given WKT, create a GML file in the XML format.
    Files are put in the "gml" directory.
    Name of the file follows this format: ``IAU_(iau_version)_(code).xml``

    :param wkt: Input WKT
    :param override_file_flag: Whether the user wants to override existing files
    """
    try:
        lines = wkt.split('\n')[::-1]
        for line in lines:
            line = line.strip()
            if line.startswith('ID['):
                matches = findall(r'\b\d+\b', line)
                if len(matches) == 2:
                    iau_version, code = matches
                    break
                else:
                    raise ValueError("Unexpected format in the 'ID' line.")
        else:
            raise ValueError("No 'ID' line found in the WKT.")
    except ValueError as e:
        print(f"Error: {e}")
        return

    path_to_file = f"gml/IAU_{iau_version}_{code}.xml"

    if override_file_flag is False:
        if os.path.exists(path_to_file):
            return

    # TODO: Placeholder replace(). Remove when ApacheSIS is updated.
    wkt = wkt.replace("GEOGCRS", "GEODCRS")

    try:
        crs = CRS.fromWKT(wkt)
        result = str(XML.marshal(crs))

        with open(f"gml/IAU_{iau_version}_{code}.xml", mode='w') as output_file:
            output_file.write(result)

    except jpype.JException as ex:
        raise RuntimeError(f"Java error: {ex.message()}")

    except FileNotFoundError:
        raise FileNotFoundError("Error: File or directory not found.")

    except Exception as e:
        raise RuntimeError(f"Error: An unexpected error occurred - {str(e)}")


def generate_all_gml_files():
    directory_has_files = len(os.listdir("gml")) > 0
    if directory_has_files:
        reset_flag, override_flag = _get_user_input()
    else:
        reset_flag, override_flag = False, False

    if reset_flag is True:
        _remove_files_in_directory("gml")

    with open("result.wkts", mode='r') as file:
        wkts = file.read().split("\n\n")

    # tqdm for visual representation of the process
    for wkt_content in tqdm(wkts, desc="Generating GML files", unit="files"):
        generate_gml_file_from_wkt(wkt_content, override_flag)


if __name__ == "__main__":
    # Using ApacheSIS to generate the GML
    jpype.startJVM(classpath=[f"../apache-sis-{__apache_sis__}/lib/*"])

    # Java imports for ApacheSIS
    from org.apache.sis.referencing import CRS
    from org.apache.sis.xml import XML

    generate_all_gml_files()

    jpype.shutdownJVM()
