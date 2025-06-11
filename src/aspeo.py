#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ASPeo

Usage:
    aspeo.py -h | --help
    aspeo.py -v | --version
    aspeo.py new [<preset>] [--path <path>]
    aspeo.py pt <toml> [--debug]
    aspeo.py mp <toml> [--debug]
"""

from asp import parse_toml
from asp_pt import pixel_tracking
from asp_mp import map_projection
from asp_new import generate_toml
import os
import docopt

PROJECT = parse_toml(os.path.join(os.path.dirname(__file__), "../pyproject.toml"))
VERSION = PROJECT["project"]["version"]


def resolve_cli(arguments):
    if arguments["new"]:
        preset = arguments["<preset>"]
        path = arguments["--path"]
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

    else:
        print("ASPeo version: v{}".format(VERSION))


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)

    resolve_cli(arguments)
