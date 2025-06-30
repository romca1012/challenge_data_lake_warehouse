from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, DoubleType

def get_data_schema(topic_name: str):
    
    schemas = {
        'vehicle_data': StructType([
            StructField("id", StringType(), True),
            StructField("vehicle_id", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("location", StringType(), True),
            StructField("speed", DoubleType(), True),
            StructField("direction", StringType(), True),
            StructField("make", StringType(), True),
            StructField("model", StringType(), True),
            StructField("year", IntegerType(), True),
            StructField("fuelType", StringType(), True),
        ]),

        # gpsSchema
        "gps_data": StructType([
            StructField("id", StringType(), True),
            StructField("vehicle_id", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("speed", DoubleType(), True),
            StructField("direction", StringType(), True),
            StructField("vehicleType", StringType(), True)
        ]),
            
        # trafficSchema
        "traffic_data": StructType([
            StructField("id", StringType(), True),
            StructField("vehicle_id", StringType(), True),
            StructField("camera_id", StringType(), True),
            StructField("location", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("snapshot", StringType(), True)
        ]),

        # weatherSchema
        "weather_data": StructType([
            StructField("id", StringType(), True),
            StructField("vehicle_id", StringType(), True),
            StructField("location", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("temperature", DoubleType(), True),
            StructField("weatherCondition", StringType(), True),
            StructField("precipitation", DoubleType(), True),
            StructField("windSpeed", DoubleType(), True),
            StructField("humidity", IntegerType(), True),
            StructField("airQualityIndex", DoubleType(), True),
        ]),

        # emergencySchema
        "emergency_data": StructType([
            StructField("id", StringType(), True),
            StructField("vehicle_id", StringType(), True),
            StructField("incidentId", StringType(), True),
            StructField("type", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("location", StringType(), True),
            StructField("status", StringType(), True),
            StructField("description", StringType(), True),
        ])
    }
    return schemas.get(topic_name, schemas)