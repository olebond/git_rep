from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, coalesce


def create_spark_session(app_name="SparkUnitTestApp"):
    return (
        SparkSession.builder \
        .master("local[4]") \
        .appName("SparkUnitTestApp") \
        .config("spark.driver.memory", "16g") \
        .config("spark.executor.memory", "16g") \
        .getOrCreate()
    )


def load_data(spark, path):
    return spark.read.csv(path, header=True, inferSchema=True)


def get_column_count(df, expected_count):
    try:
        return len(df.columns) == expected_count
    except Exception:
        return False


def check_column_parses(df, column_name, *, numeric_type=None, timestamp_formats=None):
    try:
        if numeric_type is not None:
            invalid_count = (
                df.select(column_name)
                  .filter(col(column_name).cast(numeric_type).isNull())
                  .count()
            )
            return invalid_count == 0

        if timestamp_formats is not None:
            timestamp_col = coalesce(*[to_timestamp(col(column_name), fmt) for fmt in timestamp_formats])
            invalid_count = df.filter(timestamp_col.isNull()).count()
            return invalid_count == 0

        return False
    except Exception:
        return False


def check_amount_received_is_float(df):
    return check_column_parses(df, "Amount Received", numeric_type="double")


def check_timestamp_format(df, formats=["yyyy/MM/dd HH:mm", "yyyy-MM-dd HH:mm:ss"]):
    return check_column_parses(df, "Timestamp", timestamp_formats=formats)


def check_payment_format_valid(df, valid_values):
    try:
        invalid_count = (
            df.select("Payment Format")
              .filter(col("Payment Format").isin(valid_values) == False)
              .count()
        )
        return invalid_count == 0
    except Exception:
        return False


def get_distinct_payment_formats(df):
    try:
        return [row[0] for row in df.select("Payment Format").distinct().collect()]
    except Exception:
        return []

def has_payment_format(df, payment_type):
    formats = set(get_distinct_payment_formats(df))
    return payment_type in formats


if __name__ == "__main__":
    spark = create_spark_session()
    df_header_check = load_data(spark, "HI-Large_Trans.csv").limit(1)
    header_status = get_column_count(df_header_check, 11)

    df_full = load_data(spark, "HI-Large_Trans.csv")
    df = df_full.select("Amount Received", "Timestamp", "Payment Format").cache()
    check_amount_received_is_float(df)
    check_timestamp_format(df)

    distinct_formats = get_distinct_payment_formats(df)
    check_payment_format_valid(df, distinct_formats)
    has_payment_format(df, "Reinvestment")