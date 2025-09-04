from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.functions import explode, col, concat_ws

# --- Налаштування MSSQL ---
MSSQL_URL = "jdbc:sqlserver://localhost:1433;databaseName=flights_db;encrypt=true;trustServerCertificate=true"
MSSQL_TABLE = "tv_shows"
MSSQL_USER = "sa"
MSSQL_PASSWORD = "YourStrong@Passw0rd"
MSSQL_DRIVER = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
MSSQL_JAR = "study_spark/sqljdbc_12.10 2/enu/jars/mssql-jdbc-12.10.1.jre8.jar"

# --- Створення SparkSession ---
spark = SparkSession.builder \
    .appName("TVShows_MSSQL") \
    .config("spark.jars", MSSQL_JAR) \
    .getOrCreate()

# --- Зчитування JSON ---
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
df = df.withColumn("origin_country", concat_ws(",", col("origin_country")))

# names with status 'Canceled'
if "status" in df.columns:
    df_names_canceled = df.filter(col("status") == "Canceled").select("name")
    print("names with status Canceled:", df_names_canceled.count())
    df_names_canceled.write.mode("overwrite").csv("study_spark/jdbc_names_canceled.csv", header=True)

# origin_country popularity > 5.0
if "origin_country" in df.columns:
    df_popular = df.filter(col("popularity") > 5.0) \
        .withColumn("origin_country_str", concat_ws(",", col("origin_country"))) \
        .select("name", "origin_country_str", "popularity")
    print("Total records with popularity > 5.0:", df_popular.count())
    df_popular.write.mode("overwrite").csv("study_spark/jdbc_popularity_gt5.csv", header=True)

# number_of_episodes < 100
df_few_episodes = df.filter(col("number_of_episodes") < 100).select("name")
print("names with number_of_episodes < 100:", df_few_episodes.count())
df_few_episodes.write.mode("overwrite").csv("study_spark/jdbc_names_few_episodes.csv", header=True)

# --- Запис у MSSQL через JDBC ---
df.write.format("jdbc") \
    .option("url", MSSQL_URL) \
    .option("dbtable", MSSQL_TABLE) \
    .option("user", MSSQL_USER) \
    .option("password", MSSQL_PASSWORD) \
    .option("driver", MSSQL_DRIVER) \
    .mode("overwrite") \
    .save()

spark.stop() 