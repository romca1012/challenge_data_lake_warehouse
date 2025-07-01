from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import from_json, col

from utils.schema import get_data_schema

from config.config import configuration


def main(kafka_topic: str, topic_key: str):
    
    spark =     SparkSession \
                .builder.appName(f"{topic_key}Streaming") \
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
                .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0") \
                .getOrCreate()

    # Adjust the log level to minimize the console output on executors
    spark.sparkContext.setLogLevel('WARN')

    def read_kafka_topic(topic, schema):
        return (
            spark.readStream
            .format('kafka')
            .option('kafka.bootstrap.servers', 'localhost:9092')
            .option('subscribe', topic)
            .option('startingOffsets', 'earliest')
            .load()
            .selectExpr('CAST(value AS STRING)')
            .select(from_json(col('value'), schema).alias('data'))
            .select('data.*')
            .withWatermark('timestamp', '2 minutes')
        )
    

    def streamWriter(input: DataFrame, checkpointFolder, output):
        return (
            input.writeStream
            .format('parquet')
            .option('checkpointLocation', checkpointFolder)
            .option('path', output)
            .outputMode('append')
            .start()
        )
    
    dataSchema = get_data_schema(kafka_topic)
    dataFrame = read_kafka_topic(kafka_topic, dataSchema).alias(topic_key)
    
    query = streamWriter(
        dataFrame,
        f's3a://sparkstreamingdata/checkpoints/{kafka_topic}',
        f's3a://sparkstreamingdata/data/{kafka_topic}'
    )
    
    query.awaitTermination()

if __name__ == "__main__":
    
    kafka_topic = os.getenv('KAFKA_TOPIC')
    topic_key = os.getenv('TOPIC_KEY')
    
    main(kafka_topic, topic_key)