#!/bin/bash

# bash utils/raster-tiles.sh qgis/full-nz-mono

# Set date

# Get Inputs
QGIS_PROJ=$1
PROCESSORS=4
PROJ_NAME=$( basename $QGIS_PROJ )

# Set Dirs
RASTER_TILES="tiles/raster-tiles"
LOCAL_TILES="${RASTER_TILES}/${PROJ_NAME}"
S3_DIR="raster-tiles/${PROJ_NAME}"
CONFIG_DIR="configs"

mkdir -p ${RASTER_TILES}

jq -c '.[]' ${CONFIG_DIR}/scales.json | while read scl; 
do
    echo $scl
    python3 utils/image-export.py ${QGIS_PROJ}.qgz $scl $PROCESSORS
done

scl_arr=( $(jq -r '.[]' configs/scales.json ) )

scales=$( echo "${scl_arr[@]}" | sed 's/ /,/g' )

python3 utils/create-vrts.py ${QGIS_PROJ} $scales
python3 utils/raster-tiler.py 14 ${QGIS_PROJ}
python3 utils/clean-dirs.py ${QGIS_PROJ}

chmod 777 -R .

echo "Done!"

