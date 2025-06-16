#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Digital Surface Model (DSM) generation Sequence (based on Ames Stereo Pipeline)

Need from the parameter file:
* sources: raw images (non map-projected)

Usage:
    asp_dsm.py <toml> [--debug]
    asp_dsm.py -h | --help

Options:
    -h --help       Show this screen
    <toml>          ASPeo parameter file
"""

from asp import (
    map_project,
    bundle_adjust,
    stereo,
    pc_align,
    point2dem,
    dem_mosaic,
    parse_toml,
)
import os
import docopt


def dsm_generation(params: dict, debug=False):
    print(params["source"])
    raise NotImplementedError("dsm generation not yet implemented")


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_toml(toml)
    dsm_generation(params, debug=debug)
