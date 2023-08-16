#!/bin/bash

# bash utils/data-transfers/qgis-data-up.sh

source .creds

mkdir -p data/coverage

aws s3 sync --quiet s3://qgis-tiles/qgis qgis 

aws s3 sync --quiet s3://qgis-tiles/data/coverage data/coverage