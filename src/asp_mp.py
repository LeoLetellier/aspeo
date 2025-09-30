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
from params import (
    get_sources,
    parse_params,
    retrieve_max2p_bbox,
    retrieve_dem,
    get_pairs,
    ids_from_source,
    source_from_id,
)
from params import DIR_BA, DIR_MP_PAN, DIR_MP_MS, DIR_PANSHARP
import os
import docopt
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)


def map_projection(params: dict, debug=False):
    """Core function for the Map projection Workflow"""
    logger.info("Beginning Map Projection sequence")
    output_dir = params.get("output", ".")
    sources = get_sources(params)
    if "pairs" in params:
        pairs = get_pairs(params, ids_from_source(sources))
    else:
        pairs = None
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
        run_ba(sources, pairs, params, output_ba, debug=debug)

        params["map-project"]["bundle-adjust-prefix"] = output_ba
    elif os.path.isdir(output_dir + "/BA/"):
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


def run_ba(sources, pairs, params, output_ba, debug=False):
    """Bundle Adjust handling for pairs without major overlapping"""
    if pairs is None:
        # No pairs, do same bundle adjust for all images
        imgs = [s["pan"] for s in sources]
        cams = [s["cam"] for s in sources]
        parallel = len(imgs) > 3
        bundle_adjust(imgs, cams, output_ba, params, parallel=parallel, debug=debug)
    else:
        # pairs are given, do bundle adjust per pair
        for p in pairs:
            id1, id2 = p[0], p[1]
            src1, src2 = source_from_id(id1, sources), source_from_id(id2, sources)
            imgs = [src1["pan"], src2["pan"]]
            cams = [src1["cam"], src2["cam"]]

            if len(p) > 2:
                id3 = p[2]
                src3 = source_from_id(id3, sources)
                imgs.append(src3["pan"])
                cams.append(src3["cam"])
                bundle_adjust(imgs, cams, output_ba, params, debug=debug)


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_params(toml)
    map_projection(params, debug=debug)
