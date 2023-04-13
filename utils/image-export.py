from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

import os
import math
from osgeo import gdal
import geopandas as gp
import sys
import os
from multiprocessing import Pool

# make tiler
# python3 utils/image-export.py "qgis/full-nz-mono.qgz" 32000000 4


def rend(index, gtile):        
    # Set Paths
    raw_path = os.path.join(OUT_BASE, str(index))
    os.makedirs(raw_path, exist_ok=True)
    
    # Get bounds for processing
    xmin = gtile.geometry.bounds[0]
    ymin = gtile.geometry.bounds[1]
    xmax = gtile.geometry.bounds[2]
    ymax = gtile.geometry.bounds[3]
    
    width = math.ceil(
    abs(
        (((xmin - xmax) * METRE_TO_INCH) / float(scale))
        * DPI
    )
    )
    height = math.ceil(
        abs(
            (((ymin - ymax) * METRE_TO_INCH) / float(scale))
            * DPI
        )
    )
    
    file_name = str(scale) + "_images.png"
    image_path = os.path.join(raw_path, file_name)
    print(image_path)
    
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
    settings.setExtent(QgsRectangle(xmin, ymin, xmax, ymax))
    
    # setup qgis map renderer
    print("Rendering...")
    render = QgsMapRendererCustomPainterJob(settings, p)
    render.start()
    render.waitForFinished()
    p.end()

    # save the image
    print("Saving Image...")
    img.save(image_path, "png")

    gtif_file_name = str(scale) + "_gtiff_images.tif"
    gtif_path = os.path.join(raw_path, gtif_file_name)
    
    print("Running Translate...")
    creation_options = [
        "TILED=YES",
        "COMPRESS=LZW",
        "BIGTIFF=YES"
    ]
    gdal.Translate(
        gtif_path, 
        image_path, 
        outputBounds=[xmin, ymax, xmax, ymin], 
        bandList=[1,2,3], 
        outputSRS="EPSG:2193",            
        creationOptions = creation_options,
        callback = gdal.TermProgress_nocb 
    )
    
    os.remove(image_path)

def main(gpGrid):
    print("Rendering QGIS")
    with Pool(4) as pool:
        # prepare arguments
        items = [(index, gtile) for index, gtile in gpGrid.iterrows()]
        # issue tasks to the process pool and wait for tasks to complete
        pool.starmap(rend, items)

if __name__ == "__main__":
    project_path = sys.argv[1]
    scale = sys.argv[2]

    PROCESSORS = sys.argv[3]

    GRID = "qgis/qgis-data/grids/100k_grid.gpkg"
    OUT_DIR = "tiles"

    DIR_NAME = os.path.basename(project_path).split(".")[0]
    OUT_BASE = os.path.join(OUT_DIR, "qgis-grids", DIR_NAME)
    os.makedirs(OUT_BASE, exist_ok=True)

    # Resolutions and scales set per LINZ map tiles standards:
    # https://www.linz.govt.nz/data/linz-data-service/guides-and-documentation/nztm2000-map-tile-service-schema
    METRE_TO_INCH = 39.3701
    DPI = 90.71428571428571
    # Supply path to qgis install location
    # Create a reference to the QgsApplication.  Setting the
    # second argument to False disables the GUI.
    print("Setting QGIS paths")
    qgs = QgsApplication([], False)
    QgsApplication.setPrefixPath("/usr", True)
    QgsApplication.setThemeName("default")
    app = QgsApplication([], False, ".local/share/QGIS/QGIS3/profiles/default")
    app.initQgis()
    authMgr = app.authManager()

    project = QgsProject.instance()

    project.read(project_path)

    layers = QgsProject.instance().mapLayers().values()

    # Project Extent
    proj_extent = project.mapLayersByName("nz-extent")[0].extent()

    # Scales
    gpGrid = gp.read_file(GRID) 
    main(gpGrid)



        
    
