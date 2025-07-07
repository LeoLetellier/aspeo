#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ASPeo parameter file generator

Usage:
    asp_new.py [<preset>] [--path <path>]
    asp_new.py -h | --help

Options:
    -h --help       Show this screen
    <preset>        ASPeo parameters preset
    --path <path>   Path to save the parameter file
"""

import docopt
import os
from os.path import splitext, basename, dirname, join
from shutil import copyfile

from asp import parse_toml

PROJECT = parse_toml(os.path.join(os.path.dirname(__file__), "../pyproject.toml"))
VERSION = PROJECT["project"]["version"]
PRESET_FOLDER = "presets"


class Preset:
    def __init__(self, preset: str):
        self.preset = preset
        self.base_folder = dirname(dirname(__file__))
        self.avail = self.get_avail()

        if self.preset not in self.avail:
            raise ValueError("Invalid preset name. Presets are:", self.avail)

    def get_avail(self):
        """Check dynamically the available toml presets in repo"""
        files = os.listdir(join(self.base_folder, PRESET_FOLDER))
        tomls = [
            splitext(basename(f))[0]
            for f in files
            if splitext(basename(f))[1] == ".toml"
        ]
        return tomls

    def path(self):
        return join(self.base_folder, PRESET_FOLDER, self.preset + ".toml")


def generate_toml(preset, path=None):
    if preset is None:
        preset = "default"
    target = path if type(path) is str and path is not None else "./aspeo.toml"

    preset = Preset(preset)
    print(preset.path(), target)
    copyfile(preset.path(), target)
    print(target)
    write_version(target)
    print("Successfully wrote {} in the working directory!".format(target))


def write_version(file):
    with open(file, "r") as infile:
        content = infile.read()

    version_notice = "# ASPeo PARAMETER FILE (v{})\n".format(VERSION)
    content = version_notice + content

    with open(file, "w") as outfile:
        outfile.write(content)


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    preset = arguments["<preset>"]
    path = arguments["<path>"]

    generate_toml(preset, path=path)
