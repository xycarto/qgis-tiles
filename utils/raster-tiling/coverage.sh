#!/bin/bash

# bash utils/raster-tiling/coverage.sh NZTM2000 "qgis/full-nz-mono.qgz" 6

MATRIX=$1
PROJECT=$2
MAXZOOM=$3

COVER="utils/raster-tiling/configs/coverage.json"
COVERAGES="data/coverage"

coverage_list=$( ls $COVERAGES)

for coverage in ${coverage_list[@]}
do
    file="${COVERAGES}/$coverage"
    echo $file
    json=$(cat $COVER | jq --arg cover ${file} '."nztm-coverages"[] | select(.path == $cover)')
    minzoom=$(jq .minzoom <<< $json)
    maxzoom=$(jq .maxzoom <<< $json)
    path=$(jq .path <<< $json)
    for zoom in $( seq $minzoom $maxzoom)
    do
        make no-index matrix=${MATRIX} zoom=${zoom} qgis=${PROJECT} path=${path}
        if [[ $zoom -eq $MAXZOOM ]]; then
            exit
        fi
    done
done

