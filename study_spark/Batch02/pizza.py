from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql import Window
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

#total_cali_ckn = filtered.agg(F.sum("quantity").alias("total_cali_ckn")).collect()[0]["total_cali_ckn"]

filtered.agg(F.sum("quantity")).show(truncate=False)

ingredients = joined.filter(
    (joined["date"] == "2015-01-02") &
    (joined["time"] == "18:27:50")
)
ingredients.select("ingredients").show(truncate=False)

ingredients_exploded = ingredients.withColumn(
    "ingredient",
    F.explode(F.split(F.col("ingredients"), ","))
)
ingredient_counts = ingredients_exploded.groupBy("ingredient") \
    .agg(F.sum("quantity").alias("total_quantity")) \
    .orderBy(F.desc("total_quantity"))
ingredient_counts.show(truncate=False)

mostsold = joined.filter((F.col("date") >= "2015-01-01") & (F.col("date") <= "2015-01-08"))

sold_rank = mostsold.groupBy("category") \
    .agg(F.sum("quantity").alias("total_sold"))

w = Window.orderBy(F.desc("total_sold"))
most_sold_rank = sold_rank.withColumn("rank", F.rank().over(w))
most_sold_rank.filter(F.col("rank") <= 2).show(truncate=False)

most_sold_category = mostsold.groupBy("category") \
    .agg(F.sum("quantity").alias("total_sold")) \
    .orderBy(F.desc("total_sold")) \
    .limit(1)
    
most_sold_category.show(truncate=False)

spark.stop()