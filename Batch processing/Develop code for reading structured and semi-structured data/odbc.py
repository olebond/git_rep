import pyodbc
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import pandas as pd
from pyspark.sql.functions import explode, col, concat_ws

spark = SparkSession.builder.appName("TVShows_ODBC").getOrCreate()

df = spark.read.option("multiline", "true").json("study_spark/tvs.json")
df = df.select(
    "id", "name", "original_name", "overview", "tagline", "in_production", "status",
    "original_language", "first_air_date", "last_air_date", "number_of_episodes",
    "number_of_seasons", "poster_path", "vote_average", "vote_count", "popularity", "origin_country"
)
df = df.withColumn("first_air_date", F.when(F.col("first_air_date") == "", None).otherwise(F.col("first_air_date")))
df = df.withColumn("last_air_date", F.when(F.col("last_air_date") == "", None).otherwise(F.col("last_air_date")))
df = df.withColumn("first_air_date", F.to_date("first_air_date")) \
       .withColumn("last_air_date", F.to_date("last_air_date"))

if "status" in df.columns:
    df_names_canceled = df.filter(col("status") == "Canceled").select("name")
    print("names with status Canceled:", df_names_canceled.count())
    df_names_canceled.write.mode("overwrite").csv("study_spark/output_names_canceled.csv", header=True)

if "origin_country" in df.columns:
    df_popular = df.filter(col("popularity") > 5.0) \
        .withColumn("origin_country_str", concat_ws(",", col("origin_country"))) \
        .select("name", "origin_country_str", "popularity")
    print("Total records with popularity > 5.0:", df_popular.count())
    df_popular.write.mode("overwrite").csv("study_spark/output_popularity_gt5.csv", header=True)

df_few_episodes = df.filter(col("number_of_episodes") < 100).select("name")
print("names with number_of_episodes < 100:", df_few_episodes.count())
df_few_episodes.write.mode("overwrite").csv("study_spark/output_names_few_episodes.csv", header=True)

df.write \
    .format("com.microsoft.sqlserver.odbc.spark") \
    .option("url", "jdbc:sqlserver://localhost:1433;databaseName=flights_db") \
    .option("dbtable", "dbo.tv_shows") \
    .option("user", "sa") \
    .option("password", "YourStrong@Passw0rd") \
    .option("driver", "ODBC Driver 18 for SQL Server") \
    .mode("overwrite") \
    .save()
