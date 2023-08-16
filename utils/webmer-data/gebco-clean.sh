#!/bin/bash

# utils/webmer-data/gebco-clean.sh

IN_GEBCO="qgis/qgis-data/raster/web-mercator/gebco_2023_sub_ice_topo_geotiff"
OUT_GEBCO="qgis/qgis-data/raster/web-mercator/gebco"
CUTLINE="qgis/qgis-data/vector/web-mercator/webmercator-extent.gpkg"

tif_list=$( find ${IN_GEBCO} -name "*.tif" )

for tif in ${tif_list[@]}; do
    echo $tif
    base=$( basename $tif )
    gdalwarp -overwrite -s_srs EPSG:4326 -t_srs EPSG:3857  -cutline $CUTLINE -crop_to_cutline -tr 4500 4500 $IN_GEBCO/$base $OUT_GEBCO/bathy/$base
    gdaldem hillshade -multidirectional -compute_edges $OUT_GEBCO/bathy/$base $OUT_GEBCO/bathy-hs/$base
    gdaladdo -ro $OUT_GEBCO/bathy/$base
    gdaladdo -ro $OUT_GEBCO/bathy-hs/$base
done    

