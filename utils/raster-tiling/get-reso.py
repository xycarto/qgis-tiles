import math
import os
import sys

# python3 utils/raster-tiling/get-reso.py 32000000

import math
from pyproj import CRS, Transformer

# Script to calculate base scale for NZTM tiling scheme.  Extent for this
# calculation is taken from https://www.linz.govt.nz/data/linz-data-service/guides-and-documentation/nztm2000-map-tile-service-schema
# This script can be modified to determine the base scale of other projections
# It is a work in progress.  
# Note: tis does not yet factor in non-standard zoom scaling, e.g. scaling that is only a factor of 2
# Note: PPI has been modified from the NZTM stanrd and now uses 96
#
# TODO:
#  1. Determine method to work out all scales (will be loop of zoom levels)
#  2. Test with other known projections

inCRS = CRS(2193)
wgsCRS = CRS(4326)
PPI = 90.71428571428571 # Pixels per Inch
TILE_SIZE = [256, 256]
ZOOM_LEVEL = 0
MPU = 0.0254 # Meter per Unit
MPP = 0.00028 # Meters per Pixel

# From NZTM Standard here:
# https://www.linz.govt.nz/data/linz-data-service/guides-and-documentation/nztm2000-map-tile-service-schema
minx = 274000
maxx = 3327000
miny = 3087000
maxy = 7173000

# Pyproj format is: (minx, miny, maxx, maxy)
nztm_bounds = (minx, miny, maxx, maxy)

# Get bounds in WGS84
transformer = Transformer.from_crs(inCRS, wgsCRS, always_xy=True)
wgs_bounds = transformer.transform_bounds(*nztm_bounds)
wgs_minx = wgs_bounds[0]
wgs_maxx = wgs_bounds[2]
wgs_miny = wgs_bounds[1]
wgs_maxy = wgs_bounds[3]

# Center point in degrees
center_point = ((abs(wgs_maxy) + abs(wgs_miny))/2)
print(center_point)

# Calulate scheme for NZTM: https://epsg.io/2193
# Based on GRS 80 Ellipoide
# Flattening based on ellipsoid and derived from: 
# https://www.linz.govt.nz/data/geodetic-system/datums-projections-and-heights/geodetic-datums/reference-ellipsoids
flattening = 298.257
f = 1/flattening
e2 = (2-f)*f

# Scale Factor for true distance.  For now, estimated at 41 degrees (about center of NZ)
# The proper formula for local scale factor in ellipsoid Mercator (with true scale at equator)
# is:
#
# k = sqrt( 1 - e^2 * sin^2(phi)) / cos(phi)
#
# where e^2 is the squared eccentricity of the ellipsoid. 
# (Source: John P. Snyder, Map Projections: A Working Manual, 
# #page 44, see http://pubs.er.usgs.gov/usgspubs/pp/pp1395 ) 
# That is, e^2 = (2-f)*f, where f is the flattening. 
deg = math.radians(40.9006)
scale_factor = math.sqrt( 1 - e2 * math.sin(deg)**2)**0.5 / math.cos(deg)

# Calulate Scale X
base_width = abs((maxx) - (minx)) * 0.9996
print(base_width)
base_scale_x = round(
    ((base_width/scale_factor) * PPI) / ((TILE_SIZE[0] * 2**ZOOM_LEVEL) * MPU)
    )
# Calculate Reso X
base_reso_x = base_scale_x * MPP
print(base_scale_x)
print(base_reso_x)

# # Calulate Scale Y
# base_height = abs(abs(maxy) - abs(miny))
# base_scale_y = round(
#     (math.cos(deg) * (base_width) * PPI) / ((TILE_SIZE[1] * 2**ZOOM_LEVEL) * MPU)
#     )
# # Calculate Reso Y
# base_reso_y = base_scale_y * MPP
# print(base_scale_y)
# print(base_reso_y)

