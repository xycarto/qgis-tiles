import os
from multiprocessing import Pool
import sys
import math
from shapely.geometry import box
from shapely.geometry import Polygon
os.environ['USE_PYGEOS'] = '0'
import geopandas as gp

from multiprocessing import Pool

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

# python3 utils/raster-tiler-test-grid.py "qgis/full-nz-mono.qgz"

def rend(index, row, scl):
    width = math.floor(
        abs(
            (((row.xmin - row.xmax) * METRE_TO_INCH) / float(scl['scaleDenominator']))
            * DPI
        )
        )
    height = math.floor(
        abs(
            (((row.ymin - row.ymax) * METRE_TO_INCH) / float(scl['scaleDenominator']))
            * DPI
        )
    )
    
    save_dir = os.path.join(zoom_dir, str(row.column))
    os.makedirs(save_dir, exist_ok=True)
    
    image_path = os.path.join(save_dir, f"{str(row.row)}.png")
    
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

project_path = sys.argv[1]

print("Setting QGIS paths")
qgs = QgsApplication([], False)
QgsApplication.setPrefixPath("/usr", True)
QgsApplication.setThemeName("default")
app = QgsApplication([], False, ".local/share/QGIS/QGIS3/profiles/default")
app.initQgis()
authMgr = app.authManager()

project = QgsProject.instance()

project.read(project_path)

# layers = project.mapLayers().values()

# Project Extent
project.mapLayersByName("nz-extent")[0].extent()

os.makedirs("data", exist_ok=True)
test_dir = os.path.join("tiles", "test")
os.makedirs(test_dir, exist_ok=True)

XMIN = 274000
YMIN = 3087000
XMAX = 3327000
YMAX = 7173000

matrix = [
    {
      "type": "TileMatrixType",
      "identifier": "0",
      "scaleDenominator": 32000000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 2,
      "matrixHeight": 4,
      "reso": 8960
    },
    {
      "type": "TileMatrixType",
      "identifier": "1",
      "scaleDenominator": 16000000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 4,
      "matrixHeight": 8,
      "reso": 4480
    },
    {
      "type": "TileMatrixType",
      "identifier": "2",
      "scaleDenominator": 8000000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 8,
      "matrixHeight": 16,
      "reso": 2240
    },
    {
      "type": "TileMatrixType",
      "identifier": "3",
      "scaleDenominator": 4000000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 16,
      "matrixHeight": 32,
      "reso": 1120
    },
    {
      "type": "TileMatrixType",
      "identifier": "4",
      "scaleDenominator": 2000000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 32,
      "matrixHeight": 64,
      "reso": 560
    },
    {
      "type": "TileMatrixType",
      "identifier": "5",
      "scaleDenominator": 1000000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 64,
      "matrixHeight": 128,
      "reso": 280
    },
    {
      "type": "TileMatrixType",
      "identifier": "6",
      "scaleDenominator": 500000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 128,
      "matrixHeight": 256,
      "reso": 140
    },
    {
      "type": "TileMatrixType",
      "identifier": "7",
      "scaleDenominator": 250000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 256,
      "matrixHeight": 512,
      "reso": 70
    },
    {
      "type": "TileMatrixType",
      "identifier": "8",
      "scaleDenominator": 100000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 640,
      "matrixHeight": 1280,
      "reso": 28
    },
    {
      "type": "TileMatrixType",
      "identifier": "9",
      "scaleDenominator": 50000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 1280,
      "matrixHeight": 2560,
      "reso": 14
    },
    {
      "type": "TileMatrixType",
      "identifier": "10",
      "scaleDenominator": 25000,
      "topLeftCorner": [10000000, -1000000],
      "tileWidth": 256,
      "tileHeight": 256,
      "matrixWidth": 2560,
      "matrixHeight": 5120,
      "reso": 7
    }              
    ]

METRE_TO_INCH = 39.3701
DPI = 90.71428571428571

print(matrix[0]['scaleDenominator'])

# Create Grid
geom =box(XMIN,YMIN,XMAX,YMAX)
# gp.GeoDataFrame(geometry=[geom], crs=2193).to_file("data/test_extent.gpkg", driver="GPKG")

for scl in matrix:
    # print(scl)
    print(scl['reso'])
    zoom = scl['identifier']
    zoom_dir = os.path.join("tiles", "test", str(zoom))
    os.makedirs(zoom_dir, exist_ok=True)
    cell_size = scl['reso']
    tile_span_x = scl['tileWidth'] * cell_size
    tile_span_y = scl['tileHeight'] * cell_size

    XleftOrigin = scl['topLeftCorner'][1]
    XrightOrigin = XleftOrigin + tile_span_x
    YtopOrigin = scl['topLeftCorner'][0]
    YbottomOrigin = YtopOrigin - tile_span_y
    polygons = []
    for i in range(scl['matrixWidth']):
        Ytop = YtopOrigin
        Ybottom = YbottomOrigin
        for j in range(scl['matrixHeight']):
            gridNum = [j,i]
            writeGeom = Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)])
            polygons.append(
                {
                'row': j,
                'column': i,
                'grid_num': str(gridNum),
                'xmin': XleftOrigin,
                'xmax': XrightOrigin,
                'ymin': Ybottom,
                'ymax': Ytop,
                'geometry': writeGeom
                }
            ) 
            Ytop = Ytop - tile_span_y
            Ybottom = Ybottom - tile_span_y
        XleftOrigin = XleftOrigin + tile_span_x
        XrightOrigin = XrightOrigin + tile_span_x
            
    print("Writing polygons")
    grid = gp.GeoDataFrame(polygons, crs=2193)
    grid.to_file(f"data/{str(scl['scaleDenominator'])}_grid_index.gpkg", driver="GPKG")

    
    print("Rendering QGIS")
    with Pool(12) as pool:
        # prepare arguments
        items = [(index, row, scl) for index, row in grid.iterrows()]
        # issue tasks to the process pool and wait for tasks to complete
        pool.starmap(rend, items)       
    
