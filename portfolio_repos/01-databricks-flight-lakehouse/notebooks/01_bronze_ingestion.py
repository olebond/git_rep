# Databricks notebook source
# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC #lab2_bronze_ingestion
# MAGIC
# MAGIC # LAB2 Notes - Azure + Databricks Bronze Pipeline
# MAGIC
# MAGIC This notebook loads raw data from Azure Storage and writes it into a Bronze Delta table.
# MAGIC
# MAGIC **## Azure Storage**
# MAGIC
# MAGIC Storage account:
# MAGIC sadlsdev
# MAGIC
# MAGIC Container:
# MAGIC bondarcontainer
# MAGIC
# MAGIC Data lake folder structure:
# MAGIC
# MAGIC raw - raw source files (CSV / JSON)  
# MAGIC bronze - first processing layer  
# MAGIC silver - cleaned and standardized data (planned)  
# MAGIC gold - aggregated data for analytics
# MAGIC
# MAGIC Dataset used in this lab:
# MAGIC flights.csv
# MAGIC
# MAGIC File location in storage:
# MAGIC bondarcontainer/raw/flights.csv
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Databricks Environment
# MAGIC
# MAGIC Workspace:
# MAGIC dbr_dev
# MAGIC
# MAGIC Catalog:
# MAGIC dbr_dev
# MAGIC
# MAGIC Schemas used in the lakehouse:
# MAGIC
# MAGIC dbr_dev.bondar_raw  
# MAGIC dbr_dev.bondar_bronze  
# MAGIC dbr_dev.bondar_silver (planned)  
# MAGIC dbr_dev.bondar_gold (planned)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Access to Azure Storage
# MAGIC
# MAGIC External Location created:
# MAGIC sadlsdev_raw
# MAGIC
# MAGIC Path:
# MAGIC abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/
# MAGIC
# MAGIC External Volume created:
# MAGIC dbr_dev.bondar_raw.raw_files
# MAGIC
# MAGIC Databricks reads the raw data through the volume path:
# MAGIC
# MAGIC /Volumes/dbr_dev/bondar_raw/raw_files/
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Bronze Layer Pipeline
# MAGIC
# MAGIC Steps performed in this notebook:
# MAGIC
# MAGIC 1 Read raw CSV data from Azure Storage
# MAGIC 2 Apply a basic transformation (remove duplicates)
# MAGIC 3 Add metadata columns:
# MAGIC     source_file
# MAGIC     ingestion_timestamp
# MAGIC     load_date
# MAGIC 4 Write the result into a Delta table
# MAGIC
# MAGIC Bronze table created:
# MAGIC
# MAGIC dbr_dev.bondar_bronze.flights_bronze
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Idempotency
# MAGIC
# MAGIC The pipeline can be executed multiple times without creating duplicate data.
# MAGIC
# MAGIC This is ensured by using:
# MAGIC
# MAGIC mode("overwrite")
# MAGIC
# MAGIC and
# MAGIC
# MAGIC dropDuplicates()
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Data Flow
# MAGIC
# MAGIC flights.csv  
# MAGIC → RAW volume  
# MAGIC → Bronze Delta table  
# MAGIC → (Silver layer – LAB3)  
# MAGIC → (Gold layer – LAB3)
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Cluster Configuration
# MAGIC
# MAGIC Single node cluster
# MAGIC
# MAGIC Node type:
# MAGIC Standard_F4
# MAGIC
# MAGIC Resources:
# MAGIC 4 CPU  
# MAGIC 8 GB RAM  
# MAGIC
# MAGIC Auto termination:
# MAGIC 20 minutes

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE EXTERNAL LOCATION sadlsdev_raw
# MAGIC URL 'abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/'
# MAGIC WITH (STORAGE CREDENTIAL dls_dev);

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE EXTERNAL VOLUME dbr_dev.bondar_raw.raw_files
# MAGIC LOCATION 'abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/raw/';

# COMMAND ----------

display(dbutils.fs.ls("/Volumes/dbr_dev/bondar_raw/raw_files"))

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, current_date, col

# COMMAND ----------

raw_path = "/Volumes/dbr_dev/bondar_raw/raw_files/flights.csv"

raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(raw_path)
)

# COMMAND ----------

bronze_df = (
    raw_df
    .dropDuplicates()
    .withColumn("source_file", col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("load_date", current_date())
)

# COMMAND ----------

bronze_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("dbr_dev.bondar_bronze.flights_bronze")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS total_rows
# MAGIC FROM dbr_dev.bondar_bronze.flights_bronze;