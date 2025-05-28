import tomli
import os
import sys
import subprocess

BLACK_LEFT = os.path.join(os.path.dirname(__file__), "assets", "black_left.tsai")
BLACK_RIGHT = os.path.join(os.path.dirname(__file__), "assets", "black_right.tsai")


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


def stereo(images: list, cameras: list, output: str, parameters: dict, debug=False):
    """Launch a parallel_stereo (ASP) based on a parameter dict

    If debug is used, print the command without launching it. Useful to show the command
    even without the ASP binaries available
    """
    params = format_dict(parameters["stereo"]["cmd"])

    cmd = "parallel_stereo {} {} {} {}".format(
        arg_to_str(images), arg_to_str(cameras), arg_to_str(output), params
    )

    if debug:
        print(cmd)
    else:
        sh(cmd)


def corr_eval(left, right, disp, output, parameters: dict, debug=False):
    """Launch a corr_eval (ASP) to evaluate the ncc of a stereo result"""
    params = format_dict(parameters.get("corr-eval", {}).get("cmd", {}))

    cmd = "corr_eval {} {} {} {} {}".format(params, left, right, disp, output)

    if debug:
        print(cmd)
    else:
        sh(cmd)
