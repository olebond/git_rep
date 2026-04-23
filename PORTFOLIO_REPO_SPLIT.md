# Portfolio Repository Split Plan

This repository was originally used as a learning workspace for Python, SQL, Spark, Airflow, Docker, and Databricks practice.

For job search purposes, the work is being reorganized into smaller, clearer project candidates under `portfolio_repos/`.
Each folder is designed to become a separate GitHub repository.

## Recommended Repositories

### 1. Databricks Flight Lakehouse

Path: `portfolio_repos/01-databricks-flight-lakehouse`

Focus:
- Azure Data Lake Storage
- Databricks
- Unity Catalog
- Delta Lake
- Bronze and Silver layers
- Auto Loader and Structured Streaming

Why this is valuable:
This is the strongest Junior Data Engineer portfolio project because it shows cloud data platform work, lakehouse architecture, and practical ingestion/transformation patterns.

### 2. Python Flight Data Converter

Path: `portfolio_repos/02-python-flight-data-converter`

Focus:
- Python CLI
- CSV processing
- Data transformation
- Unit tests
- Clean package structure

Why this is valuable:
This project shows Python fundamentals, clean project organization, testable code, and practical data processing.

### 3. Spark Batch Data Quality

Path: `portfolio_repos/03-spark-batch-data-quality`

Focus:
- PySpark
- Data validation
- Schema checks
- Unit testing Spark helper functions

Why this is valuable:
This project shows Spark basics and data quality thinking, which are useful for Junior Data Engineer roles.

### 4. Airflow File Pipeline

Path: `portfolio_repos/04-airflow-file-pipeline`

Focus:
- Apache Airflow
- DAG structure
- Docker Compose
- Simple orchestration workflow

Why this is valuable:
This project shows basic workflow orchestration and can be extended into a more realistic file ingestion pipeline.

## What Should Stay Out Of Portfolio Repos

- `legacy_snapshots/`
- `spark_local/`
- local database folders such as `study_docker/postgres_data/`
- generated Spark output folders
- `.DS_Store`, IDE files, local logs, archives, and large raw datasets

These files can stay in the learning workspace, but they should not be included in clean public portfolio repositories.

## Suggested Next Steps

1. Review each project folder in `portfolio_repos/`.
2. Choose which project should be polished first.
3. Move the chosen folder into a new standalone GitHub repository.
4. Add screenshots, architecture diagrams, and a short "How to run" section where needed.
5. Keep old learning materials private or archived.
