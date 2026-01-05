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

import logging
import os
from shutil import copyfile

import docopt

from asp import corr_eval, image_align, stereo
from params import (
    DIR_ALIGNED,
    DIR_STEREO,
    PREF_STEREO,
    check_for_mp,
    get_pairs,
    get_sources,
    ids_from_source,
    make_full_pairs,
    parse_params,
    source_from_id,
)

logger = logging.getLogger(__name__)


def corr_eval_ncc(stereo_output: str, params: dict, debug=False):
    """NCC correlation evaluation for each stereo pair"""
    left = stereo_output + "-L.tif"
    right = stereo_output + "-R.tif"
    disp = stereo_output + "-F.tif"
    corr_eval(left, right, disp, stereo_output, params, debug=debug)


def pixel_tracking(params: dict, debug=False):
    """Beginning Pixel Tracking sequence"""
    logger.info("Initializing pixel tracking")
    output_dir = params.get("output", ".")
    sources = get_sources(params, first=2)
    ids = ids_from_source(sources)
    if params.get("pairs", None) is not None:
        pairs = get_pairs(params, ids, first=2)
    else:
        pairs = make_full_pairs(ids)
    sources = check_for_mp(sources, output_dir)
    if sources is None:
        raise ValueError("No map projected images defined or no previous mp run found")
    aligned = None
    if params.get("force", False):
        logger.info("Force mode: every pair will be recomputed even if already exists")

    if "align" in params.keys():
        raise NotImplementedError("feature might not be kept")
        logger.info("Launching image alignment")
        aligned = {sources[0]["id"]: DIR_ALIGNED + os.path.basename(sources[0]["mp"])}
        if not debug:
            copyfile(sources[0]["mp"], DIR_ALIGNED + os.path.basename(sources[0]["mp"]))

        for s in sources[1:]:
            output = os.path.join(output_dir, DIR_ALIGNED + os.path.basename(s["mp"]))
            image_align(
                sources[0]["mp"],
                s["mp"],
                DIR_ALIGNED + os.path.basename(s["mp"]),
                params,
                debug=debug,
            )
            aligned[s["id"]] = DIR_ALIGNED + os.path.basename(s["mp"])

    if "stereo" in params.keys():
        logger.info("Launching stereo")
        for p in pairs:
            id1, id2 = p[0], p[1]
            logger.debug("Stereo pair: {} - {}".format(id1, id2))
            src1, src2 = source_from_id(id1, sources), source_from_id(id2, sources)
            if aligned is not None:
                imgs = [aligned[id1], aligned[id2]]
            else:
                imgs = [src1["mp"], src2["mp"]]
            output = os.path.join(
                output_dir, DIR_STEREO, id1 + "_" + id2 + "/" + PREF_STEREO
            )
            outfile = os.path.join(
                output_dir, DIR_STEREO, id1 + "_" + id2 + "/" + PREF_STEREO + "-F.tif"
            )
            # if not os.path.isdir(output) or params.get("force", False):
            if not os.path.isfile(outfile) or params.get("force", False):
                use_params = params
                if params.get("correct-corr-search", False):
                    use_params = correct_corr_search(params.copy(), imgs)
                stereo(imgs, None, output, use_params, debug=debug)
            else:
                logger.info(f"Skipping (already exists): {id1}-{id2}")

    if "corr-eval" in params.keys():
        logger.info("Launching correlation evaluation (ncc)")
        for p in pairs:
            id1, id2 = p[0], p[1]
            output = os.path.join(
                output_dir, DIR_STEREO, id1 + "_" + id2 + "/" + PREF_STEREO
            )
            if not os.path.isfile(output + "-ncc.tif") or params.get("force", False):
                corr_eval_ncc(output, params, debug=debug)
            else:
                logger.info(f"Skipping NCC (already exists): {id1}-{id2}")


def correct_corr_search(params, src1, src2):
    res = params["mp-pan"]
    delta_ulx = (src1["ulx"] - src2["ulx"]) / res
    delta_uly = (src1["uly"] - src2["uly"]) / res
    corr_search = params["stereo"]["corr-search"]
    params["stereo"]["corr-search"] = [
        corr_search[0] - delta_ulx,
        corr_search[0] - delta_ulx,
        corr_search[1] - delta_uly,
        corr_search[1] - delta_uly,
    ]
    return params


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_params(toml)
    pixel_tracking(params, debug=debug)
