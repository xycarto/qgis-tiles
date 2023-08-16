#!/bin/bash

# bash utils/data-transfers/qgis-data-up.sh

source .creds

aws s3 sync qgis s3://qgis-tiles/qgis

aws s3 sync data/coverage s3://qgis-tiles/data/coverage