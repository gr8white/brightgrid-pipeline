from pyspark.sql.functions import col, current_timestamp

VOLUME_PATH = "/Volumes/brightgrid/bronze/raw_readings"
CHECKPOINT = "/Volumes/brightgrid/bronze/checkpoints/ingest_readings"
TARGET_TABLE = "brightgrid.bronze.meter_readings"

FORMAT = "json"
SCHEMA_HINTS = "reading_kwh FLOAT, voltage FLOAT"

stream = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", FORMAT)
    .option("cloudFiles.schemaHints", SCHEMA_HINTS)
    .option("cloudFiles.schemaLocation", CHECKPOINT + "/schema")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.maxFilesPerTrigger", "1")
    .load(VOLUME_PATH)
    .withColumn("_source_file", col("_metadata.file_path"))
    .withColumn("_ingested_at", current_timestamp())
)

(
    stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT)
    .option("mergeSchema", "true")
    .trigger(availableNow=True)
    .toTable(TARGET_TABLE)
)