from pyspark.sql import SparkSession
from pyspark.sql.functions import col, hour, dayofweek, month, unix_timestamp, round
import os

def main():
    # 1. Configuration de la SparkSession
    # On spécifie le chemin local vers le driver JAR car le container n'a pas accès à internet
    jar_path = "/opt/airflow/scripts/postgresql-42.5.0.jar"
    
    spark = SparkSession.builder \
        .appName("SmartLogiTrack-Silver-Transformation") \
        .config("spark.jars", jar_path) \
        .config("spark.driver.extraClassPath", jar_path) \
        .getOrCreate()

    print("Début de la transformation Silver (Mode Local JAR)...")

    # 2. Chargement des données Bronze
    bronze_path = "data/bronze_taxi.parquet"
    if not os.path.exists(bronze_path):
        # On essaie le chemin absolu dans le container si le relatif échoue
        bronze_path = "/opt/airflow/data/bronze_taxi.parquet"
        
    df = spark.read.parquet(bronze_path)

    # 3. Nettoyage et Filtrage
    print("Nettoyage des données...")
    df_filtered = df.filter(
        (col("trip_distance") > 0) & (col("trip_distance") <= 200) &
        (col("passenger_count") > 0) &
        (unix_timestamp(col("tpep_dropoff_datetime")) > unix_timestamp(col("tpep_pickup_datetime")))
    )

    # 4. Feature Engineering
    print("Engineering des caractéristiques...")
    df_silver = df_filtered.withColumn("pickup_hour", hour(col("tpep_pickup_datetime"))) \
                           .withColumn("day_of_week", dayofweek(col("tpep_pickup_datetime"))) \
                           .withColumn("month", month(col("tpep_pickup_datetime"))) \
                           .withColumn("duration_minutes", 
                                       round((unix_timestamp(col("tpep_dropoff_datetime")) - 
                                              unix_timestamp(col("tpep_pickup_datetime"))) / 60, 2))

    # 5. Écriture vers PostgreSQL (Zone Silver)
    jdbc_url = "jdbc:postgresql://postgres:5432/airflow"
    db_properties = {
        "user": "airflow",
        "password": "airflow",
        "driver": "org.postgresql.Driver"
    }

    print("Chargement vers la base de données Postgres (table silver_taxi_trips)...")
    df_silver.write.format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "silver_taxi_trips") \
        .option("user", db_properties["user"]) \
        .option("password", db_properties["password"]) \
        .option("driver", db_properties["driver"]) \
        .mode("overwrite") \
        .save()

    print("Transformation terminée et données chargées dans la table silver_taxi_trips.")
    spark.stop()

if __name__ == "__main__":
    main()
