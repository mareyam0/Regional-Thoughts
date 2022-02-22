<h1 align="center"><b>Regional-Thoughts</b></h1>


<p align="center">
<img width="300" alt="RegionalThoughts_Wordcloud" src="https://user-images.githubusercontent.com/99036510/155221764-59abc221-d588-4ceb-820b-0ce8e20b93a1.png">
</p>



Twitter is an online news and social networking site where people communicate in short messages called tweets. The data provided by Twitter, and the insights we're able to glean from them, can be truly world-changing, in more ways than most people realize.
Considering the importance of tweets in daily life and the amount of data they provide, it would be interesting to develop a solution that can provide some knowledge about ***regional thoughts***.

For this purpose, we chose to create this solution that allows to users, based on geo-tagged tweets, to have an idea about the most discussed subjects in any area (in this example, we focused on USA as study area, considering that most tweets are in english), the polarity of tweets, tweets shared in a specific time and other information.

<!-- CONTENTS -->
<h2 id = "contents">Contents</h2>

<details open = "open">
  <summary>Contents</summary>
  <ol>
    <li><a href = "#methodology">Methodology</a></li>
    <li><a href = "#steps">How can I run this solution ?</a></li>
    <li><a href = "#Authors">Authors</a></li>
  </ol>
</details>

<h2 id = "methodology">1. Methodology</h2>


1. Firstly, to get the geo-tagged tweets, the user need some keys provided by twitter (see "config.ini" file);
2. We used twitter API to get the tweets we need ("twitter_api.py" file);
3. we proceeded by cleaning the data (organised in a DataFrame) and convert it to a GeoDataFrame (with the geometry column);
4. we used "KeyBert" as a library for Natural Language Processing in Python to extract keywords from tweets;
5. we proceeded then by a sentimental analysis: we calculated the subjectivity and the polarity of tweets using "textblob library"






<h2 id = "steps">2. How can I run this solution ?</h2>






<h2 id = "Authors">3. Authors</h2>
<b>Jaskaran Singh PURI</b><br>
Master's degree in Geospatial Technologies at <a href ="https://www.novaims.unl.pt/" target = "_blank">NOVA University of Lisbon</a>, <a href ="https://www.uni-muenster.de/en/" target = "_blank">WWU Münster</a> and <a href ="https://www.uji.es/" target = "_blank">UJI</a><br>
</p>
<b>Mareyam Belcaid</b><br>
Master's degree in Geospatial Technologies at <a href ="https://www.novaims.unl.pt/" target = "_blank">NOVA University of Lisbon</a>, <a href ="https://www.uni-muenster.de/en/" target = "_blank">WWU Münster</a> and <a href ="https://www.uji.es/" target = "_blank">UJI</a><br>
</p>
<b>Maryeme Akhatar</b><br>
Master's degree in Geospatial Technologies at <a href ="https://www.novaims.unl.pt/" target = "_blank">NOVA University of Lisbon</a>, <a href ="https://www.uni-muenster.de/en/" target = "_blank">WWU Münster</a> and <a href ="https://www.uji.es/" target = "_blank">UJI</a><br>
</p>


