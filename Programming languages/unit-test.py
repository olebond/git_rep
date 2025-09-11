import unittest
from spark_app import (
    create_spark_session,
    get_column_count,
    check_amount_received_is_float,
    check_timestamp_format,
    check_payment_format_valid,
    load_data,
    has_payment_format,
)

VALID_CSV_LOCAL_PATH = "test/fixtures/transactions_valid_local.csv"
INVALID_CSV_LOCAL_PATH = "test/fixtures/transactions_invalid_local.csv"
EMPTY_CSV_PATH = "test/fixtures/transactions_empty.csv"

class BaseSparkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = create_spark_session("SparkUnitTestAppTests")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()


class TestColumnCount(BaseSparkTest):
    def test_valid_csv_column_count(self):
        df = load_data(self.spark, VALID_CSV_LOCAL_PATH)
        self.assertTrue(get_column_count(df, 11))

    def test_invalid_csv_column_count(self):
        df = load_data(self.spark, INVALID_CSV_LOCAL_PATH)
        self.assertFalse(get_column_count(df, 11))

    def test_empty_csv_column_count(self):
        df = load_data(self.spark, EMPTY_CSV_PATH)
        self.assertFalse(get_column_count(df, 11))


class TestAmountReceivedType(BaseSparkTest):
    def test_valid_amount_received(self):
        df = load_data(self.spark, VALID_CSV_LOCAL_PATH)
        self.assertTrue(check_amount_received_is_float(df))

    def test_invalid_amount_received(self):
        df = load_data(self.spark, INVALID_CSV_LOCAL_PATH)
        self.assertFalse(check_amount_received_is_float(df))

    def test_empty_amount_received(self):
        df = load_data(self.spark, EMPTY_CSV_PATH)
        self.assertFalse(check_amount_received_is_float(df))


class TestTimestampFormat(BaseSparkTest):
    def test_valid_timestamp_format(self):
        df = load_data(self.spark, VALID_CSV_LOCAL_PATH)
        self.assertTrue(check_timestamp_format(df))

    def test_invalid_timestamp_format(self):
        df = load_data(self.spark, INVALID_CSV_LOCAL_PATH)
        self.assertFalse(check_timestamp_format(df))

    def test_empty_timestamp_format(self):
        df = load_data(self.spark, EMPTY_CSV_PATH)
        self.assertFalse(check_timestamp_format(df))


class TestPaymentFormat(BaseSparkTest):
    def test_valid_payment_format(self):
        df = load_data(self.spark, VALID_CSV_LOCAL_PATH)
        self.assertTrue(has_payment_format(df, "Cheque"))

    def test_invalid_payment_format(self):
        df = load_data(self.spark, INVALID_CSV_LOCAL_PATH)
        self.assertFalse(has_payment_format(df, "Reinvestment"))

    def test_empty_payment_format(self):
        df = load_data(self.spark, EMPTY_CSV_PATH)
        self.assertFalse(has_payment_format(df, "Reinvestment"))


if __name__ == "__main__":
    unittest.main(verbosity=2)