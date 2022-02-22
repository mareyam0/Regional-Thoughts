import tweepy
import configparser
import pandas as pd
import geopandas as gpd

# read configs
config = configparser.ConfigParser()
config.read('config.ini')

api_key=config['twitter']['api_key']
api_key_secret= config['twitter']['api_key_secret']

access_token= config['twitter']['access_token']
access_token_secret= config['twitter']['access_token_secret']

#authentication
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

places = api.geo_search(query="USA", granularity="country")
place_id = places[0].id
tweets = api.search(q="place:%s" % place_id, count=200, result_type='recent') # count is for the number of tweets we need

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


#let's create another 2 columns with the mean of each of phi and lambda // then we will drop the last 4 columns 
df["phi"]=(df["phi1"].astype(float)+df["phi2"].astype(float))/2
df["Lambda"]=(df["lambda1"].astype(float)+df["lambda2"].astype(float))/2

#drop extra columns
df.drop(columns=["geo.bbox","point2","point4","point1","point3","lambda1", "phi1", "lambda2", "phi2"],inplace=True)


#creating the geodataframe
#g_tweets=geopandas.GeoDataFrame(columns=['author_id', 'text', 'source', 'created_at','place_id', 'full_name	', 'phi', 'Lambda', 'geometry' ], geometry='geometry')
g_tweets=g_tweets.append(gpd.GeoDataFrame(df1, geometry= gpd.points_from_xy(df1.Lambda, df1.phi)))

#verify if need to create an empty geodataframe first



