#!/bin/bash

# bash utils/raster-tiling/coverage.sh 2193 0 qgis/full-nz-mono.qgz "data/coverage/full-nz.gpkg" "v1"
# time make coverage epsg=2193 qgis="qgis/full-nz-mono.qgz" minzoom=10 maxzoom=11 version=v1 

EPSG=$1
PROJECT=$2
MINZOOM=$3
MAXZOOM=$4
VERSION=$5

# Set Matrix Syntax
if [[ ${EPSG} = "2193" ]]; then
    MATRIX="NZTM2000"
elif [[ ${EPSG} == "3857" ]]; then
    MATRIX="WebMercatorQuad"
else
    echo "Invalid EPSG code. Projection only supports 2913 or 3857"
    exit
fi

COVERAGE_JSON="utils/raster-tiling/configs/coverages/${MATRIX}-coverage.json"

jq -c '."'"$MATRIX"'"[]' $COVERAGE_JSON | while read cover;
do
    echo $cover
    minzoom=$(jq .minzoom <<< $cover)
    maxzoom=$(jq .maxzoom <<< $cover)
    path=$(jq .path <<< $cover)

    for zoom in $( seq $minzoom $maxzoom)
    do
        if [[ $zoom -ge $MINZOOM ]]; then
            make no-index matrix=${MATRIX} zoom=${zoom} qgis=${PROJECT} coverage=${path} version=$VERSION
            if [[ $zoom -eq $MAXZOOM ]]; then
                exit
            fi
        fi
    done   
done
