import os
import logging
import xml.etree.ElementTree as ET
import numpy as np

logger = logging.getLogger(__name__)

KEYS = ["id", "pan", "ms", "cam", "mp"]

DIR_BA = "BA/ba"
DIR_MP_PAN = "MP/PAN/mp-pan-"
DIR_MP_MS = "MP/MS/mp-ms-"
DIR_PANSHARP = "MP/PANSHARP/pansharp-"
DIR_ALIGNED = "MP/ALIGNED/align-"
DIR_STEREO = "STEREO/"
PREF_STEREO = "stereo"


def get_sources(params: dict, first=None) -> list[dict]:
    """Create the source dict from a file or raw definition"""
    source = params.get("source", None)
    if source is None:
        logger.info("Source is not explicitly described in toml, inferring from pairs")
        pairs = get_pairs(params, first=first)
        ids = ids_from_pairs(pairs)
        source = [{"id": str(i)} for i in ids]
        return extend_paths(source, params)
    if type(source) is list:
        logger.info("Source is described directly in toml")
        return extend_paths(source, params)

    logger.info("Reading source from file: {}".format(source))
    with open(source, "r") as infile:
        content = infile.read().split("\n")
    content = [c.split(" ") for c in list(filter(None, content))]

    if not all([len(c) == len(content[0]) for c in content]):
        raise ValueError("Source file contain non consistent lines")
    if len(content[0]) == 0:
        raise ValueError("Source file is empty")

    key_index = {}
    if params.get("source-header", False):
        logger.info("Read source keys")
        headers = content[0]
        content = content[1:]
        for k in KEYS:
            if k in headers:
                key_index[k] = headers.index(k)
            else:
                key_index[k] = None
            if key_index[KEYS[0]] is None:
                raise ValueError("No id field provided in source file")
    else:
        logger.info("Infer source keys from column nbs")
        for i, k in enumerate(KEYS):
            if len(content[0]) < i + 1:
                key_index[k] = i

    source = []
    logger.info("Dispatch content to source")
    for c in content:
        s = {}
        for k in KEYS:
            s[k] = c[key_index[k]]
        source.append(s)

    return extend_paths(source, params)


def extend_paths(sources: list[dict], params: dict) -> list[dict]:
    """Extend the images paths by adding the optional source folder, prefix and suffix"""
    src_folder = params.get("src-folder", "")

    def extend(key: str):
        pref = params.get(key + "-prefix", "")
        suff = params.get(key + "-suffix", "")
        if s.get(key, None) is not None:
            s[key] = os.path.join(src_folder, pref + s[key] + suff)

    for s in sources:
        if params.get("derive-pan", False):
            if s.get("pan", None) is None:
                s["pan"] = s["id"]
        else:
            if s.get("mp", None) is None:
                s["mp"] = s["id"]

        for key in KEYS[1:]:
            extend(key)

    return sources


def get_pairs(
    params: dict, ids: list[str] | None = None, first: int | None = None
) -> list[list[str]]:
    """Fetch ids from file"""
    file = params["pairs"]

    with open(file, "r") as infile:
        content = infile.read().split("\n")

    content = list(filter(None, content))
    content = [
        list(filter(None, c.replace("\t", " ").strip().split())) for c in content
    ]
    content = list(filter(None, content))

    if params.get("pairs-header", False):
        content = content[1:]

    if first is None and not all([len(c) == 2 or len(c) == 3 for c in content]):
        raise ValueError("Pairs file is invalid, pairs should involve 2 or 3 ids.")

    if first is not None:
        content = [c[:first] for c in content]

    if ids is not None:
        for c in content:
            for p in c:
                if p not in ids:
                    raise ValueError("Found unknown id in pairs file")

    return content


def make_full_pairs(ids: list[str]) -> list[list[str]]:
    pairs = []
    for i in range(len(ids) - 1):
        for j in range(i + 1, len(ids)):
            pairs.append([ids[i], ids[j]])
    logger.info("Made full {} pairs out of {} imgs".format(len(pairs), len(ids)))
    return pairs


def ids_from_pairs(pairs: list[list[str]]) -> list[str]:
    """Use the pair file to retrieve source ids"""
    flat_pairs = [p for pair in pairs for p in pair]
    unique_ids = list(set(flat_pairs))
    return unique_ids


def ids_from_source(source: list[dict]) -> list[str]:
    ids = [s["id"] for s in source]
    return ids


def source_from_id(id: str, sources: list[dict]) -> dict:
    """Get the source dict associated to an id"""
    for s in sources:
        if s["id"] == id:
            return s
    raise ValueError("id does not exist in sources")


def check_for_mp(sources: list[dict], working_dir: str) -> list[dict] | None:
    """Try to fetch MP images resulting from aspeo mp"""
    mp_pan_folder = os.path.join(os.path.abspath(working_dir), DIR_MP_PAN)
    for s in sources:
        mp_target = mp_pan_folder + s["id"] + ".tif"
        if os.path.isfile(mp_target):
            s["mp"] = mp_target
        elif s.get("mp", None) is None:
            return None
    return sources


def get_dim_bbox(dim: str) -> list[float]:
    root = ET.parse(dim).getroot()
    bbox_polygon = root.findall("./Dataset_Content/Dataset_Extent/Vertex")
    bbox_points = []
    for b in bbox_polygon:
        bbox_points.append([float(b.find("./LON").text), float(b.find("./LAT").text)])
    return points_to_bbox(bbox_points)


def points_to_bbox(points: list):
    """
    Convert a list of points (x, y) into a bbox, i.e retrieve the min max on each axis

    :param points: (N, 2) list of float / integer. Can be (lat, long), (x, y), ...
    :returns bbox: bounding box [x_min, x_max, y_min, y_max]
    """
    min = np.min(points, axis=0)
    max = np.max(points, axis=0)
    return [min[0], max[0], min[1], max[1]]


def retrieve_max2p_bbox(params: dict) -> list:
    all_bbox = []
    for s in params["source"]:
        if s.get("dim", None) is not None:
            all_bbox.append(get_dim_bbox(s["dim"]))
        else:
            raise ValueError("dim is not provided in toml sources")
    all_bbox = np.array(all_bbox)
    all_bbox = [np.min(all_bbox[:, :, 0]), np.max(all_bbox[:, :, 1]), np.min(all_bbox[:, :, 2]), np.max(all_bbox[:, :, 3])]
    # 2% padding for security
    bbox_width = all_bbox[1] - all_bbox[0]
    bbox_height = all_bbox[3] - all_bbox[2]
    global_2p_bbox = [all_bbox[0] - 0.02 * bbox_width,
                        all_bbox[1] + 0.02 * bbox_width,
                        all_bbox[2] - 0.02 * bbox_height,
                        all_bbox[3] + 0.02 * bbox_height]
    return global_2p_bbox
