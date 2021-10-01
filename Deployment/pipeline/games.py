#!/usr/bin/env python

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
from pyspark.sql.functions import rank, col
from google.cloud import storage
import datetime

date = datetime.date.today()
today = date.strftime("%Y/%m/%d")

if len(sys.argv) != 5:
  raise Exception("Exactly 4 arguments are required: <inputPath> <outputPath> <queryName> <bucket>")

inputPath=sys.argv[1]
outputPath=sys.argv[2]
queryName=sys.argv[3]
bucket=sys.argv[4]

sc = SparkSession.builder.appName("PysparkExample")\
.config("spark.sql.shuffle.partitions", "50")\
.config("spark.driver.maxResultSize","5g").getOrCreate()

#Creates a spark data frame called as raw_data.

#BRANDS#
brands = sc.read.option("header", "true").csv(f"{inputPath}consoles.csv")
brands.createOrReplaceTempView("brands")
#CONSOLES#
games = sc.read.option("header", "true").csv(f"{inputPath}result.csv")
games.createOrReplaceTempView("games")

client = storage.Client()
# https://console.cloud.google.com/storage/browser/[bucket-id]/
bucket = client.get_bucket(bucket)
# Then do other things...
blob = bucket.get_blob(queryName)

sqlQuery = blob.download_as_string()

query = sc.sql(sqlQuery.decode("utf-8"))

query.createOrReplaceTempView("query")

df10Best = query.orderBy(col('custom_score').desc()).limit(10)

df10Worst = query.where(query.userscore != 'tbd').orderBy(col('custom_score').asc()).limit(10)

windowBestPerConsole = Window.partitionBy(query['console']).orderBy(query['company'],query['custom_score'].desc())

dfBestPerConsole = query.select('*', rank().over(windowBestPerConsole).alias('rank'))\
  .filter(col('rank') <= 10)

windowWorstPerConsole = Window.partitionBy(query['console']).orderBy(query['company'],query['custom_score'].asc())

dfWorstPerConsole = query.where(query.userscore != 'tbd').select('*', rank().over(windowWorstPerConsole).alias('rank'))\
  .filter(col('rank') <= 10)
  
qName = queryName.replace("queries", "").replace(".sql", "")
  
dfBestPerConsole.write.partitionBy('company','console')\
.mode("overwrite")\
.format("csv")\
.option('header', 'true')\
.save(f"{outputPath}{today}{qName}/BestPerConsole")

dfWorstPerConsole.write.partitionBy('company','console')\
.mode("overwrite")\
.format("csv")\
.option('header', 'true')\
.save(f"{outputPath}{today}{qName}/WorstPerConsole")

df10Best.write.mode("overwrite")\
.format("csv")\
.option('header', 'true')\
.save(f"{outputPath}{today}{qName}/10Best")

df10Worst.write.mode("overwrite")\
.format("csv")\
.option('header', 'true')\
.save(f"{outputPath}{today}{qName}/10Worst")