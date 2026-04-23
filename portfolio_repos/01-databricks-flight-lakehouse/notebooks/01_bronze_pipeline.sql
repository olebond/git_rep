-- Databricks notebook source
-- MAGIC %md
-- MAGIC # LAB2 Notes - Azure + Databricks Bronze Pipeline
-- MAGIC
-- MAGIC This notebook reads raw flight data from Azure Storage and writes it into the Bronze layer.
-- MAGIC
-- MAGIC ## Azure Storage
-- MAGIC
-- MAGIC Storage account:
-- MAGIC sadlsdev
-- MAGIC
-- MAGIC Container:
-- MAGIC bondarcontainer
-- MAGIC
-- MAGIC Folders:
-- MAGIC raw
-- MAGIC bronze
-- MAGIC silver
-- MAGIC gold
-- MAGIC
-- MAGIC Dataset used:
-- MAGIC flights.csv
-- MAGIC
-- MAGIC Raw file location:
-- MAGIC bondarcontainer/raw/flights.csv
-- MAGIC
-- MAGIC ## Databricks / Unity Catalog
-- MAGIC
-- MAGIC Catalog:
-- MAGIC dbr_dev
-- MAGIC
-- MAGIC Schemas:
-- MAGIC dbr_dev.bondar_raw
-- MAGIC dbr_dev.bondar_bronze
-- MAGIC dbr_dev.bondar_silver
-- MAGIC dbr_dev.bondar_gold
-- MAGIC
-- MAGIC ## Access objects
-- MAGIC
-- MAGIC External Location:
-- MAGIC sadlsdev_raw
-- MAGIC
-- MAGIC Raw Volume:
-- MAGIC dbr_dev.bondar_raw.raw_files
-- MAGIC
-- MAGIC ## Pipeline steps
-- MAGIC
-- MAGIC 1. Read raw CSV from Azure Storage
-- MAGIC 2. Apply a basic transformation with dropDuplicates()
-- MAGIC 3. Add metadata columns:
-- MAGIC    - source_file
-- MAGIC    - ingestion_timestamp
-- MAGIC    - load_date
-- MAGIC 4. Write Delta files into Azure bronze folder
-- MAGIC 5. Register an external Bronze table in Unity Catalog
-- MAGIC
-- MAGIC ## Idempotency
-- MAGIC
-- MAGIC The pipeline is idempotent because:
-- MAGIC - dropDuplicates() removes duplicate rows inside the dataset
-- MAGIC - mode("overwrite") rewrites the Bronze output on every run

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS dbr_dev.bondar_raw;

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS dbr_dev.bondar_bronze;

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS dbr_dev.bondar_silver;

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS dbr_dev.bondar_gold;

-- COMMAND ----------

CREATE EXTERNAL LOCATION IF NOT EXISTS sadlsdev_raw
URL 'abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/'
WITH (STORAGE CREDENTIAL dls_dev);

-- COMMAND ----------

CREATE EXTERNAL VOLUME IF NOT EXISTS dbr_dev.bondar_raw.raw_files
LOCATION 'abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/raw/';

-- COMMAND ----------

DROP VOLUME IF EXISTS dbr_dev.bondar_bronze.bronze_files;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC from pyspark.sql.functions import current_timestamp, current_date, col

-- COMMAND ----------

-- MAGIC %python
-- MAGIC raw_path = "/Volumes/dbr_dev/bondar_raw/raw_files/flights.csv"
-- MAGIC bronze_output_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/bronze/flights_bronze"

-- COMMAND ----------

-- MAGIC %python
-- MAGIC raw_df = (
-- MAGIC     spark.read
-- MAGIC     .option("header", True)
-- MAGIC     .option("inferSchema", True)
-- MAGIC     .csv(raw_path)
-- MAGIC )

-- COMMAND ----------

-- MAGIC %python
-- MAGIC bronze_df = (
-- MAGIC     raw_df
-- MAGIC     .dropDuplicates()
-- MAGIC     .withColumn("source_file", col("_metadata.file_path"))
-- MAGIC     .withColumn("ingestion_timestamp", current_timestamp())
-- MAGIC     .withColumn("load_date", current_date())
-- MAGIC )

-- COMMAND ----------

-- MAGIC %python
-- MAGIC bronze_df.write \
-- MAGIC     .format("delta") \
-- MAGIC     .mode("overwrite") \
-- MAGIC     .save(bronze_output_path)

-- COMMAND ----------

DROP TABLE IF EXISTS dbr_dev.bondar_bronze.flights_bronze_ext;

-- COMMAND ----------

CREATE TABLE dbr_dev.bondar_bronze.flights_bronze_ext
USING DELTA
LOCATION 'abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/bronze/flights_bronze';

-- COMMAND ----------

-- MAGIC %python
-- MAGIC test_df = spark.read.format("delta").load(bronze_output_path)
-- MAGIC
-- MAGIC test_df.limit(10).display()