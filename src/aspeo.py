#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ames Stereo Pipeline sequential workflows for Earth Observation (ASPeo)

Workflows are available to launch ASP commands on a list of images or
list of pairs of images. Fine-tune the workflows using the toml
parameter file.

* new: initialize a parameter file from preset parameters
* mp: map-project the source images
* pt: perform pixel-tracking onto the pairs of images
* dsm: compute a digital surface model from stereo images

Usage:
    aspeo.py
    aspeo.py -h | --help
    aspeo.py new [<preset>] [--path <path>]
    aspeo.py pt <toml> [--debug | -d]
    aspeo.py mp <toml> [--debug | -d]
    aspeo.py dsm <toml> [--debug | -d]

Options:
    -h --help         Display command details
    <toml>              Path to the parameter file (toml)
    -d --debug        Display ASP commands instead of running them

"""

from asp import parse_toml
from asp_pt import pixel_tracking
from asp_mp import map_projection
from asp_new import generate_toml, VERSION
from asp_dsm import dsm_generation
import docopt


def resolve_cli(arguments):
    print(arguments)
    if arguments["new"]:
        preset = arguments["<preset>"]
        path = arguments["<path>"]
        if preset is None:
            preset = "default"
        generate_toml(preset, path=path)

    elif arguments["pt"]:
        toml = arguments["<toml>"]
        debug = arguments["--debug"]
        params = parse_toml(toml)
        pixel_tracking(params, debug=debug)

    elif arguments["mp"]:
        toml = arguments["<toml>"]
        debug = arguments["--debug"]
        params = parse_toml(toml)
        map_projection(params, debug=debug)

    elif arguments["dsm"]:
        toml = arguments["<toml>"]
        debug = arguments["--debug"]
        params = parse_toml(toml)
        dsm_generation(params, debug=debug)

    else:
        version_message()


def version_message():
    print("ASPeo version: v{}".format(VERSION))


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)

    resolve_cli(arguments)
