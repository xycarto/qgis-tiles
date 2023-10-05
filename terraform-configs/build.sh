#!/bin/bash

# bash build.sh

source .creds

echo "Cloning Git repo..."
git clone --branch terraform https://${TOKEN}@github.com/xycarto/qgis-tiles.git

cp -r .creds qgis-tiles

echo "Running tiles..."
cd qgis-tiles

make docker-pull

mkdir -p qgis

echo "Downloading data..."
make qgis-download

echo "Rendering tiles..."
make coverage epsg=2193 qgis="qgis/full-nz-mono.qgz" minzoom=0 maxzoom=0 version=v1

exit