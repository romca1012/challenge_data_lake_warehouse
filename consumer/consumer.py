from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import from_json, col

from utils.schema import get_data_schema

from config.config import configuration


def main():
    spark = SparkSession.builder.appName("SmartCityStreaming") \
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
                "org.apache.hadoop:hadoop-aws:3.3.1,"
                "com.amazonaws:aws-java-sdk:1.11.469") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.access.key", configuration.get('AWS_ACCESS_KEY')) \
        .config("spark.hadoop.fs.s3a.secret.key", configuration.get('AWS_SECRET_KEY')) \
        .config('spark.hadoop.fs.s3a.aws.credentials.provider',
                'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider') \
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
    
    
    kafka_topic = os.getenv('KAFKA_TOPIC')
    topic_key = os.getenv('TOPIC_KEY')
    
    dataSchema = get_data_schema(kafka_topic)
    dataFrame = read_kafka_topic(kafka_topic, dataSchema).alias(topic_key)
    
    query = streamWriter(
        dataFrame,
        f's3a://sparkstreamingdata/checkpoints/{kafka_topic}',
        f's3a://sparkstreamingdata/data/{kafka_topic}'
    )
    
    query.awaitTermination()

if __name__ == "__main__":
    main()