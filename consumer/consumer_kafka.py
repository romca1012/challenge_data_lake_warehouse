import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import from_json, col
import os

from utils.schema import get_data_schema
from config.config import configuration

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
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel('WARN')

    def read_kafka_topic(topic, schema):
        logger.info(f"Reading Kafka topic: {topic} with provided schema")
        df = (
            spark.readStream
            .format('kafka')
            .option('kafka.bootstrap.servers', 'broker:29092')
            .option('subscribe', topic)
            .option('startingOffsets', 'earliest')
            .load()
            .selectExpr('CAST(value AS STRING)')
            .select(from_json(col('value'), schema).alias('data'))
            .select('data.*')
            .withWatermark('timestamp', '2 minutes')
        )
        logger.info("Kafka topic read setup complete")
        return df

    def streamWriter(input: DataFrame, checkpointFolder, output):
        logger.info(f"Starting stream writer with checkpoint at {checkpointFolder} and output path {output}")
        query = (
            input.writeStream
            .format('parquet')
            .option('checkpointLocation', checkpointFolder)
            .option('path', output)
            .outputMode('append')
            .start()
        )
        logger.info("Stream writer started")
        return query

    try:
        dataSchema = get_data_schema(kafka_topic)
        logger.info("Data schema retrieved successfully")

        dataFrame = read_kafka_topic(kafka_topic, dataSchema).alias(topic_key)

        raw_path = os.getenv('RAW_PATH')
        target_table_path = f"{raw_path}{topic_key}"

        query = streamWriter(
            input=dataFrame,
            checkpointFolder=f'{raw_path}/checkpoints/{topic_key}',
            output=f'{target_table_path}'
        )

        logger.info("Streaming query started. Awaiting termination...")
        query.awaitTermination()
    except Exception as e:
        logger.error(f"Error during streaming: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    kafka_topic = os.getenv('KAFKA_TOPIC')
    topic_key = os.getenv('TOPIC_KEY')

    logger.info("Application launched")
    main(kafka_topic, topic_key)
