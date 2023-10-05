#!/bin/bash

# bash build.sh

source .creds

echo "Cloning Git repo..."
git clone --branch terraform https://${TOKEN}@github.com/xycarto/qgis-tiles.git

cp -r .creds qgis-tiles

echo "Running tiles..."
cd qgis-tiles && \
    make docker-pull

exit