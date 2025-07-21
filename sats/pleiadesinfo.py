#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Information retrieval from ASP raw folder (based on DIM)


Usage:
    pleiadesinfo.py <folder> [--kml]
    pleiadesinfo.py -h | --help

Options:
    -h --help       Show this screen
    <folder>        Pleides data folder (or DIM)
    --kml           Export the track countouring kml
"""

import os
import glob
import docopt
import xml.etree.ElementTree as ET
from plistlib import InvalidFileException


def parse_xml(file: str):
    """
    Parse an XML file into a root element

    :param file: path to the xml to parse
    :returns root: the root xml object
    """
    tree = ET.parse(file)
    root = tree.getroot()
    return root


def resolve_dim(folder: str):
    if os.path.isdir(folder):
        dim = glob.glob(os.path.join(folder, "DIM*.XML"))
        if len(dim) != 1:
            raise FileNotFoundError("Cannot resolve DIM")
        else:
            dim = dim[0]
    elif os.path.isfile(folder):
        dim = folder
    else:
        raise InvalidFileException("folder is neither an actual folder nor a file")
    return dim


class PleiadesDisplay:
    def __init__(self, folder):
        dim = resolve_dim(folder)
        self.dim = parse_xml(dim)

        self.is_folder_complete = False
        self.vrt_file = None

        self.dataset_name = self.get("./Dataset_Identification/DATASET_NAME")
        self.copyright = self.get(
            "./Dataset_Identification/Legal_Constraints/COPYRIGHT"
        )
        self.imaging_date = self.get(
            "./Dataset_Sources/Source_Identification/Strip_Source/IMAGING_DATE"
        )
        self.imaging_time = self.get(
            "./Dataset_Sources/Source_Identification/Strip_Source/IMAGING_TIME"
        )
        self.job_id = self.get("./Product_Information/Delivery_Identification/JOB_ID")
        self.dim_path = dim
        self.dim_version = self.get(
            "./Metadata_Identification/METADATA_FORMAT", "version"
        )
        self.rpc_path = self.get(
            "./Geoposition/Geoposition_Models/Rational_Function_Model/Component/COMPONENT_PATH",
            "href",
        )
        self.nrow = self.get("./Raster_Data/Raster_Dimensions/NROWS")
        self.ncol = self.get("./Raster_Data/Raster_Dimensions/NCOLS")
        self.data_type = self.get("./Raster_Data/Raster_Encoding/DATA_TYPE")
        self.nbits = self.get("./Raster_Data/Raster_Encoding/NBITS")
        self.sign = self.get("./Raster_Data/Raster_Encoding/SIGN")
        self.special_values = None
        self.value_min = None
        self.value_max = None
        self.value_mean = None
        self.value_std = None
        self.area = self.get("./Dataset_Content/SURFACE_AREA")
        self.cloud = self.get("./Dataset_Content/CLOUD_COVERAGE")
        self.snow = self.get("./Dataset_Content/SNOW_COVERAGE")
        self.crs = None
        self.acqu_angles = None
        self.solar_inc = None
        self.gsd = None
        self.bound_geom, self.bound_coord = self.get_geom()

    def get(self, value: str, attrib: None | str = None):
        fetch = self.dim.find(value)
        if fetch is None:
            return None

        if attrib is None:
            return fetch.text
        else:
            return fetch.attrib[attrib]

    def get_geom(self):
        vertex = self.dim.findall("./Dataset_Content/Dataset_Extent/Vertex")
        if vertex is None:
            return None, None
        latlon = [[v.find(".LAT").text, v.find(".LON").text] for v in vertex]
        coordxy = [[v.find(".COL").text, v.find(".ROW").text] for v in vertex]
        return latlon, coordxy

    def display(self):
        message = "Pleiadesinfo: {}\n\n".format(self.dataset_name)
        message += "date: {} {}\n".format(self.imaging_date, self.imaging_time)
        message += "DIM (v{}): {}\n".format(self.dim_version, self.dim_path)
        message += "nrow, ncol: {}, {}\n".format(self.nrow, self.ncol)
        message += "datatype: {} {} {}\n".format(self.data_type, self.nbits, self.sign)
        message += "Bounding polygon: {}".format(display_geom(self.bound_geom))
        message += "                  {}".format(display_geom(self.bound_coord))

        print(message)

    def export_kml(self, path):
        pass


def display_geom(geom):
    disp = ""
    for g in geom:
        disp += g[1] + "," + g[0] + " "
    return disp


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)

    folder = arguments["<folder>"]
    kml = arguments["--kml"]

    displayer = PleiadesDisplay(folder)
    displayer.display()

    if kml:
        displayer.export_kml(".")
