from raster_tiling import index_matrix as idxm
from raster_tiling import get_configs
from raster_tiling import parse_configs
# from raster_tiling import render
import os
import sys
os.environ['USE_PYGEOS'] = '0'
import geopandas as gp
from multiprocessing import Pool
import math

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

# python3 utils/raster-tiling/render-zoom.py NZTM2000 0 qgis/full-nz-mono.qgz

# def tile_check(idx_inter):
#     print("checking for tiles...")
#     for index, row in idx
    

def parse_idx(idx):
    print("Find intersecting tiles...")
    coverage = gp.read_file(COVERAGE)
    coverage_dissolve = coverage.dissolve()
    idx_inter = idx.loc[idx.intersects(coverage_dissolve.geometry[0])]
    
    return idx_inter
    
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

def render(matrix_zoom, row, out_dir):
    METRE_TO_INCH = 39.3701
    DPI = 90.71428571428571
    
    print(type(row))
    xmin, ymin, xmax, ymax = row.geometry.bounds
    
    width = math.floor(
        abs(
            (((xmin - xmax) * METRE_TO_INCH) / float(matrix_zoom[0]['scaleDenominator']))
            * DPI
        )
        )
    height = math.floor(
        abs(
            (((ymin - ymax) * METRE_TO_INCH) / float(matrix_zoom[0]['scaleDenominator']))
            * DPI
        )
    )
    
    zoom_dir = os.path.join(out_dir, matrix_zoom[0]['identifier'])
    col_dir = os.path.join(zoom_dir, str(row.column))
    os.makedirs(zoom_dir, exist_ok=True)
    os.makedirs(col_dir, exist_ok=True)
    
    image_path = os.path.join(col_dir, f"{str(row.row)}.png")
    
    # Start Map Settings
    settings = QgsMapSettings()
    settings.setOutputSize(QSize(width, height))

    settings.setDestinationCrs(QgsCoordinateReferenceSystem.fromEpsgId(2193))
    
    p = QPainter()
    img = QImage(QSize(width, height), QImage.Format_ARGB32_Premultiplied)
    p.begin(img)        
    p.setRenderHint(QPainter.Antialiasing)

    # Set layers to render. Only renders "checked" layers
    layers = list([lyr for lyr in QGIS.layerTreeRoot().checkedLayers()])
    settings.setLayers(layers)

    # Set Extent
    settings.setExtent(QgsRectangle(row.xmin, row.ymin, row.xmax, row.ymax))
    
    # setup qgis map renderer
    # print("Rendering...")
    render = QgsMapRendererCustomPainterJob(settings, p)
    render.start()
    render.waitForFinished()
    p.end()

    # save the image
    # print("Saving Image...")
    img.save(image_path, "png")    

def main():
    matrix, resos = get_configs(CONFIGS_DIR, MATRIX_NAME)
    json_reso = parse_configs(matrix, resos)  
    matrix_zoom = [x for x in json_reso if x["identifier"] == ZOOM]
    out_dir = get_project_name()
    idx = get_index(matrix_zoom)  
    idx_inter = parse_idx(idx)
    print(f"Making tiles for Zoom {ZOOM}...")
    with Pool(8) as pool:
        # prepare arguments
        items = [(matrix_zoom, row, out_dir) for index, row in idx_inter.iterrows()]
        # issue tasks to the process pool and wait for tasks to complete
        pool.starmap(render, items) 
    
if __name__ == "__main__": 
    # Inputs   
    MATRIX_NAME = sys.argv[1]   
    ZOOM = sys.argv[2]
    QGIS_PATH = sys.argv[3]
    COVERAGE=sys.argv[4]
    
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
    