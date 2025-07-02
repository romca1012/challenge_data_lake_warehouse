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

    spark = (
        SparkSession
        .builder.appName(f"{topic_key}Streaming")
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

    def write_to_postgres(input_df: DataFrame, table_name: str):
        """Écrit le streaming dans une table PostgreSQL"""
        logger.info(f"Writing to PostgreSQL table: {table_name}")

        jdbc_url = os.getenv("POSTGRES_JDBC_URL") + "metastore"
        jdbc_properties = {
            "user": os.getenv("JDBC_USER"),
            "password": os.getenv("JDBC_PASSWORD"),
            "driver": "org.postgresql.Driver"
        }

        query = (
            input_df.writeStream
            .outputMode("append")
            .foreachBatch(lambda df, epochId: df.write
                          .mode("append")
                          .jdbc(url=jdbc_url, table=table_name, properties=jdbc_properties))
            .start()
        )
        return query

    try:
        raw_path = os.getenv('RAW_PATH')
        full_table_path = f"{raw_path}{topic_key}"

        streaming_df = read_delta_from_hdfs(full_table_path)

        query = write_to_postgres(streaming_df, topic_key)

        logger.info(f"Streaming to PostgreSQL for topic {topic_key} started successfully")
        query.awaitTermination()

    except Exception as e:
        logger.error(f"Error during PostgreSQL streaming: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    kafka_topic = os.getenv('KAFKA_TOPIC')
    topic_key = os.getenv('TOPIC_KEY')

    logger.info("Application launched")
    main(kafka_topic, topic_key)
