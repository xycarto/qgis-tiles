#!/bin/bash

# bash utils/render-cog.sh "qgis/full-nz-mono"

scales=(32000000 16000000 8000000 4000000 2000000 1000000 500000)
PROCESSORS=4
QGIS_PROJ=$1

proj_name=$( basename $QGIS_PROJ )
echo $proj_name

for scl in ${scales[@]}
do
    python3 utils/image-export.py "${QGIS_PROJ}.qgz" $scl $PROCESSORS
done

scales_new=$( echo ${scales[@]} | sed 's/ /,/g' )
echo ${scales_new}

python3 utils/create-cog.py "${QGIS_PROJ}.qgz" ${scales_new}

