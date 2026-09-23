"""
# -------------------------------------------------------------------------------------------------
# Notebook: 01_silver_cleansing_dq
# Layer: Silver (Conformed & Cleansed)
# Target Lakehouse: lh_ips_silver
# Description: Cleanses Bronze data, converts AS400 Julian dates (CYYDDD) to standard ISO dates,
#              evaluates enterprise Data Quality (DQ) rules, tags quarantined records, and computes
#              standardized transaction amounts.
# -------------------------------------------------------------------------------------------------
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, lit, to_date, expr, current_timestamp, coalesce, concat, lpad
)
from pyspark.sql.types import DateType

spark = SparkSession.builder.appName("IPS_Silver_Cleansing_DQ").getOrCreate()

def convert_julian_to_gregorian(julian_col):
    """
    Converts JD Edwards 6-digit Julian Date (CYYDDD) to standard Date.
    Formula:
      - C = Century flag: 0 = 1900s, 1 = 2000s, 2 = 2100s
      - YY = 2-digit Year
      - DDD = Day of Year (001 - 366)
      Full Year = 1900 + (C * 100) + YY
    """
    century = (julian_col / 100000).cast("int")
    year_part = ((julian_col % 100000) / 1000).cast("int")
    day_of_year = (julian_col % 1000).cast("int")
    
    full_year = lit(1900) + (century * lit(100)) + year_part
    
    # Format as YYYY-01-01 and add (DDD - 1) days
    start_of_year = to_date(concat(full_year.cast("string"), lit("-01-01")), "yyyy-MM-dd")
    return expr(f"date_add({start_of_year}, {day_of_year} - 1)")

def process_silver_gl_ledger():
    """
    Cleanses General Ledger raw data (F0911), applies DQ rules, converts Julian dates,
    and isolates quarantined records into the Quarantine Delta Table.
    """
    print("--> Processing Silver GL Ledger (F0911)...")
    
    bronze_df = spark.table("lh_ips_bronze.raw_f0911_gl_ledger")
    
    # 1. Standardize types and convert Julian dates
    cleaned_df = bronze_df.select(
        col("GLKCO").alias("company_key"),
        col("GLDCT").alias("doc_type"),
        col("GLDOC").cast("long").alias("doc_number"),
        col("GLJELN").cast("int").alias("journal_line_number"),
        col("GLPOST").alias("posted_code"),
        col("GLANI").alias("account_number"),
        (col("GLAA").cast("double") / 100.0).alias("amount_domestic"),
        (col("GLACR").cast("double") / 100.0).alias("amount_foreign"),
        col("GLCRCD").alias("currency_code"),
        col("GLCRRM").alias("currency_mode"), # D = Domestic, F = Foreign
        col("GLDGJ").cast("long").alias("gl_julian_date"),
        col("GLDICJ").cast("long").alias("batch_julian_date"),
        col("GLCO").alias("company_code"),
        col("GLMCU").alias("business_unit"),
        col("GLOBJ").alias("object_account"),
        col("GLSUB").alias("sub_ledger"),
        col("GLCRCD").alias("txn_currency")
    )
    
    # 2. Add converted calendar dates
    with_dates_df = cleaned_df.withColumn(
        "accounting_date",
        when(col("gl_julian_date") > 0, convert_julian_to_gregorian(col("gl_julian_date")))
        .otherwise(lit(None).cast(DateType()))
    )
    
    # 3. Data Quality Engine & Quarantine Rules
    # Rule 1: Account number must not be null/empty
    # Rule 2: Accounting date must be valid and between 2000-01-01 and 2030-12-31
    # Rule 3: Amount must not be NaN
    dq_evaluated_df = with_dates_df.withColumn(
        "dq_status",
        when(col("account_number").isNull() | (col("account_number") == ""), lit("QUARANTINE_NULL_ACCOUNT"))
        .when(col("accounting_date").isNull(), lit("QUARANTINE_INVALID_DATE"))
        .when((col("accounting_date") < "2000-01-01") | (col("accounting_date") > "2030-12-31"), lit("QUARANTINE_OUT_OF_BOUNDS_DATE"))
        .when(col("amount_domestic").isNull(), lit("QUARANTINE_NULL_AMOUNT"))
        .otherwise(lit("PASSED"))
    ).withColumn("_silver_processed_at", current_timestamp())
    
    # 4. Split into Valid Silver records and Quarantined records
    silver_valid_df = dq_evaluated_df.filter(col("dq_status") == "PASSED")
    quarantine_df = dq_evaluated_df.filter(col("dq_status") != "PASSED")
    
    # 5. Write Silver Delta Table
    silver_valid_df.write \
                   .format("delta") \
                   .mode("overwrite") \
                   .option("overwriteSchema", "true") \
                   .saveAsTable("lh_ips_silver.silver_f0911_gl_ledger")
                   
    # 6. Write Quarantine Delta Table for DQ remediation alerts
    quarantine_df.write \
                 .format("delta") \
                 .mode("append") \
                 .saveAsTable("lh_ips_silver.silver_quarantine_records")
                 
    print(f"Silver Valid Records: {silver_valid_df.count()} | Quarantined Records: {quarantine_df.count()}")

if __name__ == "__main__":
    process_silver_gl_ledger()
