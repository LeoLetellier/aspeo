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

from asp import map_project, bundle_adjust, parse_toml, gdal_pansharp, orbit_viz
from params import get_sources
from params import DIR_BA, DIR_MP_PAN, DIR_MP_MS, DIR_PANSHARP
import os
import docopt
from copy import deepcopy


def map_projection(params: dict, debug=False):
    output_dir = params.get("output", ".")
    sources = get_sources(params)
    output_ba = os.path.join(output_dir, DIR_BA)
    output_mp_pan = os.path.join(output_dir, DIR_MP_PAN)
    output_mp_ms = os.path.join(output_dir, DIR_MP_MS)
    output_pansharp = os.path.join(output_dir, DIR_PANSHARP)
    mp_pan = params.get("mp-pan", None)
    mp_ms = params.get("mp-ms", None)

    dem = params["dem"]
    got_ms = all([s.get("ms", None) is not None for s in sources])

    if "bundle-adjust" in params.keys():
        imgs = [s["pan"] for s in sources]
        cams = [s["cam"] for s in sources]
        parallel = len(imgs) > 3
        bundle_adjust(imgs, cams, output_ba, params, parallel=parallel, debug=debug)
        params["map-project"]["bundle-adjust-prefix"] = output_ba
    elif os.path.isdir(output_ba):
        params["map-project"]["bundle-adjust-prefix"] = output_ba

    if mp_pan is not None:
        mp_params = deepcopy(params)
        mp_params["map-project"]["tr"] = mp_pan
        for s in sources:
            output = output_mp_pan + s["id"] + ".tif"
            map_project(dem, s["pan"], s["cam"], output, mp_params, debug=debug)
        del mp_params

    if mp_ms is not None and got_ms:
        ms_params = deepcopy(params)
        ms_params["map-project"]["tr"] = mp_ms
        for s in sources:
            output = output_mp_ms + s["id"] + ".tif"
            map_project(dem, s["ms"], s["cam-ms"], output, ms_params, debug=debug)
        del ms_params

    if "pansharpening" in params.keys():
        for s in sources:
            gdal_pansharp(
                s["pan"],
                s["cam"],
                output_pansharp + s["id"] + ".tif",
                params,
                debug=debug,
            )

    if "orbitviz" in params.keys():
        imgs = [s["pan"] for s in sources]
        cams = [s["cam"] for s in sources]
        orbit_viz(imgs, cams, output_dir + "/orbits.kml", params, debug=debug)


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_toml(toml)
    map_projection(params, debug=debug)
