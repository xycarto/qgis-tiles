#!/bin/bash

# bash raster-tiles.sh qgis/full-nz-mono dev

# Set date
#DATE=$(date '+%Y-%m-%d')
DATE="2023-04-03"

# Get Inputs
QGIS_PROJ=$1
STATUS=$2
SCALES=(50000)
PROCESSORS=4
PROJ_NAME=$( basename $QGIS_PROJ )

# Set Dirs
RASTER_TILES="raster-tiles"
LOCAL_TILES="${RASTER_TILES}/${PROJ_NAME}"
QGIS_PROJ_DIR="qgis"
S3_DIR="raster-tiles/${STATUS}/${PROJ_NAME}/${DATE}/${PROJ_NAME}"
CONFIG_DIR="configs"

mkdir -p ${RASTER_TILES}
# rm -rf ${QGIS_PROJ_DIR}

# Get QGIS Project and Data
if [ ! -d ${QGIS_PROJ_DIR} ]
then
    echo "Project not found. Downloading..."
    aws s3 cp --quiet --recursive s3://${AWS_BUCKET}/qgis qgis
    echo $( ls qgis )
else
    echo "QGIS Project and Data Found. Skipping Download"
    echo $( ls qgis )
fi

jq -c '.[]' ${CONFIG_DIR}/scales.json | while read scl; 
do
    echo $scl
    python3 image-export.py ${QGIS_PROJ}.qgz $scl $PROCESSORS
done

python3 create-vrts.py ${QGIS_PROJ}
python3 raster-tiler.py 14 ${QGIS_PROJ}
python3 clean-dirs.py ${QGIS_PROJ}

echo "Uploading to S3"
aws s3 cp --recursive ${LOCAL_TILES} s3://${AWS_BUCKET}/${S3_DIR} --acl public-read

chmod 777 -R .

echo "Done!"

