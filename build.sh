#!/bin/bash

set -ex ## fail if crash and set to stdout
export RUN=

make qgis-data-down

# make coverage epsg=2193 qgis="qgis/full-nz-mono.qgz" minzoom=0 maxzoom=11 version=v1

make coverage epsg=3857 qgis=qgis/world-webmer.qgz minzoom=0 maxzoom=10 version=v1