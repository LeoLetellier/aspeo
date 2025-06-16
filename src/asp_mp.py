#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Map Projection Sequence (based on Ames Stereo Pipeline)

Need from the parameter file:
* sources: raw images (non map-projected)
* map-project > cmd: parameters needed by the stereo command

Usage:
    asp_mp.py <toml> [--debug]
    asp_mp.py -h | --help

Options:
    -h --help       Show this screen
    <toml>          ASPeo parameter file
"""

from asp import map_project, bundle_adjust, parse_toml
import os
import docopt


def fetch_sources(params: dict):
    dem = params["dem"]
    sources = params["source"]
    imgs = []
    cams = []
    prefix = params.get("src_prefix", "")
    suffix = params.get("src_suffix", "")
    src_folder = params.get("src_folder", "")
    for s in sources:
        id = s["id"]
        img = s.get("raw", id)
        img = os.path.join(src_folder, prefix + img + suffix)
        imgs.append(img)
        cams.append(s["cam"])
    return dem, imgs, cams


def map_projection(params: dict, debug=False):
    dem, imgs, cams = fetch_sources(params)
    output_dir = params.get("output", ".")
    output_ba = os.path.join(output_dir, "BA/ba-")
    output_mp = os.path.join(output_dir, "MP/mp-")
    if "bundle-adjust" in params.keys():
        bundle_adjust(imgs, cams, output_ba, params, debug=debug)
        params["map-project"]["cmd"]["bundle-adjust-prefix"] = output_ba
    for mp in range(len(imgs)):
        map_project(dem, imgs[mp], cams[mp], output_mp, params, debug=debug)


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_toml(toml)
    map_projection(params, debug=debug)
