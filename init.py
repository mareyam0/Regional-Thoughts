import psycopg2   
from psycopg2 import Error
import geopandas as gpd
import numpy as np
import pandas as pd

from textblob import TextBlob
import yake
from tqdm import tqdm
tqdm.pandas()

from sqlalchemy import create_engine

## Set your DB params here
table_name = "geo_tweets"
database = "gps"
user = "postgres"
password = "postgres"
port = str(5432)
host = "localhost"

## Init model for keyword extraction
language = "en"
max_ngram_size = 3
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 20

kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)

## Init DB Conenction
engine = create_engine("postgresql://"+user+":"+password+"@"+host+":"+port+"/"+database)

## Read data file
tweets = pd.read_csv('data/tweets_50k.csv')

## Cleaning
tweets.drop(columns=["geo.type","coordinates.type", "coordinates.coordinates"],inplace=True)

#Separate coordinates // then we wil drop geo.bbox
tweets["geo.bbox"]=tweets["geo.bbox"].astype(str)
tweets["lambda1"]=tweets["geo.bbox"].str.split(",").str[0]
tweets["lambda1"]=tweets["lambda1"].str.replace("[", " ")
tweets["phi1"]=tweets["geo.bbox"].str.split(",").str[1]
tweets["lambda2"]=tweets["geo.bbox"].str.split(",").str[2]
tweets["phi2"]=tweets["geo.bbox"].str.split(",").str[3]
tweets["phi2"]=tweets["phi2"].str.replace("]", " ")
tweets.drop(columns=["geo.bbox"],inplace=True)

#let's create another 2 columns with the mean of each of phi and lambda // then we will drop the last 4 columns 
tweets["phi"]=(tweets["phi1"].astype(float)+tweets["phi2"].astype(float))/2
tweets["Lambda"]=(tweets["lambda1"].astype(float)+tweets["lambda2"].astype(float))/2
tweets.drop(columns=["lambda1", "phi1", "lambda2", "phi2"],inplace=True)

g_tweets=gpd.GeoDataFrame(tweets, geometry= gpd.points_from_xy(tweets.Lambda, tweets.phi))
g_tweets.drop(columns=["Lambda", "phi", "place_id"],inplace=True)

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
        return ""

g_tweets['keywords'] = g_tweets['text'].progress_apply(getKeyword)
g_tweets['analysis'] = g_tweets['text'].apply(getSentiment)

## Set CRS
g_tweets.set_crs(epsg=3857, inplace=True, allow_override=True)

## Create table in postgis and insert data
gpd.GeoDataFrame.to_postgis(g_tweets, name = table_name, con = engine, schema = 'public', if_exists = 'replace')

c = engine.execute("CREATE INDEX idx_hour ON geo_tweets(hour);")
c.close()
print("DB Setup Completed!")
