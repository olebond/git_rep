from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.functions import col, concat_ws
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType  
import logging
import sys
import os
from datetime import datetime

MSSQL_URL = "jdbc:sqlserver://localhost:1433;databaseName=flights_db;encrypt=true;trustServerCertificate=true"
MSSQL_TABLE = "tv_shows"
MSSQL_USER = "sa"
MSSQL_PASSWORD = "YourStrong@Passw0rd"
MSSQL_DRIVER = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
MSSQL_JAR = "study_spark/sqljdbc_12.10 2/enu/jars/mssql-jdbc-12.10.1.jre8.jar"

spark = SparkSession.builder \
    .appName("TVShows_MSSQL") \
    .config("spark.jars", MSSQL_JAR) \
    .getOrCreate()

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('spark_batch')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_formatter)

os.makedirs('output', exist_ok=True)
file_handler = logging.FileHandler('output/handle-error.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_formatter)

logger.handlers = []
logger.addHandler(console_handler)
logger.addHandler(file_handler)

start_time = datetime.now()

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("original_name", StringType(), True),
    StructField("overview", StringType(), True),
    StructField("tagline", StringType(), True),
    StructField("in_production", BooleanType(), True),
    StructField("status", StringType(), True),
    StructField("original_language", StringType(), True),
    StructField("first_air_date", StringType(), True),
    StructField("last_air_date", StringType(), True),
    StructField("number_of_episodes", IntegerType(), True),
    StructField("number_of_seasons", IntegerType(), True),
    StructField("poster_path", StringType(), True),
    StructField("vote_average", DoubleType(), True),
    StructField("vote_count", IntegerType(), True),
    StructField("popularity", DoubleType(), True),
    StructField("origin_country", StringType(), True),
])

#/Users/admin/Desktop/git_rep/study_spark/tvs.json
json_path = "study_spark/tvss.json"
while True:
    try:
        df = spark.read.schema(schema).option("multiline", "true").json(json_path)
        logger.debug(f"Successfully read file: {json_path}")
        break
    except Exception as e:
        logger.debug(f"File not found or error reading file at path: {json_path}. Error: {e}")
        logger.warning(f"File not found at path: {json_path}")
        print(f"File not found at path: {json_path}. Please enter the correct path to the JSON file:")
        json_path = input("Enter path to JSON file: ")

#df = df.withColumn("first_air_date", F.when(F.col("first_air_date") == "", None).otherwise(F.col("first_air_date")))
#df = df.withColumn("last_air_date", F.when(F.col("last_air_date") == "", None).otherwise(F.col("last_air_date")))
#df = df.withColumn("first_air_date", F.to_date("first_air_date")) \
#       .withColumn("last_air_date", F.to_date("last_air_date"))
#df = df.withColumn("origin_country", concat_ws(",", col("origin_country")))

df.persist()

try:
    describe_df = df.describe()
    describe_str = describe_df.toPandas().to_string()
    logger.warning(f"DataFrame describe:\n{describe_str}")
except Exception as e:
    logger.warning(f"Could not describe DataFrame: {e}")

try:
    schema_info = "\n".join([f"{field.name}: {field.dataType}" for field in df.schema.fields])
    logger.warning(f"DataFrame schema:\n{schema_info}")
except Exception as e:
    logger.warning(f"Could not log DataFrame schema: {e}")

try:
    if "status" in df.columns:
        df_names_canceled = df.filter(col("status") == "Canceled").select("name")
        logger.info(f"names with status Canceled: {df_names_canceled.count()}")
        df_names_canceled.write.mode("overwrite").csv("study_spark/jdbc2_names_canceled.csv", header=True)

    if "origin_country" in df.columns:
        df_popular = df.filter(col("popularity") > 5.0) \
            .withColumn("origin_country_str", concat_ws(",", col("origin_country"))) \
            .select("name", "origin_country_str", "popularity")
        logger.info(f"Total records with popularity > 5.0: {df_popular.count()}")
        df_popular.write.mode("overwrite").csv("study_spark/jdbc2_popularity_gt5.csv", header=True)

    df_few_episodes = df.filter(col("number_of_episodes") < 100).select("name")
    logger.info(f"names with number_of_episodes < 100: {df_few_episodes.count()}")
    df_few_episodes.write.mode("overwrite").csv("study_spark/jdbc2_names_few_episodes.csv", header=True)


    df.write.format("jdbc") \
        .option("url", MSSQL_URL) \
        .option("dbtable", MSSQL_TABLE) \
        .option("user", MSSQL_USER) \
        .option("password", MSSQL_PASSWORD) \
        .option("driver", MSSQL_DRIVER) \
        .mode("overwrite") \
        .save()

except Exception as e:
    logger.fatal(f"Fatal error during Spark batch processing: {e}")
    print(f"Fatal error occurred: {e}")
finally:
    end_time = datetime.now()
    timer = (end_time - start_time).total_seconds()
    logger.info(f"Batch processing finished. Elapsed time: {timer} seconds.")
    try:
        logger.info(f"Total records processed: {df.count()}")
    except Exception:
        logger.warning("Could not count records in DataFrame.")
    df.unpersist()
    spark.stop() 