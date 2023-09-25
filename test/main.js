import './style.css';
import {Map, View} from 'ol';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import proj4 from 'proj4';
import {register} from 'ol/proj/proj4';
import {get as getProjection} from 'ol/proj';
import {fromLonLat} from 'ol/proj';
import XYZ from 'ol/source/XYZ.js';
import TileGrid from 'ol/tilegrid/TileGrid.js';

const MAXZOOM = 9

// set NZTM projection
proj4.defs("EPSG:2193","+proj=tmerc +lat_0=0 +lon_0=173 +k=0.9996 +x_0=1600000 +y_0=10000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs");
register(proj4);
const nztmProjection = getProjection('EPSG:2193');
var origin = [ -1000000, 10000000];
var resolutions = [ 8960, 4480, 2240, 1120, 560, 280, 140, 70, 28 ];
const matrixIds = [0, 1, 2];

const xyzUrl = "http://localhost:8081/full-nz-mono/v1/full-nz-mono/{z}/{x}/{y}.png"

const mono = new TileLayer({
  title: 'Monochrome',
  crossOrigin: 'anonymous',
  source: new XYZ({
    url: xyzUrl,
    projection: nztmProjection,
    tileGrid: new TileGrid({
      origin: origin,
      resolutions: resolutions,
      tileSize: [256, 256],
    })
  })
});

// Draw map
const map = new Map ({
  layers: [mono],
  target: 'map',
  pixelRatio: 2,
  view: new View({
    projection: nztmProjection,
    center: fromLonLat([177.0,-39.5], nztmProjection),
    zoom: 0,
    minResolution: 28,
    maxResolution: 8960,
    constrainResolution: true,
    enableRotation: false,
  })
});
