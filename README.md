<h1 align="center"><b>Regional-Thoughts</b></h1>


<p align="center">
<img width="300" alt="RegionalThoughts_Wordcloud" src="https://user-images.githubusercontent.com/99036510/155221764-59abc221-d588-4ceb-820b-0ce8e20b93a1.png">
</p>

<p>
    <a href="https://github.com/mareyam0/Regional-Thoughts/commits/master">
        <img alt="Last commit" src="https://img.shields.io/github/last-commit/deepset-ai/haystack">
    </a>
</p>

Twitter is an online news and social networking site where people communicate in short messages called tweets. The data provided by Twitter, and the insights we're able to glean from them, can be truly world-changing, in more ways than most people realize.
Considering the importance of tweets in daily life and the amount of data they provide, it would be interesting to develop a solution that can provide some knowledge about ***regional thoughts***.

For this purpose, we chose to create this solution that allows to users, based on geo-tagged tweets, to have an idea about the most discussed subjects in any area (in this example, we focused on USA as study area, considering that most tweets are in english), the polarity of tweets, tweets shared in a specific time and other information.

<p align="center">
<img alt="Product Page" src="https://github.com/mareyam0/Regional-Thoughts/blob/main/static/images/product.PNG">
</p>

## :mortar_board: Features

<ul>
  <li>Get Following Statistics For ```Polygon```
  <ul>
    <li> State Name | Total Tweets | Area of bbox
    <li> Tweets intersection OSM Roads
    <li> Wordcloud
    <li> Sentiment over time
    <li> Device Usage
  </ul>
  <li>Sentiment For 5 Time Durations For USA
  <li>Sample Location of Positive/Negative/Neutral Tweets
</ul>

<!-- CONTENTS -->
<h2 id = "contents">Contents</h2>

<details open = "open">
  <summary>Contents</summary>
  <ol>
    <li><a href = "#methodology">Methodology</a></li>
    <li><a href = "#pre">Prerequisites</a></li>
    <li><a href = "#tweet">Configure Tweetpy</a></li>
    <li><a href = "#db">Database</a></li>
    <li><a href = "#init">Installation</a></li>
    <li><a href = "#authors">Authors</a></li>
  </ol>
</details>

<h2 id = "methodology">Methodology</h2>

1. Firstly, to get the geo-tagged tweets, the user need some keys provided by twitter (see "config.ini" file);
2. We used twitter API to get the tweets we need ("twitter_api.py" file);
3. we proceeded by cleaning the data (organised in a DataFrame) and convert it to a GeoDataFrame (with the geometry column);
4. we used **"KeyBert/Yake"** as a library for Natural Language Processing in Python to extract keywords from tweets and store them in the column "keywords";
5. we proceeded then by a sentimental analysis: we calculated the subjectivity and the polarity of tweets using **"textblob"** library in python and according to the resulting values we filtred the tweets by "positive", "negative" and "neutral";
6. we did some analysis to understand the results
7. we have established a connection with a spatial database under **PostgreSQL**;
8. The next step was the **SQL** queries to extract keywords and polarity, calculate the number of people tweeting using each device (Android/Iphone) inside a polygon chosen by the user. the definition of the dominant polarity and the wordcloud were done using **python**;
9. Also using **SQL** we created queries that allow to select from the database the tweets based on time of sharing or their polarity;
10. The visualisation of the interactive map was done using HTML and Javascript.

The next Figure resume the steps behind the creation of this solution:

<p align="center"> 
<img width="500" alt="process" src="https://user-images.githubusercontent.com/99036510/155242766-f775f514-3bbb-4c84-87de-14d0447961de.png" >
</p>

<p align="center">Figure 1. Steps behind the creation of this solution</p>

<h2 id = "pre">Prerequisites</h2>
<ul>
<li>Postgres 14.1
<li>Python 3.10
</ul>

<h2 id = "tweet">API Configuration</h2>

Configure the following API Keys in ```config.ini``` for twitter connection using ```Tweepy```

```
[twitter]

api_key = 
api_key_secret = 

access_token = 
access_token_secret = 
```


<h2 id = "db">Database Setup</h2>

Following parameters can be configure in ```init.py``` and ```app.py```
```
database = "gps"
user = "postgres"
password = "postgres"
host = "localhost"
port = 5432
table_name = "geo_tweets"
```

## :floppy_disk: Installation

Setup Python Environment
```
git clone https://github.com/mareyam0/Regional-Thoughts
conda install -n py10 python=3.10
conda activate py10
pip3 install -r requirements.txt
```

Load Data
```
cd Regional-Thoughts
python init.py
```

Launch Application
```
set FLASK_APP=app.py (Windows)
export FLASK_APP=app.py (Linux)

flask run
```

View Web Page
```
http://localhost:5000
```

## :heart: Authors

<b>Jaskaran Singh PURI</b><br>
Master's degree in Geospatial Technologies at <a href ="https://www.novaims.unl.pt/" target = "_blank">NOVA University of Lisbon</a>, <a href ="https://www.uni-muenster.de/en/" target = "_blank">WWU Münster</a> and <a href ="https://www.uji.es/" target = "_blank">UJI</a><br>
</p>
<b>Mareyam Belcaid</b><br>
Master's degree in Geospatial Technologies at <a href ="https://www.novaims.unl.pt/" target = "_blank">NOVA University of Lisbon</a>, <a href ="https://www.uni-muenster.de/en/" target = "_blank">WWU Münster</a> and <a href ="https://www.uji.es/" target = "_blank">UJI</a><br>
</p>
<b>Maryeme Akhatar</b><br>
Master's degree in Geospatial Technologies at <a href ="https://www.novaims.unl.pt/" target = "_blank">NOVA University of Lisbon</a>, <a href ="https://www.uni-muenster.de/en/" target = "_blank">WWU Münster</a> and <a href ="https://www.uji.es/" target = "_blank">UJI</a><br>
</p>


