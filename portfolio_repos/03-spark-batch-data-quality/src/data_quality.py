from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def create_spark_session(app_name: str = "SparkDataQuality") -> SparkSession:
    return (
        SparkSession.builder.master("local[2]")
        .appName(app_name)
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )


def load_transactions(spark: SparkSession, path: str) -> DataFrame:
    return (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .option("timestampFormat", "yyyy/MM/dd HH:mm")
        .csv(path)
    )


def has_expected_column_count(df: DataFrame, expected_count: int) -> bool:
    if df is None:
        raise ValueError("df cannot be None")
    if expected_count < 0:
        raise ValueError("expected_count must be non-negative")
    return len(df.columns) == expected_count


def column_has_type(df: DataFrame, column_name: str, expected_type: str) -> bool:
    if df is None or column_name not in df.columns:
        return False
    actual_type = dict(df.dtypes).get(column_name)
    return str(actual_type).lower() == expected_type.lower()


def has_payment_format(df: DataFrame, payment_type: str) -> bool:
    if df is None or "Payment Format" not in df.columns:
        return False
    return df.filter(F.col("Payment Format") == payment_type).limit(1).count() > 0
