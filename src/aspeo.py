#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check ASPeo version

Usage:
    aspeo.py
"""

from asp import parse_toml
import os
import docopt

PROJECT = parse_toml(os.path.join(os.path.dirname(__file__), "../pyproject.toml"))
VERSION = PROJECT["project"]["version"]

if __name__ == "__main__":
    docopt.docopt(__doc__)
    print("ASPeo version: v{}".format(VERSION))
