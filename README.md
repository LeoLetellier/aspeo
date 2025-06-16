# ASPeo

Workflow using Ames Stereo Pipeline for Earth Observation by using image correlation to produces DSMs and displacement maps.


## Parameter file

This workflow uses a toml file to launch ASP binaries. For the parts corresponding to an asp command, all arguments on the `cmd` keyword will be added to the asp command with the following rules:

* single letter keyword: `t = "nadirpinhole"` -> `-t nadirpinhole`
* large keyword: `alignment-method = "none"` -> `--alignment-method none`
* bracket value: `corr-kernel = [9, 9]` -> `--corr-kernel 9 9`
* boolean value: `no-bigtiff = true`-> `--no-bigtiff`

So you can add/modify/remove any asp specific parameter to modulate the run or use a new asp version.

Other parameters are used to configure how the workflow behave.

The parameter file can be generated using `asp_new`, which retrieve one of the presets available in `./presets/`.

## Pixel tracking

The pixel tracking workflow takes two map-projected images with respective cameras to compute the disparity map between the two. Correlation is directly stopped before triangulation.

Images need to be registrated in the parameter file using a `[[source]]` section for each image. The section contains an `id` to identify the image, a path to the map-projected image `mp` and to its camera `cam`. If no camera is provided, a dummy tsai will be used instead. If no image path is provided, the id will be used instead. For retrieving a complete path, the `mp` path will be prefixed and suffixed using `src_prefix` and `src_suffix` defined in the `run` section. For example, in your images are named after their dates, put the date as `id` and indicate the prefix and suffix.

For pair selection, indicate a file in the section `stereo` with the keyword `pairs`. This file need to indicate a pair on each line, using both `id`s separated by space. If not given, all pairs will be used.

NCC metric can be generated at the end of the run by specifying `[corr-eval]` in the parameter file.

``crop > mp-pan > iamge-align > stereo (stop point 5) > corr-eval``


## DSM generation

WORK IN PROGRESS

``ba > crop > mp-pan > stereo > pc-align > p2d > dmos``

## Map-projection

WORK IN PROGRESS

``ba > mp-pan > mp-ms > pansharp > orbitviz``

## Adding the scripts to path

To isolate the files form PATH, exports to bash files are available in the folder `./export/`. The used `python` environment can be overriden there.
