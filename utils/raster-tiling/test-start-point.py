from raster_tiling import index_matrix as idxm
from raster_tiling import get_configs
from raster_tiling import parse_configs
# from raster_tiling import render
import os
import sys
os.environ['USE_PYGEOS'] = '0'
import geopandas as gp
from multiprocessing import Pool, Process
import math

from shapely.geometry import Polygon

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

# python3 utils/raster-tiling/test-start-point.py NZTM2000 1 qgis/full-nz-mono.qgz

def get_project_name():
    base = os.path.basename(QGIS_PATH).split(".")[0]
    out_dir = os.path.join(TILES_DIR, base)
    os.makedirs(out_dir, exist_ok=True)
    
    return out_dir  

def get_origin_cell(matrix_zoom, tile_span_x, tile_span_y, cmaxy, cminx):
    x_left = matrix_zoom[0]['topLeftCorner'][1]
    x_right = x_left + tile_span_x
    y_top = matrix_zoom[0]['topLeftCorner'][0]
    y_bottom = y_top - tile_span_y
    
    # from orgin, count down by span
    y_count = int(abs((y_top - abs(cmaxy)) / tile_span_y))
    x_count = int(abs((x_left + abs(cminx)) / tile_span_x))
    
    start_minx = x_left + (tile_span_x * x_count)
    start_maxy = y_top - (tile_span_y * y_count) 
    start_maxx = start_minx + tile_span_x
    start_miny = start_maxy - tile_span_y
    
    poly = Polygon([[start_minx, start_miny],
                    [start_maxx, start_miny],
                    [start_maxx, start_maxy],
                    [start_minx, start_maxy],
                    [start_minx, start_miny]])
    
    df = [{
        "row": y_count,
        "column": x_count,
        "geometry": poly
    }]
    
    origin_cell = gp.GeoDataFrame(df, crs=2193)
    origin_cell.to_file("data/test_origin.gpkg", driver="GPKG")
    
    return origin_cell, x_count, y_count

def rows(XleftOrigin, XrightOrigin, coverage_dissolve, matrix_zoom, column, out_dir, tile_span_y, Ytop, Ybottom, y_count, matrix_height):
    for row in range(y_count, matrix_height+y_count+1, 1):
        writeGeom = Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)]) 
        idx_inter = coverage_dissolve.loc[coverage_dissolve.intersects(writeGeom)]
        if not idx_inter.empty:
            # print(f"Making tile {row}, {column}")
            render(matrix_zoom, row, column, writeGeom, out_dir)         
        
        Ytop = Ytop - tile_span_y
        Ybottom = Ybottom - tile_span_y
        
def render(matrix_zoom, row, column, geom, out_dir):
    METRE_TO_INCH = 39.3701
    DPI = 90.71428571428571
    
    xmin, ymin, xmax, ymax = geom.bounds
    
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
    col_dir = os.path.join(zoom_dir, str(column))
    os.makedirs(zoom_dir, exist_ok=True)
    os.makedirs(col_dir, exist_ok=True)
    
    image_path = os.path.join(col_dir, f"{str(row)}.png")
    
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
    settings.setExtent(QgsRectangle(xmin, ymin, xmax, ymax))
    
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
    print(f"Making tiles for Zoom {ZOOM}...")
    matrix, resos = get_configs(CONFIGS_DIR, MATRIX_NAME)
    json_reso = parse_configs(matrix, resos)  
    matrix_zoom = [x for x in json_reso if x["identifier"] == ZOOM]
    out_dir = get_project_name()
    
    coverage = gp.read_file(COVERAGE)          
    coverage_dissolve = coverage.dissolve()
    cminx, cminy, cmaxx, cmaxy= coverage_dissolve.total_bounds
    
    cell_size = matrix_zoom[0]['resolution']
    tile_span_x = matrix_zoom[0]['tileWidth'] * cell_size
    tile_span_y = matrix_zoom[0]['tileHeight'] * cell_size

    origin_cell, x_count, y_count = get_origin_cell(matrix_zoom, tile_span_x, tile_span_y, cmaxy, cminx)
    minx, miny, maxx, maxy = origin_cell.total_bounds    
    
    XleftOrigin = minx
    XrightOrigin = XleftOrigin + tile_span_x
    YtopOrigin = maxy
    YbottomOrigin = YtopOrigin - tile_span_y
    
    matrix_width = math.ceil((abs(cminx) + abs(cmaxx)) / tile_span_x)
    matrix_height = math.ceil((abs(cmaxy) - abs(cminy)) / tile_span_y)
    
    pool = Pool(8)
    for column in range(x_count, matrix_width+x_count+1, 1):
        Ytop = YtopOrigin
        Ybottom = YbottomOrigin
        pool.apply_async(rows, args=(XleftOrigin, XrightOrigin, coverage_dissolve, matrix_zoom, column, out_dir, tile_span_y, Ytop, Ybottom, y_count, matrix_height))
        XleftOrigin = XleftOrigin + tile_span_x
        XrightOrigin = XrightOrigin + tile_span_x
    pool.close()
    pool.join()  
    
 
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
    