import os

KEYS = ["id", "pan", "ms", "cam", "mp"]

DIR_BA = "/BA/ba"
DIR_MP_PAN = "/MP/PAN/mp-pan"
DIR_MP_MS = "/MP/MS/mp-ms"
DIR_PANSHARP = "/MP/PANSHARP/pansharp"
DIR_ALIGNED = "/MP/ALIGNED/align-"
DIR_STEREO = "/STEREO/"
PREF_STEREO = "/stereo"


def get_sources(params: dict, first=None) -> list[dict]:
    """Create the source dict from a file or raw definition"""
    source = params.get("source", None)
    if source is None:
        pairs = get_pairs(params, first=first)
        ids = ids_from_pairs(pairs)
        source = [{"id": i} for i in ids]
        return extend_paths(source, params)
    if type(source) is list:
        return extend_paths(source, params)

    with open(source, "r") as infile:
        content = infile.read().split("\n")
    content = [c.split(" ") for c in list(filter(None, content))]

    if not all([len(c) == len(content[0]) for c in content]):
        raise ValueError("Source file contain non consistent lines")
    if len(content[0]) == 0:
        raise ValueError("Source file is empty")

    key_index = {}
    if params.get("stereo", {}).get("pairs-header", False):
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
        for i, k in enumerate(KEYS):
            if len(content[0]) < i + 1:
                key_index[k] = i

    source = []
    for c in content:
        s = {}
        for k in KEYS:
            s[k] = c[key_index[k]]
        source.append(s)

    return extend_paths(source, params)


def extend_paths(sources: list[dict], params: dict) -> list[dict]:
    """Extend the images paths by adding the optional source folder, prefix and suffix"""
    src_folder = params.get("src_folder", "")

    def extend(key: str):
        pref = params.get(key + "_prefix", "")
        suff = params.get(key + "_suffix", "")
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


def get_pairs(params: dict, ids: list[str] | None = None, first: int | None = None) -> list[list[str]]:
    """Fetch ids from file"""
    file = params["pairs"]

    with open(file, "r") as infile:
        content = infile.read().split("\n")

    content = list(filter(None, content))
    content = [list(filter(None, c.replace('\t', ' ').strip().split())) for c in content]

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
