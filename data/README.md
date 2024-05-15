# GML Generator
The `gml_generator.py` script generates GML files using Apache SIS, from a set of WKTs listed in a file (`result.wkts`).

## Requirements
In order to run `gml_generator.py`:
* Make sure that the file `result.wkts` is in the same directory as `gml_generator.py`
* In `result.wkts` make sure that each WKT is separated by a double line break (`\n\n`)

## Running the script
To run the script, go to the project directory and run the following:
```bash
make generate-gml
```

### Parameters
When running the script, you will be prompted a few parameters:
* **Apache SIS**
    * If you have local installation of Apache SIS in the same directory as the script, with the format `apache-sis-1.4`, the script will automatically detect it and use this Apache SIS for GML generation.
    * Otherwise, you will be prompted the directory to a local installation of Apache SIS.
    * If you don't have local installation, Apache SIS will be downloaded (~12 MB). *Note: Apache SIS directory will be deleted once the script is completed.*
* **Remove all existing GML files:** Whether you want to remove all GML files in the output directory. This can be useful to make sure you do not keep previously-generated GML files.
* **Override existing GML files:** Whether you want to override existing GML files if they already exist.

*Note: The last two prompts are not displayed if the output directory is empty or doesn't exist.*

There will be a warning: `AVERTISSEMENT: La variable environnementale « SIS_DATA » n'est pas définie.` This references a variable used by the EPSG extension (for Apache SIS), which is not needed for IAU CRS. You can safely ignore that warning.

GML files are generated in the `gml` directory.
