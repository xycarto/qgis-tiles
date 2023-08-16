from raster_tiling import index_matrix as idxm
from raster_tiling import get_configs
from raster_tiling import parse_configs
import glob
import json
import os
import sys

# python3 utils/raster-tiling/idx-matrix.py NZTM2000 0

def main():    
    matrix, resos = get_configs(CONFIGS_DIR, MATRIX_NAME)
    json_reso = parse_configs(matrix, resos)    
    matrix_zoom = [x for x in json_reso if x["identifier"] == ZOOM]
    
    gpkg = os.path.join(GPKG_DIR, f"{str(matrix_zoom[0]['scaleDenominator'])}.gpkg")
    csv = os.path.join(GPKG_DIR, f"{str(matrix_zoom[0]['scaleDenominator'])}.csv")
    crs = 2193
    if not os.path.exists(gpkg):
        idxm(matrix_zoom[0], gpkg, crs)    

if __name__ == "__main__": 
    # Input Matrix name   
    MATRIX_NAME = sys.argv[1]   
    ZOOM = sys.argv[2]
    
    # DIRS 
    DATA_DIR = "data"    
    CONFIGS_DIR = os.path.join("utils", "raster-tiling", "configs")
    GPKG_DIR = os.path.join(DATA_DIR, "idx", MATRIX_NAME)
    
    for d in [DATA_DIR, CONFIGS_DIR, GPKG_DIR]:
        os.makedirs(d, exist_ok=True)
        
    main()