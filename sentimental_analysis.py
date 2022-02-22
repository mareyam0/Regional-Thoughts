import tweepy
import configparser
import pandas as pd
import numpy as np
import re
from textblob import TextBlob
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.image as mpimg
import imageio

#create function to get the subjectivity
def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

#create a function to get the polarity
def getPolarity(text):
    return TextBlob(text).sentiment.polarity

#Create two new columns
g_tweets['Subjectivity'] = g_tweets['Tweets'].apply(getSubjectivity)
g_tweets['Polarity'] = g_tweets['Tweets'].apply(getPolarity)

#plot the word Cloud
allWords = ' '.join([twts for twts in g_tweets['Tweets']])


#from google.colab import files
twitter_mask = np.array(Image.open("twitter_mask.png"))

wordcloud = WordCloud(stopwords=STOPWORDS,max_words=1000, background_color='white',width=1800,height=1400,mask=twitter_mask,contour_width=5, contour_color='skyblue').generate(allWords)

plt.imshow(wordcloud)
plt.axis("off")
#plt.savefig('./my_twitter_wordcloud_2.png', dpi=300)
plt.show()



#Create a function to compute the negative, neutral and positive analysis
def getAnalysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

g_tweets['Analysis'] = g_tweets['Polarity'].apply(getAnalysis)


#print all of the positive tweets
j=1
sortedtweets=g_tweets.sort_values(by=['Polarity'])
for i in range(0, sortedtweets.shape[0]):
    if (sortedtweets['Analysis'][i] == 'Positive'): 
        #we can add the condition of location
        print(str(j)+ ') '+sortedtweets['Tweets'][i])
        print()
        j=j+1
    

#print the negative tweets
j=1
sortedtweets=g_tweets.sort_values(by=['Polarity'], ascending='False')
for i in range(0, sortedtweets.shape[0]):
    if (sortedtweets['Analysis'][i] == 'Negative'): 
        #we can add the condition of location
        print(str(j)+ ') '+sortedtweets['Tweets'][i])
        print()
        j=j+1


#Plot the polarity and subjectivity
plt.figure(figsize=(8,6))
for i in range(0, g_tweets.shape[0]):
    plt.scatter(g_tweets['Polarity'][i], g_tweets['Subjectivity'][i], color='Blue')

plt.title('Sentiment Analysis')
plt.xlabel('Polarity')
plt.ylabel('Subjectivity')


#percentage of the positive tweets
ptweets= g_tweets[g_tweets.Analysis == 'Positive']
ptweets = ptweets['Tweets']

round((ptweets.shape[0]/ g_tweets.shape[0])*100,1)

#percentage of negative tweets
ntweets= g_tweets[g_tweets.Analysis == 'Negative']
ntweets = ntweets['Tweets']
round((ntweets.shape[0]/ g_tweets.shape[0])*100,1)

#value counts
g_tweets['Analysis'].value_counts()

#plot anad visualize the counts
plt.title('Sentiment Analysis')
plt.ylabel('Counts')
plt.xlabel('Sentiment')
g_tweets['Analysis'].value_counts().plot(kind='bar')



