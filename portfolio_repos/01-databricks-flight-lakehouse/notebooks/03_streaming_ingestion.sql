-- Databricks notebook source
-- MAGIC %md
-- MAGIC # LAB3 - Streaming and Event-Based Ingestion
-- MAGIC
-- MAGIC ## File Streaming
-- MAGIC - Generate multiple input files
-- MAGIC - Auto Loader ingestion
-- MAGIC - Trigger experiment
-- MAGIC - Full reload validation
-- MAGIC
-- MAGIC ## Event Streaming
-- MAGIC - Synthetic producer
-- MAGIC - Event Hub consumer design
-- MAGIC - Bronze sink
-- MAGIC - Job and cost awareness

-- COMMAND ----------

-- MAGIC %python
-- MAGIC flights_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/raw/flights.csv"
-- MAGIC
-- MAGIC flights_df = (
-- MAGIC     spark.read
-- MAGIC     .format("csv")
-- MAGIC     .option("header", True)
-- MAGIC     .option("inferSchema", True)
-- MAGIC     .load(flights_path)
-- MAGIC )

-- COMMAND ----------

-- MAGIC %python
-- MAGIC flights_df.count()

-- COMMAND ----------

-- MAGIC %python
-- MAGIC flights_df.printSchema()

-- COMMAND ----------

-- MAGIC %python
-- MAGIC stream_input_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/raw/flights_stream_input/"

-- COMMAND ----------

-- MAGIC %python
-- MAGIC dbutils.fs.rm(stream_input_path, True)

-- COMMAND ----------

-- MAGIC %python
-- MAGIC dbutils.fs.mkdirs(stream_input_path)

-- COMMAND ----------

-- MAGIC %python
-- MAGIC (
-- MAGIC     flights_df
-- MAGIC     .repartition(800)
-- MAGIC     .write
-- MAGIC     .mode("overwrite")
-- MAGIC     .option("header", True)
-- MAGIC     .csv(stream_input_path)
-- MAGIC )

-- COMMAND ----------

-- MAGIC %python
-- MAGIC source_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/raw/flights_stream_input/"
-- MAGIC bronze_output_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/bronze/flights_stream_bronze/"
-- MAGIC checkpoint_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/_checkpoint/autoloader_flights/"
-- MAGIC schema_location = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/_schemas/autoloader_flights/"

-- COMMAND ----------

-- MAGIC %python
-- MAGIC dbutils.fs.rm(bronze_output_path, True)
-- MAGIC dbutils.fs.rm(checkpoint_path, True)
-- MAGIC dbutils.fs.rm(schema_location, True)

-- COMMAND ----------

-- MAGIC %python
-- MAGIC from pyspark.sql.functions import current_timestamp, col
-- MAGIC
-- MAGIC stream_df = (
-- MAGIC     spark.readStream
-- MAGIC     .format("cloudFiles")
-- MAGIC     .option("cloudFiles.format", "csv")
-- MAGIC     .option("cloudFiles.schemaLocation", schema_location)
-- MAGIC     .option("header", True)
-- MAGIC     .load(source_path)
-- MAGIC )
-- MAGIC
-- MAGIC bronze_stream = (
-- MAGIC     stream_df
-- MAGIC     .withColumn("source_file", col("_metadata.file_path"))
-- MAGIC     .withColumn("ingestion_timestamp", current_timestamp())
-- MAGIC )
-- MAGIC
-- MAGIC query = (
-- MAGIC     bronze_stream.writeStream
-- MAGIC     .format("delta")
-- MAGIC     .option("checkpointLocation", checkpoint_path)
-- MAGIC     .outputMode("append")
-- MAGIC     .trigger(once=True)
-- MAGIC     .start(bronze_output_path)
-- MAGIC )

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Trigger Experiment - Trigger Once and Reload
-- MAGIC
-- MAGIC To simulate a full reprocessing scenario, the checkpoint directory was removed before restarting the stream.
-- MAGIC
-- MAGIC This step resets the streaming state, meaning that Spark no longer remembers which files were previously processed.
-- MAGIC
-- MAGIC As a result, all input files are treated as new data.
-- MAGIC
-- MAGIC After deleting the checkpoint, the streaming job was executed using the `trigger(once=True)` option.
-- MAGIC
-- MAGIC This trigger processes all available data in a single run and then stops automatically, behaving similarly to a batch job while still using the streaming API.
-- MAGIC
-- MAGIC This approach is useful for:
-- MAGIC - scheduled data ingestion jobs
-- MAGIC - cost-efficient processing (no long-running cluster)
-- MAGIC - controlled reprocessing of data
-- MAGIC
-- MAGIC It also demonstrates how streaming pipelines can be safely restarted and re-executed when needed.

-- COMMAND ----------

-- MAGIC %python
-- MAGIC dbutils.fs.rm(bronze_output_path, True)
-- MAGIC dbutils.fs.rm(checkpoint_path, True)
-- MAGIC dbutils.fs.rm(schema_location, True)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Full Data Reload
-- MAGIC
-- MAGIC To simulate a full data reprocessing scenario, both the checkpoint directory and the Bronze output path were cleared.
-- MAGIC
-- MAGIC This ensures that Spark does not retain any information about previously processed files.
-- MAGIC
-- MAGIC The pipeline was then executed using `trigger(once=True)`, which processed all available input files in a single run and recreated the Bronze table from scratch.
-- MAGIC
-- MAGIC The final row count matched the original dataset (5,819,079 records), confirming that the reload was successful and no duplicate data was introduced.

-- COMMAND ----------

-- MAGIC %python
-- MAGIC bronze_df = spark.read.format("delta").load(bronze_output_path)
-- MAGIC display(bronze_df)

-- COMMAND ----------

-- MAGIC %python
-- MAGIC bronze_df.count()

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # Event Streaming
-- MAGIC
-- MAGIC This section demonstrates event-based ingestion using Azure Event Hub and Spark Structured Streaming.
-- MAGIC
-- MAGIC Planned architecture:
-- MAGIC
-- MAGIC Synthetic Data Producer
-- MAGIC ↓
-- MAGIC Azure Event Hub
-- MAGIC ↓
-- MAGIC Spark Structured Streaming Consumer
-- MAGIC ↓
-- MAGIC Bronze Delta Table
-- MAGIC
-- MAGIC Because the shared Event Hubs namespace had reached its resource limit, the Event Hub creation step could not be completed immediately.
-- MAGIC
-- MAGIC The pipeline logic and code structure were still prepared in advance for execution once an Event Hub becomes available.

-- COMMAND ----------

-- MAGIC %python
-- MAGIC event_bronze_output_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/bronze/synthetic_event_stream_bronze/"
-- MAGIC event_checkpoint_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/_checkpoint/synthetic_event_stream/"

-- COMMAND ----------

-- MAGIC %python
-- MAGIC from azure.eventhub import EventHubProducerClient, EventData
-- MAGIC import json
-- MAGIC import time
-- MAGIC import random
-- MAGIC
-- MAGIC connection_str = "<PUT_YOUR_CONNECTION_STRING_HERE>"
-- MAGIC eventhub_name = "bondar-eh"
-- MAGIC
-- MAGIC producer = EventHubProducerClient.from_connection_string(
-- MAGIC     conn_str=connection_str,
-- MAGIC     eventhub_name=eventhub_name
-- MAGIC )
-- MAGIC
-- MAGIC def generate_event():
-- MAGIC     return {
-- MAGIC         "event_id": random.randint(1, 1000000),
-- MAGIC         "event_type": random.choice(["click", "view", "purchase"]),
-- MAGIC         "user_id": random.randint(1, 10000),
-- MAGIC         "timestamp": int(time.time())
-- MAGIC     }
-- MAGIC
-- MAGIC # event = generate_event()
-- MAGIC # event_data = EventData(json.dumps(event))
-- MAGIC # producer.send_batch([event_data])

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Synthetic Event Producer
-- MAGIC
-- MAGIC A synthetic event producer was prepared using the Azure Event Hub Python SDK.
-- MAGIC
-- MAGIC The producer is designed to generate simple JSON events with the following fields:
-- MAGIC - event_id
-- MAGIC - event_type
-- MAGIC - user_id
-- MAGIC - timestamp
-- MAGIC
-- MAGIC These events simulate user activity such as clicks, views, and purchases.
-- MAGIC
-- MAGIC At this stage, the producer code was prepared but not executed, because the shared Event Hubs namespace had reached its Event Hub limit and a dedicated Event Hub was not yet available.

-- COMMAND ----------

-- MAGIC %python
-- MAGIC from pyspark.sql.functions import col, from_json
-- MAGIC from pyspark.sql.types import StructType, StringType, IntegerType
-- MAGIC
-- MAGIC eventhub_connection_string = "<PUT_YOUR_CONNECTION_STRING_HERE>"
-- MAGIC
-- MAGIC eh_conf = {
-- MAGIC     "eventhubs.connectionString": eventhub_connection_string
-- MAGIC }
-- MAGIC
-- MAGIC event_stream_df = (
-- MAGIC     spark.readStream
-- MAGIC     .format("eventhubs")
-- MAGIC     .options(**eh_conf)
-- MAGIC     .load()
-- MAGIC )

-- COMMAND ----------

-- MAGIC %python
-- MAGIC schema = StructType() \
-- MAGIC     .add("event_id", IntegerType()) \
-- MAGIC     .add("event_type", StringType()) \
-- MAGIC     .add("user_id", IntegerType()) \
-- MAGIC     .add("timestamp", IntegerType())
-- MAGIC
-- MAGIC parsed_df = event_stream_df.selectExpr("CAST(body AS STRING)") \
-- MAGIC     .select(from_json(col("body"), schema).alias("data")) \
-- MAGIC     .select("data.*")

-- COMMAND ----------

-- MAGIC %python
-- MAGIC from pyspark.sql.functions import current_timestamp
-- MAGIC
-- MAGIC event_enriched_df = (
-- MAGIC     parsed_df
-- MAGIC     .withColumn("ingestion_timestamp", current_timestamp())
-- MAGIC )

-- COMMAND ----------

-- MAGIC %md
-- MAGIC **Note:** This cell is prepared for execution once a dedicated Event Hub and valid connection string become available.

-- COMMAND ----------

-- MAGIC %python
-- MAGIC event_query = (
-- MAGIC     event_enriched_df.writeStream
-- MAGIC     .format("delta")
-- MAGIC     .option("checkpointLocation", event_checkpoint_path)
-- MAGIC     .outputMode("append")
-- MAGIC     .trigger(once=True)
-- MAGIC     .start(event_bronze_output_path)
-- MAGIC )

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Event Streaming Pipeline
-- MAGIC
-- MAGIC An event-based ingestion pipeline was designed using Azure Event Hub and Spark Structured Streaming.
-- MAGIC
-- MAGIC A synthetic data producer was prepared to generate JSON-based events simulating user activity.
-- MAGIC
-- MAGIC The Spark consumer was configured to:
-- MAGIC - read streaming events from Event Hub
-- MAGIC - parse the JSON payload
-- MAGIC - enrich the stream with ingestion metadata
-- MAGIC - write the result into a Bronze Delta table
-- MAGIC
-- MAGIC Due to the shared Event Hub namespace reaching its resource limit, a dedicated Event Hub could not be created during this lab.
-- MAGIC
-- MAGIC However, the full pipeline logic and notebook implementation were prepared and are ready to be executed once an Event Hub becomes available.