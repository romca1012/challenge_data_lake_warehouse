import logging
from pyspark.sql import SparkSession, DataFrame
import os
from utils.schema import get_data_schema

# --- Setup basique du logger ---
logger = logging.getLogger("spark_streaming_app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def main(kafka_topic: str, topic_key: str):
    logger.info(f"Starting Spark session for topic_key={topic_key}, kafka_topic={kafka_topic}")

    # Configuration optimisée pour Delta Lake, Hive et JDBC
    spark = (
        SparkSession
        .builder.appName(f"{topic_key}Streaming")
        .config("spark.hadoop.hive.exec.dynamic.partition", "true")
        .config("spark.hadoop.hive.exec.dynamic.partition.mode", "nonstrict")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.delta.logStore.class", "org.apache.spark.sql.delta.storage.HDFSLogStore")
        .enableHiveSupport()
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel('WARN')

    def read_delta_from_hdfs(full_table_path: str):
        """Lit les nouvelles données Delta depuis HDFS en streaming"""
        logger.info("Reading Delta tables from HDFS in streaming mode")
        
        df = (
            spark.readStream
            .format("delta")
            .load(full_table_path)
        )
        logger.info("Delta streaming source setup complete")
        return df

    def write_delta_to_hive_table(input_df: DataFrame, delta_path: str, table_name: str):
        """Écrit le streaming dans une table Delta enregistrée dans Hive Metastore"""
        logger.info(f"Writing to Delta table registered in Hive: {table_name}")
        
        # Création de la database si elle n'existe pas
        spark.sql(f"CREATE DATABASE IF NOT EXISTS process_data.db")
        
        # Configuration pour l'écriture Delta avec optimisations PowerBI
        query = (
            input_df.writeStream
            .outputMode("append")
            .format("delta")
            .option("checkpointLocation", f"/checkpoints/delta/{table_name}")
            .option("mergeSchema", "true")
            .option("path", f"{delta_path}{table_name}")
            .start()
        )
        
        # Enregistrement de la table dans Hive Metastore
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            USING DELTA
            LOCATION '{delta_path}{table_name}'
        """)
        
        logger.info(f"Delta streaming to Hive table {table_name} started")
        return query

    try:
        raw_path  = os.getenv('RAW_PATH')
        full_table_path = f"{raw_path}{topic_key}"
        delta_path = os.getenv('WAREHOUSE_DB_PATH')
        
        # Lecture depuis Delta Lake
        streaming_df = read_delta_from_hdfs(full_table_path)

        # Écriture vers Delta avec enregistrement Hive
        query = write_delta_to_hive_table(streaming_df, delta_path, topic_key)

        logger.info(f"Streaming Delta pipeline started successfully")
        
        query.awaitTermination()
    except Exception as e:
        logger.error(f"Error during Delta streaming: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    kafka_topic = os.getenv('KAFKA_TOPIC')
    topic_key = os.getenv('TOPIC_KEY')

    logger.info("Application launched")
    main(kafka_topic, topic_key)