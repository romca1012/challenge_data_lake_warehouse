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
        return (spark.readStream
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
        return (input.writeStream
                .format('parquet')
                .option('checkpointLocation', checkpointFolder)
                .option('path', output)
                .outputMode('append')
                .start())
    
    
    vehicleDF = read_kafka_topic('vehicle_data', get_data_schema('vehicle_data')).alias('vehicle')
    gpsDF = read_kafka_topic('gps_data', get_data_schema('gps_data')).alias('gps')
    trafficDF = read_kafka_topic('traffic_data', get_data_schema('traffic_data')).alias('traffic')
    weatherDF = read_kafka_topic('weather_data', get_data_schema('weather_data')).alias('weather')
    emergencyDF = read_kafka_topic('emergency_data', get_data_schema('emergency_data')).alias('emergency')


    query1 = streamWriter(vehicleDF, 's3a://sparkstreamingdata/checkpoints/vehicle_data',
                 's3a://sparkstreamingdata/data/vehicle_data')
    query2 = streamWriter(gpsDF, 's3a://sparkstreamingdata/checkpoints/gps_data',
                 's3a://sparkstreamingdata/data/gps_data')
    query3 = streamWriter(trafficDF, 's3a://sparkstreamingdata/checkpoints/traffic_data',
                 's3a://sparkstreamingdata/data/traffic_data')
    query4 = streamWriter(weatherDF, 's3a://sparkstreamingdata/checkpoints/weather_data',
                 's3a://sparkstreamingdata/data/weather_data')
    query5 = streamWriter(emergencyDF, 's3a://sparkstreamingdata/checkpoints/emergency_data',
                 's3a://sparkstreamingdata/data/emergency_data')

    

    query5.awaitTermination()

if __name__ == "__main__":
    main()