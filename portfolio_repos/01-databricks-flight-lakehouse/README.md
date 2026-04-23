# Databricks Flight Lakehouse

Training lakehouse project for ingesting flight data from Azure Data Lake Storage into Databricks using a Bronze/Silver architecture.

## What This Project Shows

- Raw CSV ingestion from Azure Data Lake Storage
- Databricks notebooks with PySpark and SQL
- Unity Catalog schemas, external locations, and volumes
- Bronze Delta table creation with ingestion metadata
- Silver layer transformations, validation, and deduplication
- Delta Lake `MERGE` logic for upserts
- SCD Type 2 table structure preparation
- File-based streaming with Auto Loader and Structured Streaming
- Event streaming design with Azure Event Hub

## Project Structure

```text
notebooks/
  01_bronze_ingestion.py
  01_bronze_pipeline.sql
  02_silver_pipeline.py
  03_streaming_ingestion.sql
```

## Interview Summary

This project demonstrates a Junior Data Engineer learning path around a modern lakehouse stack: Azure storage, Databricks, Delta Lake, governed access with Unity Catalog, and basic batch/streaming ingestion patterns.

## Notes

Some notebooks were created as Databricks labs. The Event Hub section contains prepared consumer/producer logic and should be described as a designed/prepared lab component unless executed with a real Event Hub.
