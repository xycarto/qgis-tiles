import './style.css';
import {Map, View} from 'ol';
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ.js';

const xyzUrl = "http://127.0.0.1:8081/world-webmer/v1/world-webmer/{z}/{x}/{y}.png"

const mono = new TileLayer({
  title: 'Monochrome',
  crossOrigin: 'anonymous',
  source: new XYZ({
    url: xyzUrl,
    wrapX: true,
  })
});

// Draw map
const map = new Map ({
  layers: [mono],
  target: 'map',
  view: new View({
    center: [0,0],
    zoom: 0,
  })
});
