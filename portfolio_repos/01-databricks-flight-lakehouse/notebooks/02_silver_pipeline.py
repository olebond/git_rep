# Databricks notebook source
bronze_df = spark.read.table("dbr_dev.bondar_bronze.flights_bronze")

display(bronze_df)
bronze_df.printSchema()
print(bronze_df.columns)
print(bronze_df.count())

# COMMAND ----------

silver_stage_df = bronze_df.toDF(*[col.lower() for col in bronze_df.columns])

# COMMAND ----------

silver_stage_df = bronze_df.toDF(*[col.lower() for col in bronze_df.columns])

print(silver_stage_df.columns)
silver_stage_df.printSchema()
display(silver_stage_df)

# COMMAND ----------

from pyspark.sql import functions as F

silver_stage_df = silver_stage_df.withColumn(
    "flight_date",
    F.to_date(
        F.concat_ws("-", F.col("year"), F.col("month"), F.col("day")),
        "yyyy-M-d"
    )
)

# COMMAND ----------

silver_stage_df.select("year", "month", "day", "flight_date").display()
silver_stage_df.printSchema()

# COMMAND ----------

silver_stage_df.filter(F.col("flight_date").isNull()).count()

# COMMAND ----------

silver_stage_df.filter(F.col("airline").isNull()).count()

# COMMAND ----------

silver_stage_df.filter(F.col("flight_number").isNull()).count()

# COMMAND ----------

silver_stage_df.filter(F.col("origin_airport").isNull()).count()

# COMMAND ----------

silver_stage_df.filter(F.col("destination_airport").isNull()).count()

# COMMAND ----------

silver_stage_df.select("departure_delay").describe().show()

# COMMAND ----------

silver_stage_df.select("arrival_delay").describe().show()

# COMMAND ----------

valid_df = (
    silver_stage_df
    .filter(F.col("flight_date").isNotNull())
    .filter(F.col("airline").isNotNull())
    .filter(F.col("flight_number").isNotNull())
    .filter(F.col("origin_airport").isNotNull())
    .filter(F.col("destination_airport").isNotNull())
    .filter((F.col("departure_delay").isNull()) | ((F.col("departure_delay") >= -200) & (F.col("departure_delay") <= 2000)))
    .filter((F.col("arrival_delay").isNull()) | ((F.col("arrival_delay") >= -200) & (F.col("arrival_delay") <= 2000)))
    .filter((F.col("cancelled").isNull()) | (F.col("cancelled").isin(0, 1)))
    .filter((F.col("diverted").isNull()) | (F.col("diverted").isin(0, 1)))
)

# COMMAND ----------

print("Before:", silver_stage_df.count())
print("After:", valid_df.count())

print("Rejected:", silver_stage_df.count() - valid_df.count())

# COMMAND ----------

from pyspark.sql.window import Window

window_spec = Window.partitionBy(
    "flight_date",
    "flight_number",
    "origin_airport",
    "destination_airport"
).orderBy(F.col("ingestion_timestamp").desc())

# COMMAND ----------

dedup_df = (
    valid_df
    .withColumn("rn", F.row_number().over(window_spec))
)

# COMMAND ----------

dedup_df = dedup_df.filter(F.col("rn") == 1).drop("rn")

# COMMAND ----------

print("Before dedup:", valid_df.count())
print("After dedup:", dedup_df.count())

# COMMAND ----------

spark.sql("CREATE SCHEMA IF NOT EXISTS dbr_dev.bondar_silver")

# COMMAND ----------

spark.sql("""
CREATE TABLE IF NOT EXISTS dbr_dev.bondar_silver.flights_silver (
    flight_date DATE,
    day_of_week INT,
    airline STRING,
    flight_number INT,
    tail_number STRING,
    origin_airport STRING,
    destination_airport STRING,
    scheduled_departure INT,
    departure_time INT,
    departure_delay INT,
    taxi_out INT,
    wheels_off INT,
    scheduled_time INT,
    elapsed_time INT,
    air_time INT,
    distance INT,
    wheels_on INT,
    taxi_in INT,
    scheduled_arrival INT,
    arrival_time INT,
    arrival_delay INT,
    diverted INT,
    cancelled INT,
    cancellation_reason STRING,
    air_system_delay INT,
    security_delay INT,
    airline_delay INT,
    late_aircraft_delay INT,
    weather_delay INT,
    source_file STRING,
    ingestion_timestamp TIMESTAMP,
    load_date DATE,
    silver_loaded_at TIMESTAMP
)
USING DELTA
""")

# COMMAND ----------

spark.sql("DESCRIBE dbr_dev.bondar_silver.flights_silver").show(100, False)

# COMMAND ----------

spark.sql("SELECT COUNT(*) AS row_count FROM dbr_dev.bondar_silver.flights_silver").show()

# COMMAND ----------

silver_merge_df = dedup_df.withColumn("silver_loaded_at", F.current_timestamp())

# COMMAND ----------

silver_merge_df.select("flight_date", "flight_number", "silver_loaded_at").show(10, False)

# COMMAND ----------

silver_merge_df.printSchema()

# COMMAND ----------

silver_final_df = silver_merge_df.select(
    "flight_date",
    "day_of_week",
    "airline",
    "flight_number",
    "tail_number",
    "origin_airport",
    "destination_airport",
    "scheduled_departure",
    "departure_time",
    "departure_delay",
    "taxi_out",
    "wheels_off",
    "scheduled_time",
    "elapsed_time",
    "air_time",
    "distance",
    "wheels_on",
    "taxi_in",
    "scheduled_arrival",
    "arrival_time",
    "arrival_delay",
    "diverted",
    "cancelled",
    "cancellation_reason",
    "air_system_delay",
    "security_delay",
    "airline_delay",
    "late_aircraft_delay",
    "weather_delay",
    "source_file",
    "ingestion_timestamp",
    "load_date",
    "silver_loaded_at"
)

# COMMAND ----------

silver_final_df.printSchema()

# COMMAND ----------

silver_final_df.select(
    "flight_date",
    "origin_airport",
    "destination_airport",
    "flight_number",
    "silver_loaded_at"
).show(10, False)

# COMMAND ----------

from delta.tables import DeltaTable

# COMMAND ----------

silver_table = DeltaTable.forName(spark, "dbr_dev.bondar_silver.flights_silver")

# COMMAND ----------

(
    silver_table.alias("t")
    .merge(
        silver_final_df.alias("s"),
        """
        t.flight_date = s.flight_date
        AND t.flight_number = s.flight_number
        AND t.origin_airport = s.origin_airport
        AND t.destination_airport = s.destination_airport
        """
    )
    .whenMatchedUpdate(set={
        "day_of_week": "s.day_of_week",
        "airline": "s.airline",
        "tail_number": "s.tail_number",
        "scheduled_departure": "s.scheduled_departure",
        "departure_time": "s.departure_time",
        "departure_delay": "s.departure_delay",
        "taxi_out": "s.taxi_out",
        "wheels_off": "s.wheels_off",
        "scheduled_time": "s.scheduled_time",
        "elapsed_time": "s.elapsed_time",
        "air_time": "s.air_time",
        "distance": "s.distance",
        "wheels_on": "s.wheels_on",
        "taxi_in": "s.taxi_in",
        "scheduled_arrival": "s.scheduled_arrival",
        "arrival_time": "s.arrival_time",
        "arrival_delay": "s.arrival_delay",
        "diverted": "s.diverted",
        "cancelled": "s.cancelled",
        "cancellation_reason": "s.cancellation_reason",
        "air_system_delay": "s.air_system_delay",
        "security_delay": "s.security_delay",
        "airline_delay": "s.airline_delay",
        "late_aircraft_delay": "s.late_aircraft_delay",
        "weather_delay": "s.weather_delay",
        "source_file": "s.source_file",
        "ingestion_timestamp": "s.ingestion_timestamp",
        "load_date": "s.load_date",
        "silver_loaded_at": "s.silver_loaded_at"
    })
    .whenNotMatchedInsert(values={
        "flight_date": "s.flight_date",
        "day_of_week": "s.day_of_week",
        "airline": "s.airline",
        "flight_number": "s.flight_number",
        "tail_number": "s.tail_number",
        "origin_airport": "s.origin_airport",
        "destination_airport": "s.destination_airport",
        "scheduled_departure": "s.scheduled_departure",
        "departure_time": "s.departure_time",
        "departure_delay": "s.departure_delay",
        "taxi_out": "s.taxi_out",
        "wheels_off": "s.wheels_off",
        "scheduled_time": "s.scheduled_time",
        "elapsed_time": "s.elapsed_time",
        "air_time": "s.air_time",
        "distance": "s.distance",
        "wheels_on": "s.wheels_on",
        "taxi_in": "s.taxi_in",
        "scheduled_arrival": "s.scheduled_arrival",
        "arrival_time": "s.arrival_time",
        "arrival_delay": "s.arrival_delay",
        "diverted": "s.diverted",
        "cancelled": "s.cancelled",
        "cancellation_reason": "s.cancellation_reason",
        "air_system_delay": "s.air_system_delay",
        "security_delay": "s.security_delay",
        "airline_delay": "s.airline_delay",
        "late_aircraft_delay": "s.late_aircraft_delay",
        "weather_delay": "s.weather_delay",
        "source_file": "s.source_file",
        "ingestion_timestamp": "s.ingestion_timestamp",
        "load_date": "s.load_date",
        "silver_loaded_at": "s.silver_loaded_at"
    })
    .execute()
)

# COMMAND ----------

spark.sql("SELECT COUNT(*) AS row_count FROM dbr_dev.bondar_silver.flights_silver").show()

# COMMAND ----------

spark.sql("""
SELECT flight_date, origin_airport, destination_airport, flight_number, silver_loaded_at
FROM dbr_dev.bondar_silver.flights_silver
LIMIT 10
""").show(10, False)

# COMMAND ----------

(
    silver_table.alias("t")
    .merge(
        silver_final_df.alias("s"),
        """
        t.flight_date = s.flight_date
        AND t.flight_number = s.flight_number
        AND t.origin_airport = s.origin_airport
        AND t.destination_airport = s.destination_airport
        """
    )
    .whenMatchedUpdate(set={
        "day_of_week": "s.day_of_week",
        "airline": "s.airline",
        "tail_number": "s.tail_number",
        "scheduled_departure": "s.scheduled_departure",
        "departure_time": "s.departure_time",
        "departure_delay": "s.departure_delay",
        "taxi_out": "s.taxi_out",
        "wheels_off": "s.wheels_off",
        "scheduled_time": "s.scheduled_time",
        "elapsed_time": "s.elapsed_time",
        "air_time": "s.air_time",
        "distance": "s.distance",
        "wheels_on": "s.wheels_on",
        "taxi_in": "s.taxi_in",
        "scheduled_arrival": "s.scheduled_arrival",
        "arrival_time": "s.arrival_time",
        "arrival_delay": "s.arrival_delay",
        "diverted": "s.diverted",
        "cancelled": "s.cancelled",
        "cancellation_reason": "s.cancellation_reason",
        "air_system_delay": "s.air_system_delay",
        "security_delay": "s.security_delay",
        "airline_delay": "s.airline_delay",
        "late_aircraft_delay": "s.late_aircraft_delay",
        "weather_delay": "s.weather_delay",
        "source_file": "s.source_file",
        "ingestion_timestamp": "s.ingestion_timestamp",
        "load_date": "s.load_date",
        "silver_loaded_at": "s.silver_loaded_at"
    })
    .whenNotMatchedInsert(values={
        "flight_date": "s.flight_date",
        "day_of_week": "s.day_of_week",
        "airline": "s.airline",
        "flight_number": "s.flight_number",
        "tail_number": "s.tail_number",
        "origin_airport": "s.origin_airport",
        "destination_airport": "s.destination_airport",
        "scheduled_departure": "s.scheduled_departure",
        "departure_time": "s.departure_time",
        "departure_delay": "s.departure_delay",
        "taxi_out": "s.taxi_out",
        "wheels_off": "s.wheels_off",
        "scheduled_time": "s.scheduled_time",
        "elapsed_time": "s.elapsed_time",
        "air_time": "s.air_time",
        "distance": "s.distance",
        "wheels_on": "s.wheels_on",
        "taxi_in": "s.taxi_in",
        "scheduled_arrival": "s.scheduled_arrival",
        "arrival_time": "s.arrival_time",
        "arrival_delay": "s.arrival_delay",
        "diverted": "s.diverted",
        "cancelled": "s.cancelled",
        "cancellation_reason": "s.cancellation_reason",
        "air_system_delay": "s.air_system_delay",
        "security_delay": "s.security_delay",
        "airline_delay": "s.airline_delay",
        "late_aircraft_delay": "s.late_aircraft_delay",
        "weather_delay": "s.weather_delay",
        "source_file": "s.source_file",
        "ingestion_timestamp": "s.ingestion_timestamp",
        "load_date": "s.load_date",
        "silver_loaded_at": "s.silver_loaded_at"
    })
    .execute()
)

# COMMAND ----------

spark.sql("SELECT COUNT(*) AS row_count FROM dbr_dev.bondar_silver.flights_silver").show()

# COMMAND ----------

spark.sql("""
CREATE TABLE IF NOT EXISTS dbr_dev.bondar_silver.flights_silver_scd2 (
    flight_date DATE,
    day_of_week INT,
    airline STRING,
    flight_number INT,
    tail_number STRING,
    origin_airport STRING,
    destination_airport STRING,
    scheduled_departure INT,
    departure_time INT,
    departure_delay INT,
    taxi_out INT,
    wheels_off INT,
    scheduled_time INT,
    elapsed_time INT,
    air_time INT,
    distance INT,
    wheels_on INT,
    taxi_in INT,
    scheduled_arrival INT,
    arrival_time INT,
    arrival_delay INT,
    diverted INT,
    cancelled INT,
    cancellation_reason STRING,
    air_system_delay INT,
    security_delay INT,
    airline_delay INT,
    late_aircraft_delay INT,
    weather_delay INT,
    source_file STRING,
    ingestion_timestamp TIMESTAMP,
    load_date DATE,
    silver_loaded_at TIMESTAMP,
    record_hash STRING,
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    is_current BOOLEAN
)
USING DELTA
""")

# COMMAND ----------

cols = spark.table("dbr_dev.bondar_silver.flights_silver_scd2").columns

print("record_hash" in cols)
print("effective_from" in cols)
print("effective_to" in cols)
print("is_current" in cols)

# COMMAND ----------

scd2_source_df = (
    silver_final_df
    .withColumn(
        "record_hash",
        F.sha2(
            F.concat_ws(
                "||",
                F.coalesce(F.col("day_of_week").cast("string"), F.lit("")),
                F.coalesce(F.col("airline"), F.lit("")),
                F.coalesce(F.col("flight_number").cast("string"), F.lit("")),
                F.coalesce(F.col("tail_number"), F.lit("")),
                F.coalesce(F.col("origin_airport"), F.lit("")),
                F.coalesce(F.col("destination_airport"), F.lit("")),
                F.coalesce(F.col("scheduled_departure").cast("string"), F.lit("")),
                F.coalesce(F.col("departure_time").cast("string"), F.lit("")),
                F.coalesce(F.col("departure_delay").cast("string"), F.lit("")),
                F.coalesce(F.col("taxi_out").cast("string"), F.lit("")),
                F.coalesce(F.col("wheels_off").cast("string"), F.lit("")),
                F.coalesce(F.col("scheduled_time").cast("string"), F.lit("")),
                F.coalesce(F.col("elapsed_time").cast("string"), F.lit("")),
                F.coalesce(F.col("air_time").cast("string"), F.lit("")),
                F.coalesce(F.col("distance").cast("string"), F.lit("")),
                F.coalesce(F.col("wheels_on").cast("string"), F.lit("")),
                F.coalesce(F.col("taxi_in").cast("string"), F.lit("")),
                F.coalesce(F.col("scheduled_arrival").cast("string"), F.lit("")),
                F.coalesce(F.col("arrival_time").cast("string"), F.lit("")),
                F.coalesce(F.col("arrival_delay").cast("string"), F.lit("")),
                F.coalesce(F.col("diverted").cast("string"), F.lit("")),
                F.coalesce(F.col("cancelled").cast("string"), F.lit("")),
                F.coalesce(F.col("cancellation_reason"), F.lit("")),
                F.coalesce(F.col("air_system_delay").cast("string"), F.lit("")),
                F.coalesce(F.col("security_delay").cast("string"), F.lit("")),
                F.coalesce(F.col("airline_delay").cast("string"), F.lit("")),
                F.coalesce(F.col("late_aircraft_delay").cast("string"), F.lit("")),
                F.coalesce(F.col("weather_delay").cast("string"), F.lit(""))
            ),
            256
        )
    )
    .withColumn("effective_from", F.current_timestamp())
    .withColumn("effective_to", F.lit(None).cast("timestamp"))
    .withColumn("is_current", F.lit(True))
)

scd2_source_df.select(
    "flight_date",
    "flight_number",
    "origin_airport",
    "destination_airport",
    "record_hash",
    "effective_from",
    "effective_to",
    "is_current"
).show(10, False)

scd2_source_df.printSchema()

# COMMAND ----------

scd2_source_df.write.format("delta").mode("append").saveAsTable("dbr_dev.bondar_silver.flights_silver_scd2")

# COMMAND ----------

spark.sql("SELECT COUNT(*) AS row_count FROM dbr_dev.bondar_silver.flights_silver_scd2").show()

# COMMAND ----------

from pyspark.sql.functions import when

scd2_changed_df = scd2_source_df.withColumn(
    "arrival_delay",
    when(F.col("flight_number") == 2, F.col("arrival_delay") + 10)
    .otherwise(F.col("arrival_delay"))
)

# COMMAND ----------

scd2_changed_df = scd2_changed_df.withColumn(
    "record_hash",
    F.sha2(
        F.concat_ws(
            "||",
            F.coalesce(F.col("day_of_week").cast("string"), F.lit("")),
            F.coalesce(F.col("airline"), F.lit("")),
            F.coalesce(F.col("flight_number").cast("string"), F.lit("")),
            F.coalesce(F.col("tail_number"), F.lit("")),
            F.coalesce(F.col("origin_airport"), F.lit("")),
            F.coalesce(F.col("destination_airport"), F.lit("")),
            F.coalesce(F.col("scheduled_departure").cast("string"), F.lit("")),
            F.coalesce(F.col("departure_time").cast("string"), F.lit("")),
            F.coalesce(F.col("departure_delay").cast("string"), F.lit("")),
            F.coalesce(F.col("taxi_out").cast("string"), F.lit("")),
            F.coalesce(F.col("wheels_off").cast("string"), F.lit("")),
            F.coalesce(F.col("scheduled_time").cast("string"), F.lit("")),
            F.coalesce(F.col("elapsed_time").cast("string"), F.lit("")),
            F.coalesce(F.col("air_time").cast("string"), F.lit("")),
            F.coalesce(F.col("distance").cast("string"), F.lit("")),
            F.coalesce(F.col("wheels_on").cast("string"), F.lit("")),
            F.coalesce(F.col("taxi_in").cast("string"), F.lit("")),
            F.coalesce(F.col("scheduled_arrival").cast("string"), F.lit("")),
            F.coalesce(F.col("arrival_time").cast("string"), F.lit("")),
            F.coalesce(F.col("arrival_delay").cast("string"), F.lit("")),
            F.coalesce(F.col("diverted").cast("string"), F.lit("")),
            F.coalesce(F.col("cancelled").cast("string"), F.lit("")),
            F.coalesce(F.col("cancellation_reason"), F.lit("")),
            F.coalesce(F.col("air_system_delay").cast("string"), F.lit("")),
            F.coalesce(F.col("security_delay").cast("string"), F.lit("")),
            F.coalesce(F.col("airline_delay").cast("string"), F.lit("")),
            F.coalesce(F.col("late_aircraft_delay").cast("string"), F.lit("")),
            F.coalesce(F.col("weather_delay").cast("string"), F.lit(""))
        ),
        256
    )
)

# COMMAND ----------

scd2_changed_df = scd2_changed_df \
    .withColumn("effective_from", F.current_timestamp()) \
    .withColumn("effective_to", F.lit(None).cast("timestamp")) \
    .withColumn("is_current", F.lit(True))

# COMMAND ----------

scd2_changed_df.filter(F.col("flight_number") == 2).select(
    "flight_number",
    "arrival_delay"
).show(10)

# COMMAND ----------

from delta.tables import DeltaTable

scd2_table = DeltaTable.forName(spark, "dbr_dev.bondar_silver.flights_silver_scd2")

(
    scd2_table.alias("t")
    .merge(
        scd2_changed_df.alias("s"),
        """
        t.flight_date = s.flight_date
        AND t.flight_number = s.flight_number
        AND t.origin_airport = s.origin_airport
        AND t.destination_airport = s.destination_airport
        AND t.is_current = true
        """
    )
    .whenMatchedUpdate(
        condition="t.record_hash <> s.record_hash",
        set={
            "effective_to": "current_timestamp()",
            "is_current": "false"
        }
    )
    .execute()
)

# COMMAND ----------

current_target_df = spark.read.table("dbr_dev.bondar_silver.flights_silver_scd2").filter("is_current = true")

new_or_changed_df = (
    scd2_changed_df.alias("s")
    .join(
        current_target_df.alias("t"),
        on=[
            F.col("s.flight_date") == F.col("t.flight_date"),
            F.col("s.flight_number") == F.col("t.flight_number"),
            F.col("s.origin_airport") == F.col("t.origin_airport"),
            F.col("s.destination_airport") == F.col("t.destination_airport")
        ],
        how="left"
    )
    .filter(
        F.col("t.flight_date").isNull() |
        (F.col("s.record_hash") != F.col("t.record_hash"))
    )
    .select("s.*")
)

new_or_changed_df.write.format("delta").mode("append").saveAsTable("dbr_dev.bondar_silver.flights_silver_scd2")

# Validate SCD2 result
spark.sql("SELECT COUNT(*) AS row_count FROM dbr_dev.bondar_silver.flights_silver_scd2").show()

spark.sql("""
SELECT
    flight_date,
    flight_number,
    origin_airport,
    destination_airport,
    arrival_delay,
    record_hash,
    is_current,
    effective_from,
    effective_to
FROM dbr_dev.bondar_silver.flights_silver_scd2
WHERE flight_number = 2
ORDER BY flight_date, origin_airport, destination_airport, effective_from
""").show(50, False)

# COMMAND ----------

optimize_result_1 = spark.sql("""
OPTIMIZE dbr_dev.bondar_silver.flights_silver
ZORDER BY (flight_date, origin_airport, destination_airport)
""")

display(optimize_result_1)

# COMMAND ----------

optimize_result_2 = spark.sql("""
OPTIMIZE dbr_dev.bondar_silver.flights_silver_scd2
ZORDER BY (flight_date, origin_airport, destination_airport)
""")

display(optimize_result_2)

# COMMAND ----------

spark.sql("VACUUM dbr_dev.bondar_silver.flights_silver RETAIN 168 HOURS")

# COMMAND ----------

spark.sql("VACUUM dbr_dev.bondar_silver.flights_silver_scd2 RETAIN 168 HOURS")

# COMMAND ----------

silver_output_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/silver/flights_silver"
scd2_output_path = "abfss://bondarcontainer@sadlsdev.dfs.core.windows.net/silver/flights_silver_scd2"

silver_df = spark.read.table("dbr_dev.bondar_silver.flights_silver")
scd2_df = spark.read.table("dbr_dev.bondar_silver.flights_silver_scd2")

(
    silver_df.write
    .format("delta")
    .mode("overwrite")
    .save(silver_output_path)
)

(
    scd2_df.write
    .format("delta")
    .mode("overwrite")
    .save(scd2_output_path)
)

assert spark.read.format("delta").load(silver_output_path).count() == 5814254
assert spark.read.format("delta").load(scd2_output_path).count() == 5816314