from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = SparkSession.builder \
    .appName("English Words") \
    .getOrCreate()

df = spark.read.text("study_spark/words.txt")

df_lower = df.withColumn("word_lower", F.lower(F.col("value")))
abs = df_lower.filter(F.col("word_lower").startswith("abs"))
count_abs = abs.count()
print(f'total count of words that start with abs is {count_abs}')

df_letter_o = df_lower.filter(
    (F.length("word_lower") >= 3) &
    (F.col("word_lower").substr(3, 1) == "o")
)
count_letter_o = df_letter_o.count()
print(f'total count of words that have the third letter o is {count_letter_o}')

df_s = df_lower.filter(F.col("word_lower").endswith("s"))
df_uou = df_s.withColumn(
    "changed_word",
    F.regexp_replace(F.col("word_lower"), "ou", "uou")
)
df_result = df_uou.filter(F.col("word_lower") != F.col("changed_word"))
df_result.select("changed_word").show(truncate=False)
