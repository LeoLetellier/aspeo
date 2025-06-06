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

PRESET_FOLDER = "presets"


class Preset:
    def __init__(self, preset: str):
        self.preset = preset
        self.base_folder = dirname(__file__)
        self.avail = self.get_avail()

        if self.preset not in self.avail:
            raise ValueError("Invalid preset name")

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
    target = path if path is not None else "./aspeo.toml"
    preset = Preset(preset)
    copyfile(preset.path(), target)
    print("Successfully wrote {} in the working directory!".format(target))


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)
    preset = arguments["<preset>"]
    path = arguments["--path"]
    if preset is None:
        preset = "default"

    generate_toml(preset, path=path)
