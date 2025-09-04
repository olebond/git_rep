from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

spark = SparkSession.builder \
    .appName("Disease Symptom Analysis") \
    .master("local[1]") \
    .getOrCreate()

schema = StructType([
    StructField("Disease", StringType(), True),
    StructField("Fever", StringType(), True),
    StructField("Cough", StringType(), True),
    StructField("Fatigue", StringType(), True),
    StructField("Difficulty Breathing", StringType(), True),
    StructField("Age", IntegerType(), True),
    StructField("Gender", StringType(), True),
    StructField("Blood Pressure", StringType(), True),
    StructField("Cholesterol Level", StringType(), True),
    StructField("Outcome Variable", StringType(), True)
])

file_path = "/Users/admin/Desktop/git_rep/study_spark/Disease_symptom_and_patient_profile_dataset.csv"
df = spark.read.option("header", True).schema(schema).csv(file_path)

asthma_30_male = df.filter(
    (F.col("Disease") == "Asthma") &
    (F.col("Age") == 30) &
    (F.col("Gender") == "Male")
)
count_asthma_30_male = asthma_30_male.count()
print(f"1. Number of 30-year-old males with Asthma: {count_asthma_30_male}")

hyperthyroid_female_no_fever = df.filter(
    (F.col("Disease") == "Hyperthyroidism") &
    (F.col("Gender") == "Female") &
    (F.col("Fever") == "No")
)
count_hyperthyroid_female_no_fever = hyperthyroid_female_no_fever.count()
print(f"2. Number of females with Hyperthyroidism and No Fever: {count_hyperthyroid_female_no_fever}")

sinusitis_cough_fatigue = df.filter(
    (F.col("Disease") == "Sinusitis") &
    (F.col("Cough") == "Yes") &
    (F.col("Fatigue") == "Yes")
).groupBy("Gender").agg(F.count("*").alias("count"))

predominant = sinusitis_cough_fatigue.collect()
print("3. Sinusitis with Cough and Fatigue is more common in:")
for row in predominant:
    print(f"  {row['Gender']}: {row['count']}")

spark.stop()
