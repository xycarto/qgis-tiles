import os
from shapely.geometry import box
from shapely.geometry import Polygon
os.environ['USE_PYGEOS'] = '0'
import geopandas as gp
import math
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
import glob
import json


def get_reso(scale):    
    MPP = 0.00028 # Meters per Pixel
    resolution =  scale * MPP
    
    return resolution

def index_matrix(matrix, gpkg, crs):
    cell_size = matrix['resolution']
    tile_span_x = matrix['tileWidth'] * cell_size
    tile_span_y = matrix['tileHeight'] * cell_size

    XleftOrigin = matrix['topLeftCorner'][1]
    XrightOrigin = XleftOrigin + tile_span_x
    YtopOrigin = matrix['topLeftCorner'][0]
    YbottomOrigin = YtopOrigin - tile_span_y
    polygons = []
    for i in range(matrix['matrixWidth']):
        Ytop = YtopOrigin
        Ybottom = YbottomOrigin
        for j in range(matrix['matrixHeight']):
            gridNum = [j,i]
            writeGeom = Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)])
            polygons.append(
                {
                'row': j,
                'column': i,
                'geometry': writeGeom
                }
            ) 
            Ytop = Ytop - tile_span_y
            Ybottom = Ybottom - tile_span_y
        XleftOrigin = XleftOrigin + tile_span_x
        XrightOrigin = XrightOrigin + tile_span_x
            
    print("Writing polygons")
    grid = gp.GeoDataFrame(polygons, crs=crs)
    grid.to_file(gpkg, driver="GPKG")
    
def get_configs(configs_dir, matrix_name):
    configs = glob.glob(f"{configs_dir}/{matrix_name}*")
    for config in configs:
        if "resolutions" in config:
            with open(config) as jfile:
                resos = json.load(jfile)
        else:
            with open(config) as jfile:
                matrix = json.load(jfile)
            
    return matrix, resos

def parse_configs(matrix, resos):
    json_reso = []
    for level in matrix['tileMatrix']:
        for res in resos['nztm-resolutions']:
            if res['identifier'] == level['identifier']:
                level['resolution'] = res['resolution']
                json_reso.append(level)
                
    return json_reso
    
def render(matrix_zoom, row, out_dir, project):
    METRE_TO_INCH = 39.3701
    DPI = 90.71428571428571
    
    width = math.floor(
        abs(
            (((row.xmin - row.xmax) * METRE_TO_INCH) / float(matrix_zoom[0]['scaleDenominator']))
            * DPI
        )
        )
    height = math.floor(
        abs(
            (((row.ymin - row.ymax) * METRE_TO_INCH) / float(matrix_zoom[0]['scaleDenominator']))
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
    layers = list([lyr for lyr in project.layerTreeRoot().checkedLayers()])
    settings.setLayers(layers)

    # Set Extent
    settings.setExtent(QgsRectangle(row.xmin, row.ymin, row.xmax, row.ymax))
    
    # setup qgis map renderer
    print("Rendering...")
    render = QgsMapRendererCustomPainterJob(settings, p)
    render.start()
    render.waitForFinished()
    p.end()

    # save the image
    print("Saving Image...")
    img.save(image_path, "png")    
