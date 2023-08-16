import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gp
from shapely.geometry import Polygon

# python3 utils/webmer-data/webmer-extent.py

minx = -20037508.3427892
miny = -20037508.3427892
maxx = 20037508.3427892
maxy = 20037508.3427892

poly = Polygon([[minx, miny],
                [maxx, miny],
                [maxx, maxy],
                [minx, maxy],
                [minx, miny]])

gp.GeoDataFrame(geometry=[poly], crs=3857).to_file("qgis/qgis-data/vector/web-mercator/webmercator-extent.gpkg", driver="GPKG")