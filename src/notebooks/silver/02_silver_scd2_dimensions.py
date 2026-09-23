"""
# -------------------------------------------------------------------------------------------------
# Notebook: 02_silver_scd2_dimensions
# Layer: Silver (Slowly Changing Dimension Type 2)
# Target Lakehouse: lh_ips_silver
# Description: Implements SCD Type 2 dimension historical tracking using Delta Lake MERGE for
#              Account Master (Chart of Accounts) and Customer Master. Maintains valid_from,
#              valid_to, and is_current flags to preserve historical financial reporting accuracy.
# -------------------------------------------------------------------------------------------------
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sha2, concat_ws, lit, current_timestamp
from delta.tables import DeltaTable

spark = SparkSession.builder.appName("IPS_Silver_SCD2_Dimensions").getOrCreate()

def process_scd2_account_master():
    """
    Applies Slowly Changing Dimension Type 2 logic on F0901 Account Master.
    Tracks changes to account description, posting edit codes, and financial category codes.
    """
    print("--> Processing SCD Type 2 for Account Master (F0901)...")
    
    # 1. Read Bronze staged updates
    bronze_accounts = spark.table("lh_ips_bronze.raw_f0901_account_master")
    
    # Calculate hash of tracked attributes to detect changes
    incoming_df = bronze_accounts.select(
        col("GMAID").alias("account_id"),
        col("GMCO").alias("company_code"),
        col("GMMCU").alias("business_unit"),
        col("GMOBJ").alias("object_account"),
        col("GMSUB").alias("sub_ledger"),
        col("GMDL01").alias("account_description"),
        col("GMPEC").alias("posting_edit_code"),
        col("GMC01").alias("category_code_01")
    ).withColumn(
        "record_hash",
        sha2(concat_ws("||", col("account_description"), col("posting_edit_code"), col("category_code_01")), 256)
    )
    
    silver_target_table = "lh_ips_silver.dim_account_scd2"
    
    # Check if target table exists, if not initialize it
    if not spark.catalog.tableExists(silver_target_table):
        print("Initializing new SCD2 Dim Account table...")
        initial_df = incoming_df.withColumn("valid_from", current_timestamp()) \
                                .withColumn("valid_to", lit(None).cast("timestamp")) \
                                .withColumn("is_current", lit(True))
        initial_df.write.format("delta").mode("overwrite").saveAsTable(silver_target_table)
        return
        
    target_delta = DeltaTable.forName(spark, silver_target_table)
    
    # Step 2.1: Find existing current rows that have changed
    join_condition = (col("target.account_id") == col("source.account_id")) & (col("target.is_current") == lit(True))
    
    # Step 2.2: Perform SCD2 Merge
    # Rows with matching account_id and different hash are closed (is_current = false, valid_to = now)
    # New rows and changed rows are inserted as is_current = true
    merge_df = incoming_df.alias("source").join(
        target_delta.toDF().filter(col("is_current") == lit(True)).alias("target"),
        on="account_id",
        how="left"
    ).select(
        col("source.*"),
        col("target.record_hash").alias("target_record_hash"),
        col("target.account_id").alias("target_account_id")
    )
    
    # Records requiring insert (brand new or updated attributes)
    records_to_insert = merge_df.filter(
        col("target_account_id").isNull() | (col("record_hash") != col("target_record_hash"))
    ).withColumn("valid_from", current_timestamp()) \
     .withColumn("valid_to", lit(None).cast("timestamp")) \
     .withColumn("is_current", lit(True))
     
    # Update expired records in target
    target_delta.alias("t").merge(
        incoming_df.alias("s"),
        "t.account_id = s.account_id AND t.is_current = true AND t.record_hash != s.record_hash"
    ).whenMatchedUpdate(set={
        "is_current": lit(False),
        "valid_to": current_timestamp()
    }).execute()
    
    # Insert new active versions
    records_to_insert.drop("target_record_hash", "target_account_id") \
                     .write \
                     .format("delta") \
                     .mode("append") \
                     .saveAsTable(silver_target_table)
                     
    print("SCD Type 2 processing complete for Account Master.")

if __name__ == "__main__":
    process_scd2_account_master()
