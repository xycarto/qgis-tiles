# QGIS Tiler - Raster Tiles

Method to take QGIS project with zoom scales and create raster tiles maintaining the zoom rules from QGIS. Method developed for NZTM and Web Mercator projections

## Limitations (16 Aug 2023)

- Only available for 256 x 256 tiles
- Method for pre-rendered tile caches only
- Must have coverage files (developed by user)
- Relies on assumed naming of files in some places
- Limited to Linux OS

## Required 

- Docker
- Make

## Method Overview

1. Create QGIS project
1. Develop zoom rules in QGIS
1. Develop coverage areas for rendering
1. Develop coverage JSON
1. Render tiles based on coverage

## Method Command Example

Render tiles based on coverage

```
make coverage epsg=2193 qgis="qgis/full-nz-mono.qgz" minzoom=0 maxzoom=10 version=v1
```