#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Digital Surface Model (DSM) generation Sequence (based on Ames Stereo Pipeline)

Need from the parameter file:
* sources: raw images (non map-projected)

Usage:
    asp_dsm.py <toml> [--debug | -d]
    asp_dsm.py -h | --help

Options:
    -h --help       Show this screen
    <toml>          ASPeo parameter file
"""

from asp import stereo, pc_align, point2dem, dem_mosaic, sh
from params import (
    parse_params,
    get_sources,
    get_pairs,
    ids_from_source,
    source_from_id,
    check_for_mp,
    retrieve_max2p_bbox,
    retrieve_dem,
    DIR_STEREO,
    PREF_STEREO,
)
import os
import docopt
import logging

logger = logging.getLogger(__name__)


def dsm_generation(params: dict, debug=False):
    logger.info("Beginning DSM Generation sequence")
    output_dir = params.get("output", ".")
    sources = get_sources(params)
    pairs = get_pairs(params, ids_from_source(sources))
    sources = check_for_mp(sources, output_dir)
    if sources is None:
        raise ValueError("No map projected images defined or no previous mp run found")
    fragment = []

    if params.get("dem", None) is None:
        logger.info("dem is not provided in parameters")
        if sh("my_getDemFile.py -h").returncode == 1:
            logger.error("my_getDemFile is not available for dem retrieval")
            raise ValueError("my_getDemFile is not available for dem retrieval")
        else:
            logger.info("automatically retrieve dem using my_getDemFile")
            params["dem"] = retrieve_dem(params, debug=debug)

    for p in pairs:
        frag = os.path.join(output_dir, DIR_STEREO, p[0] + "_" + p[1])
        if len(p) > 2:
            frag += "_" + p[2]
        frag += PREF_STEREO
        fragment.append(frag)

    logger.info("working with {} fragments".format(len(fragment)))

    pc_suffix = "-PC.tif"
    if "stereo" in params.keys():
        run_stereo(pairs, sources, fragment, params, debug=debug)

    if "pc-align" in params.keys():
        logger.info("align fragments")
        for f in fragment:
            pc_align(
                params["dem"], f + pc_suffix, f + "-PC_aligned.tif", params, debug=debug
            )
        pc_suffix = "-PC_aligned.tif"

    if "point2dem" in params.keys():
        logger.info("rasterize fragments")
        for f in fragment:
            point2dem(f + pc_suffix, f, params, debug=debug)

    if "dem-mosaic" in params.keys():
        logger.info("merge fragments")
        dems = [f + "-DEM.tif" for f in fragment]
        output = output_dir + "/dem.tif"
        dem_mosaic(dems, output, params, debug=debug)


def run_stereo(pairs, sources, fragment, params, debug):
    logger.info("Do stereo")
    for i, p in enumerate(pairs):
        id1, id2 = p[0], p[1]
        src1, src2 = source_from_id(id1, sources), source_from_id(id2, sources)
        mps = [src1["mp"], src2["mp"]]
        cams = [src1["cam"], src2["cam"]]

        if len(p) > 2:
            id3 = p[2]
            src3 = source_from_id(id3, sources)
            mps.append(src3["mp"])
            cams.append(src3["cam"])
        stereo(mps, cams, fragment[i], params, debug=debug, dem=params["dem"])


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_params(toml)
    dsm_generation(params, debug=debug)
