## Import Libraries

from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
import glob, rasterio
import numpy as np
import json, os, gc
from functools import partial
import pyproj
from shapely.ops import transform
import geopandas as gpd
from shapely.geometry import Point
from psycopg2 import Error
import geopandas as gpd
import pandas as pd
import shapely, overpass, geojson, psycopg2
import tweepy
import configparser
from textblob import TextBlob
import yake
from sqlalchemy import create_engine
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from tqdm import tqdm
from PIL import Image
tqdm.pandas()

### -------------- INIT SECTION ------------------ ###

## DB Params
database = "gps"
user = "postgres"
password = "postgres"
host = "localhost"
port = str(5432)
table_name = "geo_tweets"

## Keyword extraction model init
language = "en"
max_ngram_size = 3
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 20

kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)

## Base functions

def getSentiment(text):

    score = TextBlob(text).sentiment.polarity
    
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

def getKeyword(text):
    try:
        return kw_extractor.extract_keywords(text.lower())[0][0]
    except:
        return None

def getGroup(hour):
    
    if hour >= 8 and hour <= 12:
        return "Morning"
    elif hour >= 13 and hour <= 16:
        return "Afternoon"
    elif hour >= 17 and hour <= 20:
        return "Evening"
    elif hour >= 21 and hour <= 24:
        return "Night"
    else:
        return "Late Night"

## Initialise All APIs

## Postgres connection via sqlalchemy
engine = create_engine("postgresql://"+user+":"+password+"@"+host+":"+port+"/"+database)

# OSM API
osm_api = overpass.API(timeout=500)

# Tweepy API
config = configparser.ConfigParser()
config.read('./config.ini')

api_key=config['twitter']['api_key']
api_key_secret= config['twitter']['api_key_secret']

access_token= config['twitter']['access_token']
access_token_secret= config['twitter']['access_token_secret']

auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

tweepy_api = tweepy.API(auth)

# Postgres Connection
connection = psycopg2.connect(database = database, user = user, password = password, host = host, port = port)
cursor = connection.cursor()

# FLASK APP
app = Flask(__name__)

### -------------- INIT SECTION ------------------ ###

# Index Route
@app.route('/')
def index():

    '''
    Returns twitter.html with DB Count by States
    '''

    base_usa = gpd.read_file('./static/geojson/chloro.geojson')

    query = "SELECT author_id, geometry FROM "+table_name
    tweets = gpd.GeoDataFrame.from_postgis(query, connection, geom_col="geometry")
    
    tweets.set_crs(epsg=4326, inplace=True, allow_override=True)

    usa_sentiment = base_usa.sjoin(tweets, how="right")
    usa_sentiment = usa_sentiment.groupby('name')['author_id'].agg(['count']).reset_index()
    base_usa['density'] = usa_sentiment['count']

    base_usa = base_usa.drop(['id','geometry'], axis=1)
    base_usa.columns = ['State','Tweet Count']
    
    return render_template('twitter.html', data=base_usa.to_html(classes="table", index=False, justify="center",table_id="results"), count=base_usa['Tweet Count'].sum())

# OSM Query Route
@app.route('/osm', methods=['POST'])
def osm():

    '''
    Saves road vectors into roads.geojson
    '''

    try:
        aoi = request.json['coords']['value']
        aoi_str = "("+str(aoi[1])+","+str(aoi[0])+","+str(aoi[3])+","+str(aoi[2])+")"

        res = osm_api.get("""
            way["highway"]"""+aoi_str+""";
            """, verbosity='geom')

        with open("static/geojson/roads.geojson",mode="w") as f:
            geojson.dump(res,f)

        roads = gpd.read_file('./static/geojson/roads.geojson')
        roads['geometry'] = roads.geometry.buffer(0.000035)

        tweets = gpd.read_file('./static/geojson/tweets.geojson')
        tweets['geometry'] = tweets['geometry'].buffer(0.000035)

        intersection = tweets.sjoin(roads, how="inner").shape[0]

        ## Tweet Count
        tweet_count = tweets.shape[0]
        off_road = tweet_count - intersection

        return jsonify({
            "tweet_count": [off_road, intersection]
        })
    except:
        return "0"

# Tweets Query Route
@app.route('/tweets', methods=['POST'])
def tweets():

    '''
    Queries Postgres DB by Polygon and saves tweets to tweets.geojson
    '''
    try:
        aoi = request.json['geojson']['value']

        with open("static/geojson/aoi.geojson",mode="w") as f:
            geojson.dump(aoi,f)

        aoi_bbox = aoi['features'][0]['geometry']
        footprint = shapely.wkt.dumps(shapely.geometry.shape(aoi_bbox))
        
        ## DB Query
        query = "SELECT * FROM "+table_name+" WHERE ST_WITHIN(geometry, st_setsrid(ST_GEOMFROMTEXT('{}'), 3857))".format(footprint)
        tweets = gpd.GeoDataFrame.from_postgis(query, connection, geom_col="geometry")
        
        if tweets.shape[0] == 0:
            return "0"
        
        ## To change location of overlapping tweet points to show better distribution (within the selected bbox)
        tweets.set_crs(epsg=4326, inplace=True, allow_override=True)
        total_bounds_aoi = gpd.read_file('./static/geojson/aoi.geojson').total_bounds

        x_min, y_min, x_max, y_max = total_bounds_aoi
        n = tweets.shape[0]

        x = np.random.uniform(x_min, x_max, n)
        y = np.random.uniform(y_min, y_max, n)
        gdf_points = gpd.GeoSeries(gpd.points_from_xy(x, y))

        tweets['geometry'] = gdf_points

        ## CRS changed to match OSM CRS
        tweets.to_file("static/geojson/tweets.geojson", driver="GeoJSON")
        
        return "1"
    except:
        return "0"

# Stats route for polygon results
@app.route('/statistics', methods=['POST'])
def statistics():

    '''
        Return the following for any polygon

        1. Word cloud
        2. State names
        3. Area in sqkm
        4. Device Usage
        5. Sentiment overtime
    '''

    try:

        tweets = gpd.read_file('./static/geojson/tweets.geojson')
        tweets['geometry'] = tweets['geometry'].buffer(0.000035)

        ## Word Cloud
        try:
            allKeyWords = ' '.join([words for words in tweets['keywords'] if words != None])
            
            twitter_mask = np.array(Image.open("./static/images/twitter_mask.png"))
            WordCloud(stopwords=STOPWORDS,max_words=100, background_color='white',width=500,height=500,mask=twitter_mask,contour_width=5, contour_color='skyblue').generate(allKeyWords).to_file('./static/images/wordcloud.png')

            # WordCloud(width = 500, height=300, random_state=21, max_font_size=119).generate(allKeyWords).to_file('./static/images/wordcloud.png')
            wc_result = 1
        except:
            wc_result = 0

        ## State Name
        usa_intersection = gpd.read_file('./static/geojson/chloro.geojson').sjoin(tweets, how="inner")
        states = list(np.unique(usa_intersection['name']))
        states = " | ".join(states)

        ## Area
        with open('./static/geojson/aoi.geojson') as fp:
            aoi = geojson.load(fp)['features'][0]['geometry']

        footprint = shapely.geometry.shape(aoi)

        wgs84 = pyproj.CRS('EPSG:4326')
        utm = pyproj.CRS('EPSG:3857')
        project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform

        area_sqkm = np.round(transform(project, footprint).area/1000000)

        ## Sentiment By Time
        tweets['sentiment_group'] = tweets['hour'].apply(getGroup)
        sentiment_values = tweets.groupby(['sentiment_group','analysis'])['analysis'].agg(['count']).reset_index()
        sentiment_values = sentiment_values[sentiment_values['analysis']=='Positive']
        sentiment_values['count'] = np.round(sentiment_values['count']/sentiment_values['count'].max(), 2)
        
        labels = list(sentiment_values['sentiment_group'])
        values = list(sentiment_values['count'])

        ## Devices Info
        tweet_devices = pd.DataFrame(tweets['source'].value_counts().reset_index().loc[:1])
        tweet_devices['source'] = np.round((tweet_devices['source']/tweets.shape[0])*100)
        tweet_devices.columns = ['Device','% Usage']
        
        return jsonify({
            "word_cloud": wc_result,
            "state": states,
            "area": str(area_sqkm)+" sqkm",
            "sentiment_overday": [labels, values],
            "tweet_count": str(tweets.shape[0]) + " Tweets",
            "tweet_devices": tweet_devices.to_html(classes="table result_tweet_devices", index=False, justify="center",table_id="results")
        })
    except:
        return "0"

# Sentiment for entire USA
@app.route('/sentiment', methods=['POST'])
def sentiment():

    '''
        Return sentiment of all US states for a specific time duration
    '''

    try:
        
        time = request.json['time']['value'].split("_")
        start_time = time[0]
        end_time = time[1]
        
        if len(start_time) > 0:
            
            base_usa = gpd.read_file('./static/geojson/chloro.geojson')

            query = "SELECT geometry, analysis FROM "+table_name+" WHERE hour BETWEEN {} AND {}".format(start_time, end_time)
            tweets = gpd.GeoDataFrame.from_postgis(query, connection, geom_col="geometry")
            
            usa_sentiment = base_usa.sjoin(tweets, how="left")
            usa_sentiment = usa_sentiment.groupby('name')['analysis'].agg(['count']).reset_index()
            base_usa['density'] = usa_sentiment['count']
            base_usa['density'] = base_usa['density'] / base_usa['density'].max()

            base_usa.to_file("static/geojson/sentiment.geojson", driver="GeoJSON")

            return "1"

        else:
            return "0"

    except:
        return "0"

# ETL route for fetching new tweets, transforming and storing in Postgres
@app.route('/etl', methods=['POST'])
def etl():

    '''
        Saves new transformed tweets into DB
    '''

    try:

        places = tweepy_api.search_geo(query="USA", granularity="country")
        place_id = places[0].id
        tweets = tweepy_api.search_tweets(q="place:%s" % place_id, count=10, result_type='mixed')
        
        #Creating a data frame with tweets
        df= pd.DataFrame([tweet.user.id for tweet in tweets], columns=['author_id'])
        df['text']=[tweet.text for tweet in tweets]
        df['source']=[tweet.source for tweet in tweets]
        df['created_at']=[tweet.user.created_at for tweet in tweets]
        df['place_id']=[tweet.place.id for tweet in tweets]
        df['full_name']=[tweet.place.full_name for tweet in tweets]
        df['geo.bbox']=[tweet.place.bounding_box.coordinates for tweet in tweets]
        
        #cleaning data
        df["geo.bbox"]=df["geo.bbox"].astype(str)
        df["geo.bbox"]=df["geo.bbox"].str.replace("[", " ")
        df["geo.bbox"]=df["geo.bbox"].str.replace("]", " ")

        df["point1"]=df["geo.bbox"].str.split(" , ").str[0]
        df["point2"]=df["geo.bbox"].str.split(" , ").str[1]
        df["point3"]=df["geo.bbox"].str.split(" , ").str[2]
        df["point4"]=df["geo.bbox"].str.split(" , ").str[3]

        df["lambda1"]=df["point1"].str.split(",").str[0]
        df["phi1"]=df["point1"].str.split(",").str[1]
        df["lambda2"]=df["point3"].str.split(",").str[0]
        df["phi2"]=df["point3"].str.split(",").str[1]

        df["phi"]=(df["phi1"].astype(float)+df["phi2"].astype(float))/2
        df["Lambda"]=(df["lambda1"].astype(float)+df["lambda2"].astype(float))/2

        df['created_at'] = df['created_at'].astype(str)
        df[['date','timestamp']] = df['created_at'].str.split(' ', expand=True)
        df[['time','misc']] = df['timestamp'].str.split('+', expand=True)
        df[['hour','m','s']] = df['time'].str.split(':', expand=True)

        df.drop(columns=["timestamp","time","misc","s","m","geo.bbox","point2","point4","point1","point3","lambda1", "phi1", "lambda2", "phi2"],inplace=True)
        
        df['keywords'] = df['text'].progress_apply(getKeyword)
        df['analysis'] = df['text'].progress_apply(getSentiment)

        #creating the geodataframe
        g_tweets = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.Lambda, df.phi))
        g_tweets = g_tweets[['text', 'author_id', 'source', 'created_at', 'full_name', 'date', 'hour', 'geometry', 'keywords', 'analysis']]

        g_tweets.set_crs(epsg=3857, inplace=True, allow_override=True)

        gpd.options.use_pygeos = True
        gpd.GeoDataFrame.to_postgis(g_tweets, name = table_name, con = engine, schema = 'public', if_exists = 'append')

        total_rows_query = engine.execute("SELECT COUNT(geometry) FROM "+table_name+";")
        total_rows = total_rows_query.fetchall()[0][0]
        total_rows_query.close()

        print(total_rows)
        return str(total_rows)

    except:
        return "0"

# Route to show pos/neu/neg tweets at a time
@app.route('/positive_negative_tweets', methods=['POST'])
def positive_negative_tweets():
    try:
        
        sentiment = request.json['sentiment_type']['value']
        
        query = "SELECT geometry, analysis FROM "+table_name+" WHERE analysis='{}'".format(sentiment)
        tweets = gpd.GeoDataFrame.from_postgis(query, connection, geom_col="geometry")
        tweets = tweets.sample(100)
        tweets.to_file("static/geojson/sentiment_marker.geojson", driver="GeoJSON")

        return "1"

    except:
        return "0"


if __name__ == '__main__':
    
      ## Define what IP/Port to host the app on
      app.run(host='0.0.0.0', port=5000)
 