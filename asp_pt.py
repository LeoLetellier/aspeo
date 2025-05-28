#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pixel Tracking Sequence (based on Ames Stereo Pipeline)

Usage:
    asp_pt.py <toml> [--debug]
    asp_pt.py -h | --help

Options:
    -h --help       Show this screen
    <toml>          ASPeo parameter file
"""

from asp import stereo, parse_toml, BLACK_LEFT, BLACK_RIGHT
import os
import docopt


def make_pairs(pairs_file: str, dates: list, mp: list, cams: list | None):
    """Derive pairing between images and dates based on a pair file"""
    assos_mp = dict(zip(dates, mp))
    with open(pairs_file, "r") as infile:
        line = infile.read().split("\n")
        date_pairs = [p.split(" ") for p in list(filter(None, line))]
    img_pairs = [[assos_mp[p[0]], assos_mp[p[1]]] for p in date_pairs]
    if cams is None:
        cam_pairs = len(dates) * [[BLACK_LEFT, BLACK_RIGHT]]
    else:
        assos_cam = dict(zip(dates, cams))
        cam_pairs = [[assos_cam[p[0]], assos_cam[p[1]]] for p in date_pairs]
    return img_pairs, date_pairs, cam_pairs


def fetch_sources(params: dict):
    """Fetch the id and image path from source
    Enable composing the image path using the id and a prefix/suffix
    """
    sources = params["source"]
    dates = []
    mp = []
    cams = []
    prefix = params["aspeo"].get("src_prefix", "")
    suffix = params["aspeo"].get("src_suffix", "")
    for s in sources:
        d = s["id"]
        m = s.get("mp", None)
        c = s.get("cam", None)
        if m is None:
            m = d
        m = prefix + m + suffix
        dates.append(d)
        mp.append(m)
        if cams is not None:
            if c is None:
                cams = None
            else:
                cams.append(c)

    return dates, mp, cams


def pixel_tracking(params: dict, debug=False):
    """Pixel tracking sequence using stereo"""
    pairs_file = params["stereo"]["pairs"]
    output_dir = params["aspeo"].get("output", ".")

    dates, mp, cams = fetch_sources(params)
    img_pairs, date_pairs, cam_pairs = make_pairs(pairs_file, dates, mp, cams)

    for p, d, c in zip(img_pairs, date_pairs, cam_pairs):
        output = os.path.join(output_dir, d[0] + "_" + d[1] + "/pt")
        stereo(p, c, output, params, debug=debug)


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_toml(toml)
    pixel_tracking(params, debug=debug)
