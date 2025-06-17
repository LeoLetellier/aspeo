# Ames Stereo Pipeline (ASP) Sequential Workflows for Earth Observation

Workflow using Ames Stereo Pipeline for Earth Observation by using image correlation to produces DSMs and displacement maps.


## Parameter file

This workflow uses a toml file to launch ASP binaries. For the parts corresponding to an asp command, all arguments on sub-categories will be added to the corresponding asp command with the following rules:

* single letter keyword: `t = "nadirpinhole"` -> `-t nadirpinhole`
* large keyword: `alignment-method = "none"` -> `--alignment-method none`
* bracket value: `corr-kernel = [9, 9]` -> `--corr-kernel 9 9`
* boolean value: `no-bigtiff = true`-> `--no-bigtiff`
* absent: not used

So you can add/modify/remove any asp specific parameter to modulate the run or use a new asp version.

Global parameters are used to configure how the workflow behave.

The parameter file can be generated using `asp_new`, which retrieve one of the presets available in `./presets/`.

## Pixel tracking

The pixel tracking workflow takes two map-projected images with respective cameras to compute the disparity map between the two. Correlation is directly stopped before triangulation.

Images need to be registrated in the parameter file using a `[[source]]` section for each image. The section contains an `id` to identify the image, a path to the map-projected image `mp` and to its camera `cam`. If no camera is provided, a dummy tsai will be used instead. If no image path is provided, the id will be used instead. For retrieving a complete path, the `mp` path will be prefixed and suffixed using `src_prefix` and `src_suffix` defined in the `run` section. For example, in your images are named after their dates, put the date as `id` and indicate the prefix and suffix.

For pair selection, indicate a file in the section `stereo` with the keyword `pairs`. This file need to indicate a pair on each line, using both `id`s separated by space. If not given, all pairs will be used.

NCC metric can be generated at the end of the run by specifying `[corr-eval]` in the parameter file.

implemented:

``align > stereo (stop point 5) > corr_eval``

not tested on asp/gdal command

## DSM generation

WORK IN PROGRESS

implemented:

``stereo > pc-align > p2d > dmos``

## Map-projection

WORK IN PROGRESS

target:

``crop > ba > mp-pan > mp-ms > pansharp > orbitviz``

implemented:

``ba > mp-pan > mp-ms > pansharp > orbitviz``

not tested on real asp/gdal cmd

## Adding the scripts to path

To isolate the files form PATH, exports to bash files are available in the folder `./export/`. A custom `.venv` virtual environment can be created in the repo and will be used instead of `PATH` `python` if exists.


## TODO

- [ ] add verif to use already processed files
- [ ] add logging console and file
- [ ] write configs toml
- [ ] test workflows on actual commands
