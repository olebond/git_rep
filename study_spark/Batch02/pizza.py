from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

spark = SparkSession.builder \
    .appName("PizzaOrders") \
    .master("local[*]") \
    .getOrCreate()

orders_schema = StructType([
    StructField("order_id", IntegerType(), True),
    StructField("date", StringType(), True),
    StructField("time", StringType(), True)
])

order_details_schema = StructType([
    StructField("order_details_id", IntegerType(), True),
    StructField("order_id", IntegerType(), True),
    StructField("pizza_id", StringType(), True),
    StructField("quantity", IntegerType(), True)
])

pizzas_schema = StructType([
    StructField("pizza_id", StringType(), True),
    StructField("pizza_type_id", StringType(), True),
    StructField("size", StringType(), True),
    StructField("price", FloatType(), True)
])

pizza_types_schema = StructType([
    StructField("pizza_type_id", StringType(), True),
    StructField("name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("ingredients", StringType(), True)
])

orders = spark.read.csv("study_spark/Batch02/orders.csv", header=True, schema=orders_schema)
order_details = spark.read.csv("study_spark/Batch02/order_details.csv", header=True, schema=order_details_schema)
pizzas = spark.read.csv("study_spark/Batch02/pizzas.csv", header=True, schema=pizzas_schema)
pizza_types = spark.read.csv("study_spark/Batch02/pizza_types.csv", header=True, schema=pizza_types_schema)

joined = order_details.join(orders, "order_id") \
                     .join(pizzas, "pizza_id") \
                     .join(pizza_types, "pizza_type_id")

filtered = joined.filter(
    (joined["pizza_type_id"] == "cali_ckn") &
    (joined["date"] == "2015-01-04")
)

total_cali_ckn = filtered.agg(F.sum("quantity").alias("total_cali_ckn")).collect()[0]["total_cali_ckn"]

filtered.agg(F.sum("quantity")).show()

ingredients = joined.filter(
    (joined["date"] == "2015-01-02") &
    (joined["time"] == "18:27:50")
)
ingredients.select("ingredients").show(truncate=False)

spark.stop()