import tweepy
import configparser
import pandas as pd

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

places = api.search_geo(query="USA", granularity="country")
place_id = places[0].id
tweets = api.search_tweets(q="place:%s" % place_id)
#for tweet in tweets:
    #print tweet.text + " | " + tweet.place.name if tweet.place else "Undefined place"

tweets= pd.DataFrame(tweets)
tweets.to_csv('tweets_test.csv')


##### need to be completed!!!!!!!!!!