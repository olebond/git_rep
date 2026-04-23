from pathlib import Path

from data_quality import (
    column_has_type,
    create_spark_session,
    has_expected_column_count,
    has_payment_format,
    load_transactions,
)

DATA_DIR = Path(__file__).parent.parent / "data"


def test_valid_transaction_dataset():
    spark = create_spark_session("valid-transaction-test")
    try:
        df = load_transactions(spark, str(DATA_DIR / "transactions_valid.csv"))

        assert has_expected_column_count(df, 11)
        assert column_has_type(df, "Timestamp", "timestamp")
        assert column_has_type(df, "Amount Received", "double")
        assert has_payment_format(df, "Reinvestment")
    finally:
        spark.stop()


def test_invalid_transaction_dataset():
    spark = create_spark_session("invalid-transaction-test")
    try:
        df = load_transactions(spark, str(DATA_DIR / "transactions_invalid.csv"))

        assert not has_expected_column_count(df, 11)
        assert not column_has_type(df, "Timestamp", "timestamp")
        assert not has_payment_format(df, "Reinvestment")
    finally:
        spark.stop()
