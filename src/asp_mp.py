#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Map Projection Sequence (based on Ames Stereo Pipeline)

Need from the parameter file:
* sources: raw images (non map-projected)
* map-project > cmd: parameters needed by the stereo command

Usage:
    asp_mp.py <toml> [--debug | -d]
    asp_mp.py -h | --help

Options:
    -h --help       Show this screen
    <toml>          ASPeo parameter file
"""

from asp import map_project, bundle_adjust, gdal_pansharp, orbit_viz, sh
from params import get_sources, parse_params, retrieve_max2p_bbox
from params import DIR_BA, DIR_MP_PAN, DIR_MP_MS, DIR_PANSHARP
import os
import docopt
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)


def map_projection(params: dict, debug=False):
    logger.info("Beginning Map Projection sequence")
    output_dir = params.get("output", ".")
    sources = get_sources(params)
    output_ba = os.path.join(output_dir, DIR_BA)
    output_mp_pan = os.path.join(output_dir, DIR_MP_PAN)
    output_mp_ms = os.path.join(output_dir, DIR_MP_MS)
    output_pansharp = os.path.join(output_dir, DIR_PANSHARP)
    mp_pan = params.get("mp-pan", None)
    mp_ms = params.get("mp-ms", None)

    if params.get("dem", None) is None:
        logger.info("dem is not provided in parameters")
        if sh("my_getDemFile.py -h").returncode == 1:
            logger.error("my_getDemFile is not available for dem retrieval")
            raise ValueError("my_getDemFile is not available for dem retrieval")
        else:
            logger.info("automatically retrieve dem using my_getDemFile")
            params["dem"] = retrieve_dem(params, debug=debug)

    dem = params["dem"]
    got_ms = all([s.get("ms", None) is not None for s in sources])

    if "bundle-adjust" in params.keys():
        logger.info("Bundle adjust")
        imgs = [s["pan"] for s in sources]
        cams = [s["cam"] for s in sources]
        parallel = len(imgs) > 3
        bundle_adjust(imgs, cams, output_ba, params, parallel=parallel, debug=debug)
        params["map-project"]["bundle-adjust-prefix"] = output_ba
    elif os.path.isdir(output_ba):
        params["map-project"]["bundle-adjust-prefix"] = output_ba

    if mp_pan is not None:
        logger.info("Map project Panchromatic (P) images")
        mp_params = deepcopy(params)
        mp_params["map-project"]["tr"] = mp_pan
        for s in sources:
            output = output_mp_pan + s["id"] + ".tif"
            map_project(dem, s["pan"], s["cam"], output, mp_params, debug=debug)
        del mp_params

    if mp_ms is not None and got_ms:
        logger.info("Map project Multi Spectral (MS) images")
        ms_params = deepcopy(params)
        ms_params["map-project"]["tr"] = mp_ms
        for s in sources:
            output = output_mp_ms + s["id"] + ".tif"
            map_project(dem, s["ms"], s["cam-ms"], output, ms_params, debug=debug)
        del ms_params

    if "pansharpening" in params.keys():
        logger.info("Creating pansharpened images")
        for s in sources:
            gdal_pansharp(
                s["pan"],
                s["cam"],
                output_pansharp + s["id"] + ".tif",
                params,
                debug=debug,
            )

    if "orbitviz" in params.keys():
        logger.info("Generating orbit view (KML)")
        imgs = [s["pan"] for s in sources]
        cams = [s["cam"] for s in sources]
        orbit_viz(imgs, cams, output_dir + "/orbits.kml", params, debug=debug)


def retrieve_dem(params: dict, debug=False) -> str:
    bbox = retrieve_max2p_bbox(params)
    long1, long2, lat1, lat2 = bbox[0], bbox[1], bbox[2], bbox[3]
    output = params.get("output", ".")
    dst = os.path.join(
        output,
        "cop_dem30_{}_{}_{}_{}".format(int(long1), int(long2), int(lat1), int(lat2)),
    )

    cmd1 = "my_getDemFile.py -s COP_DEM --bbox={},{},{},{} -c /data/ARCHIVES/DEM/COP-DEM_GLO-30-DTED/DEM".format(
        long1, long2, lat1, lat2
    )
    cmd2 = "gdal_translate -of Gtiff {} {}".format(dst + ".dem", dst + ".tif")
    if not debug:
        sh(cmd1)
        sh(cmd2)

        os.remove(dst + ".dem")
        os.remove(dst + ".dem.aux.xml")
        os.remove(dst + ".dem.rsc")
    else:
        print(cmd1)
        print(cmd2)
    return dst + ".tif"


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_params(toml)
    map_projection(params, debug=debug)
