# QGIS to Raster Tiles

Method to pre-render raster tile caches direct from QGIS project.

- This is not yet a fully developed repo for easy use. There are plenty of bugs, hard coded items, and tricky steps. 
- Tested in Linux Enviroment
- Project is still under development and subject to change without notice

## Required

- Docker
- Make

## Features

- Make commands
- Captures zoom rules built into QGIS project
- Local and scaled processing
- Ability to limit by zoom and coverage region for processing
- Single line command to process
- Multi-threaded
- WMTS
- Gateaux processing methods

## Limitations

- Method only for NZTM(2193) or Web Mercator(3857) Projections
- Some naming for necessary files still hard coded into process
- All input variables are required. Currently no defult settings
- At least one coverage file is necessary
- Tile size currently limited to **ONLY** 256x256 tiles

## Basic Method

```
git clone git@github.com:xycarto/qgis-tiles.git
make docker-pull
```

1. Create QGIS project in desired projection
1. Create coverage files (GPKG polygons)
1. Update coverage JSON for processing. See [here](https://github.com/xycarto/qgis-tiles/tree/main/utils/raster-tiling/configs/coverages) for example.
1. Process from `makefile`

## Outputs

- Method outputs to `tiles` directory using the name of the QGIS project

## Make Example

Run process in NZTM to produce zooms 0-4.

```
time make coverage epsg=2193 qgis="qgis/full-nz-mono.qgz" minzoom=0 maxzoom=4 version=v1
```

## Process Explanation

The process creates pre-rendered raster tile caches from a QGIS project.  The main process is controlled from the `coverage.sh` [file](https://github.com/xycarto/qgis-tiles/blob/main/utils/raster-tiling/coverage.sh) and launched by using `make coverage`. Required for `make coverage` is:

```
epsg=[Either 2193 or 3857]
qgis=[path/to/qgis.qgz file]
minzoom=[int value]
maxzoom=[int value] 
version=[version like v1]
```

The `coverage.sh` relies on having a coverage JSON in place, named the same as the Tile Matrix you plan to use. For example, if users are working in NZTM(2193), the [Tile Matrix](https://github.com/xycarto/qgis-tiles/tree/main/utils/raster-tiling/configs/matrix) used is "NZTM2000", therefore, the coverage JSON is required to be named `NZTM2000-coverage.json` and must sit in this directory: `raster-tiling/configs/coverages`. Unfortunately, this is necessary for now, but will change in the future.

The coverage JSON might look like the following:

Multiple coverages

```
{
    "NZTM2000": [
        {
            "identifier": "full-nz",
            "minzoom": 0,
            "maxzoom": 7,
            "path": "data/coverage/NZTM2000/full-nz.gpkg"
        },
        {
            "identifier": "mid-nz",
            "minzoom": 8,
            "maxzoom": 11,
            "path": "data/coverage/NZTM2000/mid-nz.gpkg"
        },
        {
            "identifier": "small-nz",
            "minzoom": 12,
            "maxzoom": 14,
            "path": "data/coverage/NZTM2000/small-nz.gpkg"
        }
        
    ]
}
```

Single Coverage

```
{
    "WebMercatorQuad": [
        {
            "identifier": "full-world",
            "minzoom": 0,
            "maxzoom": 10,
            "path": "data/coverage/WebMercatorQuad/world-full.gpkg"
        }
        
    ]
}
```

Necessary for the coverage json is a `GPKG` file covering the region a user desires to tile.  The GPKG file **MUST** be in the same projection as the QGIS project. Users will need to create their own coverage GPKGs and set the path in the JSON.  

The main processing happens here: https://github.com/xycarto/qgis-tiles/blob/main/utils/raster-tiling/raster-tiler.py

Raster tile caches are automatically sent to the `tiles` directory using the format `tiles/[project_name]/[version]/[project_name]/[zoom_level]/[column]/[row].png`. Manual modifications may be made in this file to produce JPG outputs if desired. In the future, this will be set as an input variable.

The tiling method employs a mutli-threaded process using all availaable cores on the machine on which it runs. If fewer cores are desired due to resource constraints, a modification can be made here: https://github.com/xycarto/qgis-tiles/blob/1d6736541279e870e78b18a2b475ede81be0e98a/utils/raster-tiling/raster-tiler.py#L256

## Things to know

- Raster tiling can get very large very quickly. Producing tiles for all of NZ at zoom 14 will result in many millions of tiles. This will be a very long and resource intensive process. PROCEED WITH CAUTION

- This repo is moving quickly and is likley to change without notice. This README may be out of date.

- As of 24-08-2023, the method has only been tested on Ubuntu systems

- Users are resposible for their own uploads of caches for access to a web client.

- An unstable example for consumption into a web clientusing Openlayers6 can be found [here](https://github.com/xycarto/qgis-tiles/tree/main/test) for NZTM.

## Upcoming Modifications

- More user friendly tooling

- Custom tile matrix creation for expanded projections

- Handling more projections

- Custom projection vector tiling

- Automatic WMTS creation

## Contact

- Like the method and want it further developed? Contact me at: ian@xycarto or put something in the issues

- Currently, this project is a labour of love and is developed in my spare time. I am happy to hear and accept changes from anyone on how to make the tool better. Funding is likley to make those changes/fixes happen. 