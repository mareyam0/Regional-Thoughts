from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import glob, rasterio
import numpy as np
import json, os, gc

import geopandas as gpd
from shapely.geometry import Point

import overpass
import geojson

api = overpass.API(timeout=500)
app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('twitter.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        aoi = request.json['coords']['value']
        # footprint = geojson_to_wkt(aoi)
        aoi_str = "("+str(aoi[1])+","+str(aoi[0])+","+str(aoi[3])+","+str(aoi[2])+")"
        print(aoi_str)

        res = api.get("""
            way["highway"]"""+aoi_str+""";
            """, verbosity='geom')

        with open("static/geojson/roads.geojson",mode="w") as f:
            geojson.dump(res,f)

        df = gpd.read_file('static/geojson/roads.geojson')
        df['geometry'] = df.geometry.buffer(0.0008)
        
        print(df.head())
        
        return "1"
    except:
        return "0"

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000)
 