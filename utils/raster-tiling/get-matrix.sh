#!/bin/bash

wget --no-check-certificate https://raw.githubusercontent.com/linz/NZTM2000TileMatrixSet/master/raw/NZTM2000.json -O utils/raster-tiling/configs/matrix/NZTM2000.json

wget --no-check-certificate https://raw.githubusercontent.com/opengeospatial/2D-Tile-Matrix-Set/master/registry/json/WebMercatorQuad.json  -O utils/raster-tiling/configs/matrix/WebMercatorQuad.json 