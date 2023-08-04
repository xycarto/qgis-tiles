from raster_tiling import index_matrix as idxm
from raster_tiling import get_configs
from raster_tiling import parse_configs
from raster_tiling import render
import os
import sys
os.environ['USE_PYGEOS'] = '0'
import geopandas as gp
from multiprocessing import Pool

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

# python3 utils/raster-tiling/render-zoom.py NZTM2000 0 qgis/full-nz-mono.qgz

def get_index(matrix_zoom):
    gpkg = os.path.join(GPKG_DIR, f"{str(matrix_zoom[0]['scaleDenominator'])}.gpkg")
    if not os.path.exists(gpkg):
        print("Making index...")
        crs = 2193
        idxm(matrix_zoom[0], gpkg, crs)
    idx = gp.read_file(gpkg)
    return idx

def get_project_name():
    base = os.path.basename(QGIS_PATH).split(".")[0]
    out_dir = os.path.join(TILES_DIR, base)
    os.makedirs(out_dir, exist_ok=True)
    
    return out_dir

def main():
    matrix, resos = get_configs(CONFIGS_DIR, MATRIX_NAME)
    json_reso = parse_configs(matrix, resos)  
    matrix_zoom = [x for x in json_reso if x["identifier"] == ZOOM]
    out_dir = get_project_name()
    idx = get_index(matrix_zoom)  
    for index, row in idx.iterrows():
        render(matrix_zoom, row, out_dir, QGIS) 
    
if __name__ == "__main__": 
    # Inputs   
    MATRIX_NAME = sys.argv[1]   
    ZOOM = sys.argv[2]
    QGIS_PATH = sys.argv[3]
    
    # DIRS 
    DATA_DIR = "data"    
    TILES_DIR = "tiles"
    CONFIGS_DIR = os.path.join("utils", "raster-tiling", "configs")
    GPKG_DIR = os.path.join(DATA_DIR, "idx", MATRIX_NAME)
        
    for d in [DATA_DIR, CONFIGS_DIR, GPKG_DIR, TILES_DIR]:
        os.makedirs(d, exist_ok=True)
    
    print("Setting QGIS paths")
    qgs = QgsApplication([], False)
    QgsApplication.setPrefixPath("/usr", True)
    QgsApplication.setThemeName("default")
    app = QgsApplication([], False, ".local/share/QGIS/QGIS3/profiles/default")
    app.initQgis()
    authMgr = app.authManager()

    QGIS = QgsProject.instance()

    QGIS.read(QGIS_PATH)
        
    main()
    