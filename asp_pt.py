#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
asp_pt
------
Launch pixel traking sequence

Usage:
    asp_pt.py <toml> [--debug]
    asp_pt.py -h | --help

Options:
    -h --help       Show this screen
    <toml>          ASPeo parameter file
"""
from asp import stereo, parse_toml, BLACK_LEFT, BLACK_RIGHT
import docopt


def make_pairs(pairs, dates, mp):
    assos = dict(zip(dates, mp))
    with open(pairs, "r") as infile:
        line = infile.read().split("\n")
        date_pairs = [p.split(" ") for p in list(filter(None, line))]
    img_pairs = [[assos[p[0]], assos[p[1]]] for p in date_pairs]
    return img_pairs, date_pairs


def pixel_tracking(toml, debug=False):
    params = parse_toml(toml)
    sources = params["source"]
    pairs_file = params["stereo"]["pairs"]

    dates = [s["id"] for s in sources]
    mp = [s["mp"] for s in sources]
    img_pairs, date_pairs = make_pairs(pairs_file, dates, mp)

    for p, d in zip(img_pairs, date_pairs):
        output = d[0] + "_"+ d[1] + "/pt"
        stereo(p, [BLACK_LEFT, BLACK_RIGHT], output, params, debug=debug)


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    pixel_tracking(toml, debug=debug)
