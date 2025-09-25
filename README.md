# Ames Stereo Pipeline (ASP) Sequential Workflows for Earth Observation

Workflows using [Ames Stereo Pipeline](https://github.com/NeoGeographyToolkit/StereoPipeline) for Earth Observation by using image correlation to produces DSMs and displacement maps, making ASP commands easily scalable for larger dataset.

> [!IMPORTANT]
> This project provides workflows around common ASP commands and proposes some presets for specific cases. However it does not discuss the choice or need for ASP parameters for each of these commands.
>
> The code is provided 'AS IS' without any warranty of any kind (see License: TO BE DETERMINED).

Commands can be runned for testing purposes without launching processes by adding `-d` (debug), and printing additionnal information in shell by adding `-v` (verbose).

## Installation

This codebase is developped in python and need a working python environment to be used. Library requirements can be found in the `pyproject.toml` file.

For convenience, the bash files in the `export` directory can be added to path for a simpler usage (exporting the `aspeo` command). A virtual environment can be created in this repository (for example by running `uv venv` if using [***uv***](https://github.com/astral-sh/uv)) and will be used by the bash script instead of the `python` available in `PATH`.

## Parameter file

This workflow uses a toml file to launch ASP binaries. For the parts corresponding to an ASP command, all arguments on sub-categories will be added to the corresponding ASP command with the following rules:

* single letter keyword: `t = "nadirpinhole"` -> `-t nadirpinhole`
* large keyword: `alignment-method = "none"` -> `--alignment-method none`
* bracket value: `corr-kernel = [9, 9]` -> `--corr-kernel 9 9`
* boolean value: `no-bigtiff = true`-> `--no-bigtiff`
* absent: not used

So you can add/modify/remove any ASP specific parameter to modulate the run or use a new ASP version.

Global parameters are used to configure how the workflow behave.

The parameter file can be generated using `asp_new`, which retrieve one of the presets available in `./presets/`. You can try the following command using the `default` preset:

```bash
aspeo new preset
```

## Project Processing Structure

The processing folder is defined as followed:

- `./BA/`: store the computed bundle adjustement
- `./MP/PAN/`: store the computed panchromatic ortho-rectified images
- `./MP/MS/`: store the computed multi-spectral ortho-rectified images
- `./MP/PANSHARP/`: store the pansharpened images
- `./STEREO/id1-id2/stereo-`: stereo processing files

A directory prefix can be indicated where all source files will be fetched.

Each source dataset can be described in the parameter file (under a `[[source]]` section, one for each dataset) or derived from file in some cases. They can also be derived from the pairs file (see below). Text file can be red be ignoring some header lines (i.e setting the global parameter `pairs-header` to `true`). The following attributes can be defined:

- `id`: image identifier (i.e the acquisition date DDMMYYY)
- `pan`: raw panchromatic image
- `cam`: camera associated to `pan`
- `ms`: raw multi-spectral image
- `cam-ms`: camera associated to `ms`
- `mp`: ortho-rectified (map-projected) image
- `pleiades`: folder containing pleiades acquisition data (*.TIF, *.DIM, ...)

Each of theses attributes can have a global prefix and suffix defined in the parameter file header, using `attribute-prefix` or `attribute-suffix`.

If the `pan` (must set global parameter `derive-pan` to `true`) or `mp` fields are not given, they will be derived from the id and their respective prefix and suffix.

Each source image is defined separately. For stereo, pairs must be indicated. These pairs can be constructed in a separate file (one pair per line, space separated ids) which will be indicated with the global parameter `pairs`. All ids must be defined as sources. If no file is given, all possible bi-pairs (pairs of 2 images) will be used.

If map-projected images are present in the `./MP/PAN/` folder, they will be automatically added to the corresponding source dataset. This allows successive launch of the map-projection and stereo commands.

These behaviours can be checked in the script `./src/params.py`.

## Map Projection

Common image processing and visualization requires having ortho-rectified images (= map-projected). Raw images contains distorsions due to the lens and acquisition characteristics that have to be corrected to produce a "map view" of the image (where all pixels corresponds to equivalent flat ground area).

Often, the delivered images are already ortho-rectified. However, Pléiades images for instance can be retrieved raw (for example to use the camera differences to produce a DSM).

For map projection, are needed the images with their corresponding cameras, and a DEM. For Pléiades images, raw images and cameras (DIM) can be retrieved directly using the `pleiades` keyword.

For map-projecting panchromatic or multi-spectral images, the associated attribute must be defined for each dataset and the resolution of output images set as global variables in the parameter file header using `mp-pan` and `mp-ms`. These parameters will be used as the `tr` value for the command (by defining them here, you can have different resolution for pan and ms).

```bash
aspeo mp aspeo.toml
```

For more detailled processing, additionnal steps can be used:

- `bundle-adjust`: Bundle Adjustement corrects empirically the cameras for a better fit
- **map-project**: for Panchromatic (P) and/or Multispectral (MS) data
- `pansharp`: Pansharpening (GDAL) uses the P data (with better resolution) as additionnal information for resampling MS data pto this better resolution
- `orbitviz`: Generate a kml to visualize the orbit and camera position during the acquisition

Check the `mp_pleiades` preset for additionnal information.

## Pixel tracking

The pixel tracking workflow takes two map-projected images with respective cameras to compute the disparity map (correspondance of individual pixels) between the two. Correlation is directly stopped before triangulation (ASP correlator mode).

Best practice is to have all input images in the same folder, and with a name with only the date or identifier changing. That way, a pairs file can be defined for the used pairs which will serve to derive the map-projected files from the input folder, mp prefix, identifier, and mp-suffix.

```bash
aspeo pt aspeo.toml
```

For more detailled processing, additionnal steps can be used:

- **stereo**: using `correlator-mode`
- `corr-eval`: Computing the normalized cross correlation metrics (NCC) for each pixel given the resulting disparities for the input images

Check the `pt_pleiades` preset for additionnal information.

## DSM generation

Using map-projected images and given their cameras, the 3D position of each pixels can be reconstructed by triangulation after disparity estimation. This produces a Digital Surface Model (DSM).

For more detailled processing, additionnal steps can be used:

- **stereo**
- `pc-align`: Move the resulting point cloud to fit well known positions (GCPs or other point cloud)
- `point2dem`: Sample the resulting point cloud to generate a raster DSM (one value per pixel)
- `dem-mosaic`: Merge multiple raster DSM and smooth overlapping areas to produce a unique global raster DSM

Check the `dsm_pleiades` preset for additionnal information.

## Miscellaneous

### Pléiades folder information

Information (acquisition date, size, ...) about a Pléiades data folder can be retrieved using the following command:

```bash
pleiadesinfo folder
```
