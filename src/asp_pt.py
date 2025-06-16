#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pixel Tracking Sequence (based on Ames Stereo Pipeline)

Need from the parameter file:
* sources: ideally map-projected images
* stereo > pairs: text list of pairs to process (one pair per line, space separated id)
* stereo > cmd: parameters needed by the stereo command
* corr-eval: add to compute the normalized cross-correlation (ncc metric)

Usage:
    asp_pt.py <toml> [--debug | -d]
    asp_pt.py -h | --help

Options:
    -h --help       Show this screen
    <toml>          ASPeo parameter file
"""

from asp import stereo, corr_eval, parse_toml, BLACK_LEFT, BLACK_RIGHT
from params import get_sources, get_pairs, source_from_id, ids_from_source
from params import DIR_STEREO, PREF_STEREO
import os
import docopt


def corr_eval_ncc(stereo_output: str, params: dict, debug=False):
    """NCC correlation evaluation for each stereo pair"""
    left = stereo_output + "-L.tif"
    right = stereo_output + "-R.tif"
    disp = stereo_output + "-F.tif"
    corr_eval(left, right, disp, stereo_output, params, debug=debug)


def pixel_tracking(params: dict, debug=False):
    """Pixel tracking sequence using stereo"""
    output_dir = params.get("output", ".")
    sources = get_sources(params)
    pairs = get_pairs(params, ids_from_source(sources))

    for p in pairs:
        id1, id2 = p[0], p[1]
        src1, src2 = source_from_id(id1, sources), source_from_id(id2, sources)
        pans = [src1["mp"], src2["mp"]]
        cams = [src1.get("cam", BLACK_LEFT), src2.get("cam", BLACK_RIGHT)]
        output = os.path.join(output_dir, DIR_STEREO, id1 + "_" + id2 + PREF_STEREO)
        stereo(pans, cams, output, params, debug=debug)

    if params.get("corr-eval", None) is not None:
        for p in pairs:
            id1, id2 = p[0], p[1]
            output = os.path.join(output_dir, DIR_STEREO, id1 + "_" + id2 + PREF_STEREO)
            corr_eval_ncc(output, params, debug=debug)


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_toml(toml)
    pixel_tracking(params, debug=debug)
