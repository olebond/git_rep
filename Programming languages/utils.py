def create_spark_session(app_name="SparkUnitTestApp"):
    return (
        SparkSession.builder \
        .master("local[4]") \
        .appName(app_name) \
        .config("spark.driver.memory", "16g") \
        .config("spark.executor.memory", "16g") \
        .getOrCreate()
    )

def load_data(spark, path):
    return (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .option("timestampFormat", "yyyy/MM/dd HH:mm")
        .csv(path)
    )

def get_column_count(df, expected_count: int):
    if df is None:
        raise ValueError("df cannot be None")
    if not isinstance(expected_count, int):
        raise TypeError("expected_count must be int")
    if expected_count < 0:
        raise ValueError("expected_count must be non-negative")
    return len(df.columns) == expected_count


def check_timestamp_format(df, column_name, expected_type: str) -> bool:
    try:
        if df is None or column_name not in df.columns:
            return False
        dtype = df.select(column_name).dtypes[0][1]
        return str(dtype).lower() == str(expected_type).lower()
    except Exception:
        return False


def check_amount_received_is_float(df):
    return check_timestamp_format(df, "Amount Received", "double")


def check_timestamp_column(df):
    return check_timestamp_format(df, "Timestamp", "timestamp")


def has_payment_format(df, payment_type):
    try:
        return (
            df.select("Payment Format")
              .distinct()
              .filter(col("Payment Format") == payment_type)
              .limit(1)
              .count() > 0
        )
    except Exception:
        return False


 