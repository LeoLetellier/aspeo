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
import os
import docopt


def resolve_pairs(file: str, param: dict):
    """Fetch ids from file"""
    with open(file, "r") as infile:
        content = infile.read().split("\n")
    if param.get("stereo", {}).get("pairs-header", False):
        content = content[1:]
    content = [c.split(" ") for c in list(filter(None, content))]
    ids = [c[0] for c in content]
    if len(content[0][0]) == len(content[0][1]):
        ids += [c[1] for c in content]
    ids = list(set(ids))

    param["source"] = []
    for id in ids:
        dic = {"id": id}
        param["source"].append(dic)


def make_pairs(pairs_file: str, dates: list, mp: list, cams: list | None, header: bool):
    """Derive pairing between images and dates based on a pair file"""
    assos_mp = dict(zip(dates, mp))
    with open(pairs_file, "r") as infile:
        line = infile.read().split("\n")
        if header:
            line = line[1:]
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
    prefix = params.get("src_prefix", "")
    suffix = params.get("src_suffix", "")
    src_folder = params.get("src_folder", "")
    for s in sources:
        id = s["id"]
        m = s.get("mp", id)
        c = s.get("cam", None)
        m = os.path.join(src_folder, prefix + m + suffix)
        dates.append(id)
        mp.append(m)
        if cams is not None:
            if c is None:
                cams = None
            else:
                cams.append(os.path.join(src_folder, c))

    return dates, mp, cams


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
    # dates, mp, cams = fetch_sources(params)
    # header = params.get("stereo", {}).get("pairs-header", False)
    # img_pairs, date_pairs, cam_pairs = make_pairs(pairs_file, dates, mp, cams, header)

    # for p, d, c in zip(img_pairs, date_pairs, cam_pairs):
    #     output = os.path.join(output_dir, d[0] + "_" + d[1] + "/pt")
    #     stereo(p, c, output, params, debug=debug)
    #     if params.get("corr-eval", None) is not None:
    #         corr_eval_ncc(output, params, debug=debug)
    for p in pairs:
        id1, id2 = p[0], p[1]
        src1, src2 = source_from_id(id1, sources), source_from_id(id2, sources)
        pans = [src1["pan"], src2["pan"]]
        cams = [src1.get("cam", BLACK_LEFT), src2.get("cam", BLACK_RIGHT)]
        output = os.path.join(output_dir, "STEREO", id1 + "_" + id2 + "/stereo")
        stereo(pans, cams, output, params, debug=debug)

    if params.get("corr-eval", None) is not None:
        for p in pairs:
            id1, id2 = p[0], p[1]
            output = os.path.join(output_dir, "STEREO", id1 + "_" + id2 + "/stereo")
            corr_eval_ncc(output, params, debug=debug)


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    toml = arguments["<toml>"]
    debug = arguments["--debug"]

    params = parse_toml(toml)
    pixel_tracking(params, debug=debug)
