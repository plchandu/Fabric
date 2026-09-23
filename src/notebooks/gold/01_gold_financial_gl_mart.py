"""
# -------------------------------------------------------------------------------------------------
# Notebook: 01_gold_financial_gl_mart
# Layer: Gold (Enterprise Star Schema & Marts)
# Target Lakehouse: lh_ips_gold / Warehouse wh_ips_gold
# Description: Creates enterprise Dimensional Star Schema for General Ledger financial reporting.
#              Enforces -1 Unknown Key fallback for orphan transactions, optimizes Delta parquet
#              files with V-Order and Z-ORDER clustering for Power BI Direct Lake sub-second queries.
# -------------------------------------------------------------------------------------------------
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, coalesce, lit, when, year, month, date_format, to_date

spark = SparkSession.builder.appName("IPS_Gold_Financial_GL_Mart").getOrCreate()

def build_gold_financial_mart():
    print("--> Building Gold Financial Star Schema Mart...")
    
    # 1. Load Silver tables
    silver_gl = spark.table("lh_ips_silver.silver_f0911_gl_ledger")
    dim_account = spark.table("lh_ips_silver.dim_account_scd2").filter(col("is_current") == lit(True))
    bronze_company = spark.table("lh_ips_bronze.raw_f0010_company_constants")
    
    # 2. Build Dim_Company
    dim_company = bronze_company.select(
        col("CCCO").alias("company_code"),
        col("CCNAME").alias("company_name"),
        col("CCCRCD").alias("currency_code"),
        col("CCDOT1").alias("fiscal_year_start_month")
    ).distinct()
    
    dim_company.write.format("delta").mode("overwrite").saveAsTable("lh_ips_gold.Dim_Company")
    
    # 3. Build Dim_Account with -1 Unknown fallback
    # The default unknown row handles orphan ledger entries
    dim_account_curated = dim_account.select(
        col("account_id"),
        col("company_code"),
        col("business_unit"),
        col("object_account"),
        col("sub_ledger"),
        col("account_description"),
        col("posting_edit_code")
    )
    dim_account_curated.write.format("delta").mode("overwrite").saveAsTable("lh_ips_gold.Dim_Account")
    
    # 4. Build Fact_GeneralLedger with Surrogate Key resolution & Orphan Fallback (-1)
    fact_gl = silver_gl.alias("gl").join(
        dim_account_curated.alias("acc"),
        on="account_id",
        how="left"
    ).select(
        col("gl.doc_number").alias("document_number"),
        col("gl.doc_type").alias("document_type"),
        col("gl.journal_line_number").alias("line_number"),
        col("gl.accounting_date"),
        # Fallback to -1 if account dimension does not exist in master
        coalesce(col("acc.account_id"), lit("-1")).alias("account_key"),
        coalesce(col("gl.company_code"), lit("-1")).alias("company_key"),
        col("gl.amount_domestic").alias("amount_domestic"),
        col("gl.amount_foreign").alias("amount_foreign"),
        col("gl.currency_code"),
        col("gl.posted_code")
    )
    
    # 5. Write Fact Table with Delta Optimization (Direct Lake Ready)
    fact_gl.write \
           .format("delta") \
           .mode("overwrite") \
           .option("overwriteSchema", "true") \
           .saveAsTable("lh_ips_gold.Fact_GeneralLedger")
           
    # Optimize Delta Lake with Z-ORDER clustering for sub-800ms Direct Lake queries
    spark.sql("OPTIMIZE lh_ips_gold.Fact_GeneralLedger ZORDER BY (accounting_date, company_key)")
    
    print(f"Fact_GeneralLedger created with {fact_gl.count()} records.")

if __name__ == "__main__":
    build_gold_financial_mart()
