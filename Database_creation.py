#Database Creation
import psycopg2   
from psycopg2 import Error
from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import *


#We should connect to database 'Project' using sqlalchemy!!!
from sqlalchemy import create_engine
engine = create_engine("postgresql://postgres:postgres@localhost:5432/Project")  
g_tweets.to_postgis("geo_tweets", engine, if_exists='replace') 


# Create a cursor to perform database operations
cursor = connexion.cursor()
# Print PostgreSQL details
print("PostgreSQL server information")
print(connexion.get_dsn_parameters(), "\n")

# Executing a SQL query
cursor.execute("SELECT version();")
# Fetch result
record = cursor.fetchone()
print("You are connected to - ", record, "\n")


#Let's create a table in our DB called Project and name it geo_tweets
create_table_query = '''CREATE TABLE if not exists geo_tweets
(id int PRIMARY KEY ,
author_id int ,
source varchar(40) NOT NULL ,
created_at DATE ,
text TEXT NOT NULL ,
full_name varchar(40) NOT NULL ,
keywords varchar(40) NOT NULL,
geometry geometry(point, 3857)
);'''

cursor.execute(create_table_query)
connexion.commit()


#FROM THE GEODATAFRAME TO POSTGIS
GeoDataFrame.to_postgis(g_tweetsx, name='geo_tweets', con=engine, schema='public', if_exists='replace')

