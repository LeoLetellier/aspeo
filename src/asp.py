import tomli
import os
import sys
import subprocess
import logging
logger = logging.getLogger(__name__)

BLACK_LEFT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets", "black_left.tsai"
)
BLACK_RIGHT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets", "black_right.tsai"
)


def parse_toml(file: str) -> dict:
    """Open a toml file as a dict"""
    with open(file, "rb") as f:
        toml = tomli.load(f)
    return toml


def sh(cmd: str, shell=True):
    """
    Launch a shell command

    As shell=True, all single call is made in a separate shell

    # Example

    ````
    sh("ls -l | wc -l")
    ````

    """
    logger.info('>> ' + cmd)
    subprocess.run(
        cmd, shell=shell, stdout=sys.stdout, stderr=subprocess.STDOUT, env=os.environ
    )


def arg_to_str(arg) -> str:
    """Resolve an argument into a string representation
    [10, 10] > "10 10"
    [var1, var2] > "str(var1) str(var2)"
    var > str(var)
    None > ""
    """
    if arg is not None:
        if type(arg) is list:
            # Concatenate multiples elements with space
            return " ".join([str(a) for a in arg])
        # Return element as string
        return str(arg)
    # return empty string
    return ""


def format_arg(key: str, value) -> str:
    """Format a key/value couple into a command option"""
    prefix = "--" if len(key) > 1 else "-"
    # sep = " " if len(key) > 1 else " "
    if type(value) is bool:
        if value:
            return prefix + "{}".format(key)
        else:
            return ""
    value = arg_to_str(value)
    return prefix + "{} {}".format(key, value)


def format_dict(dic: dict) -> str:
    """Format all dict into command options"""
    params = ""
    for key, value in dic.items():
        params += format_arg(key, value) + " "
    return params


def stereo(
    images: list[str], cameras: list[str], output: str, parameters: dict, debug=False
):
    """Launch a parallel_stereo (ASP) based on a parameter dict

    If debug is used, print the command without launching it. Useful to show the command
    even without the ASP binaries available
    """
    params = format_dict(parameters["stereo"])

    cmd = "parallel_stereo {} {} {} {}".format(
        arg_to_str(images), arg_to_str(cameras), output, params
    )

    if debug:
        print(cmd)
    else:
        sh(cmd)


def corr_eval(
    left: str, right: str, disp: str, output: str, parameters: dict, debug=False
):
    """Launch a corr_eval (ASP) to evaluate the ncc of a stereo result"""
    params = format_dict(parameters["corr-eval"])

    cmd = "corr_eval {} {} {} {} {}".format(params, left, right, disp, output)

    if debug:
        print(cmd)
    else:
        sh(cmd)


def map_project(
    dem: str, image: str, camera: str, output: str, parameters: dict, debug=False
):
    """Launch mapproject (ASP) to create an orthorectified image"""
    params = format_dict(parameters["map-project"])

    cmd = "mapproject {} {} {} {} {}".format(params, dem, image, camera, output)

    if debug:
        print(cmd)
    else:
        sh(cmd)


def bundle_adjust(
    images: list[str],
    cameras: list[str],
    output: str,
    parameters: dict,
    ground_control_points: list[str] | None = None,
    parallel=False,
    debug=False,
):
    """Launch bundle_adjust to reduce errors between cameras based on their given images"""
    params = format_dict(parameters["bundle-adjust"])

    gcp = ""
    if ground_control_points is not None:
        gcp += " " + arg_to_str(ground_control_points)

    cmd = "bundle_adjust {} {}{} -o {} {}".format(
        arg_to_str(images), arg_to_str(cameras), gcp, output, params
    )

    if parallel:
        cmd = "parallel_" + cmd
    if debug:
        print(cmd)
    else:
        sh(cmd)


def pc_align(
    reference: str,
    source: str,
    output: str,
    parameters: dict,
    debug=False,
):
    """Launch pc_align to align a source point cloud to another reference (or DEM)"""
    params = format_dict(parameters["pc-align"])

    cmd = "pc_align {} {} {} -o {}".format(params, reference, source, output)

    if debug:
        print(cmd)
    else:
        sh(cmd)


def point2dem(
    point_cloud: str,
    output: str,
    parameters: dict,
    debug=False,
):
    """Launch point2dem to convert a point cloud into a DEM"""
    params = format_dict(parameters["point2dem"])

    cmd = "point2dem {} {} -o {}".format(params, point_cloud, output)

    if debug:
        print(cmd)
    else:
        sh(cmd)


def dem_mosaic(
    dems: list[str],
    output: str,
    parameters: dict,
    debug=False,
):
    """Launch dem_mosaic to merge rasters with overlap blending"""
    params = format_dict(parameters["dem-mosaic"])

    cmd = "dem_mosaic {} {} -o {}".format(params, arg_to_str(dems), output)

    if debug:
        print(cmd)
    else:
        sh(cmd)


def image_align(
    reference: str, source: str, output: str, parameters: dict, debug=False
):
    """Launch image_align to align images feature based"""
    params = format_dict(parameters["align"])

    cmd = "image_align {} {} {} -o {}".format(params, reference, source, output)

    if debug:
        print(cmd)
    else:
        sh(cmd)


def orbit_viz(
    imgs: list[str], cams: list[str], output: str, parameters: dict, debug=False
):
    """Launch orbitviz to create a kml featuring the acquisition orbits"""
    params = format_dict(parameters["orbitviz"])

    cmd = "orbitviz {} {} {} -o {}".format(
        params, arg_to_str(imgs), arg_to_str(cams), output
    )

    if debug:
        print(cmd)
    else:
        sh(cmd)


def gdal_crop(input: str, output: str, parameters: dict, debug=False):
    """Use gdal_translate with the crop parameters"""
    params = format_dict(parameters["crop"])

    cmd = "gdal_translate {} {} {}".format(params, input, output)

    if debug:
        print(cmd)
    else:
        sh(cmd)


def gdal_pansharp(
    panchro: str, ms: list[str], output: str, parameters: dict, debug=False
):
    """Launch gdal pansharpen to create multispectral image with the resolution of a
    panchromatic image"""
    params = format_dict(parameters["pansharpening"])

    cmd = "gdal_pansharpen {} {} {} {}".format(panchro, arg_to_str(ms), output, params)

    if debug:
        print(cmd)
    else:
        sh(cmd)
