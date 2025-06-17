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

from asp import (
    stereo,
    pc_align,
    point2dem,
    dem_mosaic,
    parse_toml,
)
from params import get_sources, get_pairs, ids_from_source, source_from_id, DIR_STEREO, PREF_STEREO
import os
import docopt


def dsm_generation(params: dict, debug=False):
    output_dir = params.get("output", ".")
    sources = get_sources(params)
    pairs = get_pairs(params, ids_from_source(sources))

    if "stereo" in params.keys():
        for p in pairs:
            id1, id2 = p[0], p[1]
            src1, src2 = source_from_id(id1, sources), source_from_id(id2, sources)
            mps = [src1["mp"], src2["mp"]]
            cams = [src1["cam"], src2["cam"]]
            output = os.path.join(output_dir, DIR_STEREO, id1 + "_" + id2)

            if len(p) > 2:
                id3 = p[2]
                src3 = source_from_id(id3, sources)
                mps.append(src3["mp"])
                cams.append(src3["cam"])
                output += "_" + id3
            output += PREF_STEREO

            if "stop-point" in params["stereo"]:
                params["stereo"].pop("stop-point")
            stereo(mps, cams, output, params, debug=debug)

    if "pc-align" in params.keys():
        for p in pairs:
            id1, id2 = p[0], p[1]
            base = os.path.join(output_dir, DIR_STEREO, id1 + "_" + id2)
            if len(p) > 2:
                base += "_" + p[2]
            pc = base + PREF_STEREO + "-pc.tif"
            output = base + PREF_STEREO + "-pc_aligned.tif"
            pc_align(params["dem"], pc, output, params, debug=debug)

    if "point2dem" in params.keys():
        for p in pairs:
            id1, id2 = p[0], p[1]
            base = os.path.join(output_dir, DIR_STEREO, id1 + "_" + id2)
            if len(p) > 2:
                base += "_" + p[2]
            if "pc-align" in params.keys():
                pc = base + PREF_STEREO + "-pc_aligned.tif"
            else:
                pc = base + PREF_STEREO + "-pc.tif"
            output = base + PREF_STEREO + "-dem.tif"
            point2dem(pc, output, params, debug=debug)

    if "dem-mosaic" in params.keys():
        dems = []
        for p in pairs:
            id1, id2 = p[0], p[1]
            base = os.path.join(output_dir, DIR_STEREO, id1 + "_" + id2)
            if len(p) > 2:
                base += "_" + p[2]
            dems.append(base + PREF_STEREO + "-dem.tif")
        output = output_dir + "/dem.tif"
        dem_mosaic(dems, output, params, debug=debug)

if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_toml(toml)
    dsm_generation(params, debug=debug)
