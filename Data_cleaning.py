import json
import pandas as pd
from pandas import json_normalize
import os
import numpy as np
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
from shapely.geometry import Point 
###
import tweepy
import configparser
import re
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')



#Read file
tweets = pd.read_json('./twitter_data_2022-02-05T13_15_30.json', lines=True)
tweets = pd.concat([tweets, json_normalize(tweets['geo'])], axis=1).drop(['geo'], axis=1)
pd.set_option('display.max_colwidth', None)

#Delete non functional columns
tweets.drop(columns=["id", "author", "country_code", "geo.type", "country", "coordinates.type", "coordinates.coordinates", "name"],inplace=True)


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


#Convert the DF to Geo DF of geotegged tweets
g_tweets=gpd.GeoDataFrame(test, geometry= gpd.points_from_xy(test.Lambda, test.phi))
#We should drop some no needed columns 
g_tweets.drop(columns=["Lambda", "phi", "id", "place_id"],inplace=True)

#just for safety
g_tweets.to_csv('geo_tweets.shp')
g_tweets.to_csv('geo_tweets.csv')


