# Ames Stereo Pipeline (ASP) Sequential Workflows for Earth Observation

Workflow using Ames Stereo Pipeline for Earth Observation by using image correlation to produces DSMs and displacement maps, making ASP commands easily scalable for larger dataset.

Commands can be runned for testing purposes without launching processes by adding `-d` (debug), and printing additionnal information in shell by adding `-v` (verbose).

## Installation

This codebase is developped in python and need a working python environment to be used. Library requirements can be found in the `pyproject.toml` file.

For convenience, the bash files in the `export` directory can be added to path for a simpler usage (exporting the `aspeo` command). A virtual environment can be created in this repository (for example by running `uv venv` if using *uv*) and will be used by the bash script instead of the `python` available in `PATH`.

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

```bash
aspeo new default
```

## Map Projection

Common image processing and visualization requires having ortho-rectified images (= map-projected). Raw images contains distorsions due to the lens and acquisition characteristics that have to be corrected to produce a "map view" of the image (where all pixels corresponds to equivalent flat ground area).

Often, the delivered images are already ortho-rectified. However, Pléiades images for instance can be retrieved raw (for example to use the camera differences to produce a DSM).

For map projection, are needed the images with their corresponding cameras, and a DEM. For Pléiades images, raw images and cameras (DIM) can be retrieved directly using the `pleiades` keyword.

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

Images need to be registrated in the parameter file using a `[[source]]` section for each image. The section contains an `id` to identify the image, a path to the map-projected image `mp` and to its camera `cam`. If no camera is provided, a dummy tsai will be used instead. If no image path is provided, the id will be used instead. For retrieving a complete path, the `mp` path will be prefixed and suffixed using `src_prefix` and `src_suffix` defined in the `run` section. For example, in your images are named after their dates, put the date as `id` and indicate the prefix and suffix.

For pair selection, indicate a file in the section `stereo` with the keyword `pairs`. This file need to indicate a pair on each line, using both `id`s separated by space. If not given, all pairs will be used.

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
