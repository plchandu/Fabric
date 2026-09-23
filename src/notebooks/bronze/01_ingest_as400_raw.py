"""
# -------------------------------------------------------------------------------------------------
# Notebook: 01_ingest_as400_raw
# Layer: Bronze (Raw Landing / Immutable Storage)
# Target Lakehouse: lh_ips_bronze
# Description: Ingests raw JD Edwards AS400 DB2 tables via On-Premises Data Gateway into Bronze
#              Delta Lake tables with append-only watermarking, ingestion timestamps, and source lineage.
# -------------------------------------------------------------------------------------------------
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, input_file_name
import sys

# Initialize Spark session
spark = SparkSession.builder.appName("IPS_Bronze_AS400_Ingestion").getOrCreate()

def ingest_as400_table(source_path: str, table_name: str, lakehouse_table: str):
    """
    Ingests raw ERP CSV/Parquet files from Gateway landing into Bronze Delta table.
    Enforces immutable append-only storage with audit metadata columns.
    """
    print(f"--> Ingesting raw table: {table_name} into Bronze: {lakehouse_table}")
    
    # Read raw landing data
    raw_df = spark.read.option("header", "true") \
                       .option("inferSchema", "false") \
                       .csv(source_path)
    
    # Append ingestion audit metadata
    bronze_df = raw_df.withColumn("_ingestion_timestamp", current_timestamp()) \
                      .withColumn("_source_system", lit("JDE_AS400_DB2")) \
                      .withColumn("_source_file", input_file_name())
    
    # Write to Bronze Delta Table (Append mode)
    bronze_df.write \
             .format("delta") \
             .mode("append") \
             .option("mergeSchema", "true") \
             .saveAsTable(f"lh_ips_bronze.{lakehouse_table}")
             
    count = bronze_df.count()
    print(f"Successfully loaded {count} records into lh_ips_bronze.{lakehouse_table}")
    return count

if __name__ == "__main__":
    # Standard ERP Ingestion Catalog
    as400_tables = [
        {"file": "CRPOTA.F0911_GL_Ledger.csv", "table": "raw_f0911_gl_ledger"},
        {"file": "CRPOTA.F0901_Account_Master.csv", "table": "raw_f0901_account_master"},
        {"file": "CRPOTA.F0010_Company_Constants.csv", "table": "raw_f0010_company_constants"},
        {"file": "CRPOTA.F03B11_AR_Ledger.csv", "table": "raw_f03b11_ar_ledger"},
        {"file": "CRPOTA.F0411_AP_Ledger.csv", "table": "raw_f0411_ap_ledger"},
        {"file": "CRPOTA.F1201_Asset_Master.csv", "table": "raw_f1201_asset_master"},
        {"file": "CRPCTL.F0015_Currency_Exchange_Rates.csv", "table": "raw_f0015_currency_rates"}
    ]
    
    base_landing_path = "Files/Landing/AS400/"
    for item in as400_tables:
        source = f"{base_landing_path}{item['file']}"
        try:
            ingest_as400_table(source, item['file'], item['table'])
        except Exception as e:
            print(f"Warning/Error loading {item['file']}: {e}", file=sys.stderr)
