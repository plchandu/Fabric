# IPS Corporation — Comprehensive Technical Interview Guide & Question Bank (Basic to Advanced)

> **Project:** Enterprise Data Platform Modernization (IBM AS400 DB2 ERP $\rightarrow$ Microsoft Fabric)  
> **Platform Scope:** Microsoft Fabric, OneLake, Delta Lake, PySpark, Data Factory, Direct Lake, Microsoft Purview  
> **Target Audience:** Candidates & Interviewers for Data Engineers, Analytics Engineers, Fabric Specialists & Architects  
> **Document Location:** `docs/additional_docs/IPS_Project_Interview_Questions_Basic_to_Advanced.md`  

---

## 📋 Table of Contents
1. [Overview & Interview Framework](#1-overview--interview-framework)
2. [Level 1: Foundational & Basic Questions (Concepts & Architecture)](#2-level-1-foundational--basic-questions-concepts--architecture)
   - [Q1.1: What is the Medallion Architecture, and what does each layer do in this project?](#q11-what-is-the-medallion-architecture-and-what-does-each-layer-do-in-this-project)
   - [Q1.2: What is Microsoft Fabric OneLake, and how does it differ from traditional ADLS Gen2 storage accounts?](#q12-what-is-microsoft-fabric-onelake-and-how-does-it-differ-from-traditional-adls-gen2-storage-accounts)
   - [Q1.3: What is Delta Lake format, and why is it used throughout the lakehouse instead of plain CSV or Parquet?](#q13-what-is-delta-lake-format-and-why-is-it-used-throughout-the-lakehouse-instead-of-plain-csv-or-parquet)
   - [Q1.4: What source ERP system is being modernized in this project, and what are its key challenges?](#q14-what-source-erp-system-is-being-modernized-in-this-project-and-what-are-its-key-challenges)
   - [Q1.5: What is Power BI Direct Lake mode, and how does it differ from Import and DirectQuery modes?](#q15-what-is-power-bi-direct-lake-mode-and-how-does-it-differ-from-import-and-directquery-modes)
3. [Level 2: Intermediate Questions (Engineering, Cleansing & Modeling)](#3-level-2-intermediate-questions-engineering-cleansing--modeling)
   - [Q2.1: How are JD Edwards 6-digit Julian dates (CYYDDD) converted to standard Gregorian dates in PySpark?](#q21-how-are-jd-edwards-6-digit-julian-dates-cyyddd-converted-to-standard-gregorian-dates-in-pyspark)
   - [Q2.2: How does the project handle currency decimal scaling for AS400 financial ledger amounts?](#q22-how-does-the-project-handle-currency-decimal-scaling-for-as400-financial-ledger-amounts)
   - [Q2.3: How does the Data Quality Quarantine Engine work in PySpark, and why doesn't it break pipeline execution?](#q23-how-does-the-data-quality-quarantine-engine-work-in-pyspark-and-why-doesnt-it-break-pipeline-execution)
   - [Q2.4: How is Slowly Changing Dimension Type 2 (SCD2) implemented for the Chart of Accounts (F0901)?](#q24-how-is-slowly-changing-dimension-type-2-scd2-implemented-for-the-chart-of-accounts-f0901)
   - [Q2.5: What is the "Unknown Member (-1 Fallback)" pattern, and how does it prevent orphan records in Gold facts?](#q25-what-is-the-unknown-member--1-fallback-pattern-and-how-does-it-prevent-orphan-records-in-gold-facts)
   - [Q2.6: How do you handle JDE's multi-company corporate parent fallback (Company 00000)?](#q26-how-do-you-handle-jdes-multi-company-corporate-parent-fallback-company-00000)
4. [Level 3: Advanced Questions (Orchestration, Performance, Security & Purview)](#4-level-3-advanced-questions-orchestration-performance-security--purview)
   - [Q3.1: Explain the architecture of the Metadata-Driven Ingestion Framework and its 4-schema separation.](#q31-explain-the-architecture-of-the-metadata-driven-ingestion-framework-and-its-4-schema-separation)
   - [Q3.2: What is the "Subtype Inheritance Pattern" in the metadata repository, and what problem does it solve?](#q32-what-is-the-subtype-inheritance-pattern-in-the-metadata-repository-and-what-problem-does-it-solve)
   - [Q3.3: How do you prevent "DirectQuery Fallback" in Power BI Direct Lake mode to guarantee sub-800ms SLAs?](#q33-how-do-you-prevent-directquery-fallback-in-power-bi-direct-lake-mode-to-guarantee-sub-800ms-slas)
   - [Q3.4: Why should enterprise reporting avoid the "Default Semantic Model" in favor of a "Custom Semantic Model"?](#q34-why-should-enterprise-reporting-avoid-the-default-semantic-model-in-favor-of-a-custom-semantic-model)
   - [Q3.5: How is hybrid network security configured for the On-Premises Data Gateway (OPDG) connecting to AS400?](#q35-how-is-hybrid-network-security-configured-for-the-on-premises-data-gateway-opdg-connecting-to-as400)
   - [Q3.6: How does Microsoft Purview integrate with Microsoft Fabric and AS400 DB2 for end-to-end lineage?](#q36-how-does-microsoft-purview-integrate-with-microsoft-fabric-and-as400-db2-for-end-to-end-lineage)
   - [Q3.7: How are Fabric Capacity Units (CUs) managed and smoothed to prevent throttling on F32/F64 SKUs?](#q37-how-are-fabric-capacity-units-cus-managed-and-smoothed-to-prevent-throttling-on-f32f64-skus)
5. [Scenario-Based Behavioral & Problem-Solving Questions](#5-scenario-based-behavioral--problem-solving-questions)

---

## 1. Overview & Interview Framework

This interview bank is based on the production architecture of the **IPS Corporation Modernization Platform**. It evaluates candidates across three primary competencies:
1. **Architectural Acumen:** Understanding cloud lakehouse trade-offs, Zero Trust security, and Kimball modeling.
2. **Coding & Data Engineering:** Hands-on PySpark development, Delta Lake operations, Julian conversions, and SCD2 tracking.
3. **Operational Rigor:** Metadata framework automation, capacity FinOps, Data Quality quarantine, and enterprise governance.

---

## 2. Level 1: Foundational & Basic Questions (Concepts & Architecture)

### Q1.1: What is the Medallion Architecture, and what does each layer do in this project?
* **What Interviewers Look For:** Clear understanding of data refinement tiers and separation of concerns.
* **Model Answer:**
  * In our project, data flows through three progressive layers in Microsoft Fabric OneLake:
    1. **Bronze Layer (`lh_ips_bronze`):** The raw landing zone. Ingests raw data from AS400 DB2 via Fabric Data Factory Copy activities in append-only mode. It preserves original source schemas and column names, enriching rows with technical audit columns (`_source_system`, `_source_file`, `_ingestion_timestamp`).
    2. **Silver Layer (`lh_ips_silver`):** The conformed, cleansed single source of truth. PySpark notebooks convert legacy JDE `CYYDDD` Julian dates to Gregorian calendar dates, divide unscaled currency amounts, apply deduplication, evaluate Data Quality rules, divert bad records into quarantine tables, and manage historical state via SCD Type 2 Delta merges.
    3. **Gold Layer (`lh_ips_gold` / `wh_ips_gold`):** The analytical consumption layer. Models data into Kimball Star Schema Facts (`Fact_GeneralLedger`, `Fact_AR_Ledger`) and Conformed Dimensions (`Dim_Account`, `Dim_Company`, `Dim_Date`) with surrogate keys and `-1` unknown member fallbacks. Optimized with Microsoft V-Order for Direct Lake reporting.

---

### Q1.2: What is Microsoft Fabric OneLake, and how does it differ from traditional ADLS Gen2 storage accounts?
* **What Interviewers Look For:** Knowledge of SaaS unified storage, zero-copy shortcuts, and workspace virtualization.
* **Model Answer:**
  * **OneLake** is a single, unified, logical data lake for the entire enterprise tenant—often referred to as the *"OneDrive for data"*.
  * Unlike managing dozens of disjointed ADLS Gen2 storage accounts with separate connection strings, firewall IP whitelists, and access keys:
    1. **Zero-Configuration Provisioning:** OneLake is automatically provisioned with the Fabric tenant. Every workspace automatically becomes a folder in OneLake.
    2. **OneLake Shortcuts:** Allows virtualizing external data (ADLS Gen2, AWS S3, Google Cloud) into a lakehouse without moving or copying physical files.
    3. **Unified Governance:** All workloads (Spark, SQL Endpoint, Power BI Direct Lake) point to the same physical Delta Parquet files in OneLake under unified Entra ID governance.

---

### Q1.3: What is Delta Lake format, and why is it used throughout the lakehouse instead of plain CSV or Parquet?
* **What Interviewers Look For:** Understanding of ACID transactions, time travel, and transaction log mechanics (`_delta_log`).
* **Model Answer:**
  * Delta Lake is an open-source storage layer that brings ACID transactions and reliability to Apache Spark Parquet files:
    1. **ACID Transactions (`_delta_log`):** Ensures that concurrent pipeline reads and writes never result in dirty reads or partial writes. If a job fails halfway, the transaction is rolled back.
    2. **Upsert (`MERGE INTO`) Support:** Allows performing atomic upserts, which are critical for our Silver conformed tables and SCD Type 2 dimension updates without rewriting entire tables.
    3. **Time Travel & Auditing:** Delta logs enable querying previous versions of a table for historical audit reconciliation (`VERSION AS OF`).
    4. **File Compaction (`OPTIMIZE` & `VACUUM`):** Enables merging small files into optimal 128MB chunks and pruning expired history to optimize read performance.

---

### Q1.4: What source ERP system is being modernized in this project, and what are its key challenges?
* **What Interviewers Look For:** Domain familiarity with legacy IBM AS400 DB2 and JD Edwards EnterpriseOne ERP.
* **Model Answer:**
  * The source system is **IBM AS400 DB2** running **JD Edwards (JDE) EnterpriseOne**.
  * The core challenges addressed by our modernization include:
    1. **Cryptic 4-Letter Column Naming:** Columns like `GLDOC` (Doc Number), `GLDGJ` (GL Date), `GLAA` (Domestic Amount) are incomprehensible to business users.
    2. **Non-Standard Julian Dates:** JDE stores dates as 6-digit integers in `CYYDDD` format (e.g., `124366` for Dec 31, 2024), which cannot be parsed by standard BI tools.
    3. **Implicit Currency Scaling:** Financial amounts are stored as integers without decimal points (e.g., $100.50 stored as `10050`).
    4. **Mainframe OLTP Protection:** Direct analytical reporting against AS400 causes CPU spikes and database locks on critical operational transaction processing.

---

### Q1.5: What is Power BI Direct Lake mode, and how does it differ from Import and DirectQuery modes?
* **What Interviewers Look For:** Clear understanding of Direct Lake's zero-copy VertiPaq RAM mapping.
* **Model Answer:**
  * **Import Mode:** Loads data into a proprietary Power BI `.pbix` file. Blazing fast (in-memory VertiPaq), but requires scheduled data refreshes, duplicates data storage, and suffers from data latency.
  * **DirectQuery Mode:** Translates visual clicks into live SQL queries sent to the database. Always real-time, but slow (seconds of latency per visual) and imposes heavy query loads on the database.
  * **Direct Lake Mode (The Modern Standard):** Combines the sub-second query performance of Import Mode with the freshness of DirectQuery. Power BI's VertiPaq engine loads Delta Parquet files directly from OneLake into capacity RAM without copying or importing. When the Gold lakehouse is updated, Power BI refreshes its metadata pointers in **< 1 second**.

---

## 3. Level 2: Intermediate Questions (Engineering, Cleansing & Modeling)

### Q2.1: How are JD Edwards 6-digit Julian dates (CYYDDD) converted to standard Gregorian dates in PySpark?
* **What Interviewers Look For:** Mathematical precision, boundary conditions (Century flag, Day of Year, leap years), and PySpark code implementation.
* **Model Answer:**
  * In JDE, dates are stored as integer `CYYDDD`:
    * `C` = Century flag (`0` = 1900s, `1` = 2000s, `2` = 2100s).
    * `YY` = 2-digit Year within century.
    * `DDD` = Day of Year (`001` to `366`).
  * The formula calculates `Full Year = 1900 + (C * 100) + YY`, formats the start of year as `YYYY-01-01`, and adds `(DDD - 1)` days.
  * **PySpark Implementation (from [01_silver_cleansing_dq.py](file:///Users/chandu/Documents/Python_practice/Fabric/src/notebooks/silver/01_silver_cleansing_dq.py#L20-L37)):**
    ```python
    def convert_julian_to_gregorian(julian_col):
        century = (julian_col / 100000).cast("int")
        year_part = ((julian_col % 100000) / 1000).cast("int")
        day_of_year = (julian_col % 1000).cast("int")
        
        full_year = lit(1900) + (century * lit(100)) + year_part
        start_of_year = to_date(concat(full_year.cast("string"), lit("-01-01")), "yyyy-MM-dd")
        return expr(f"date_add({start_of_year}, {day_of_year} - 1)")
    ```
  * **Edge Cases Tested:** Century boundary (`099365` $\rightarrow$ 1999-12-31), Leap Day Feb 29 (`124060` $\rightarrow$ 2024-02-29), Leap Year Day 366 (`124366` $\rightarrow$ 2024-12-31), and malformed Day 400 (`124400` $\rightarrow$ routed to Quarantine).

---

### Q2.2: How does the project handle currency decimal scaling for AS400 financial ledger amounts?
* **What Interviewers Look For:** Multi-currency handling, reference to JDE `F0013` currency master, and avoidance of rounding errors.
* **Model Answer:**
  * AS400 DB2 stores currency amounts as unscaled integers to prevent floating-point inaccuracies.
  * In the General Ledger (`F0911`), domestic amounts (`GLAA`) and foreign amounts (`GLACR`) are divided by `100.0` for 2-decimal currencies (USD, EUR, CAD, GBP):
    ```python
    (col("GLAA").cast("double") / 100.0).alias("amount_domestic")
    ```
  * In production, the engine references the currency master table `F0013` (`silver_f0013_currency_codes`) which defines the explicit decimal positioning:
    * Standard currencies (USD, EUR): `2 decimals` (divide by $10^2 = 100$).
    * Zero-decimal currencies (JPY): `0 decimals` (divide by $10^0 = 1$).
    * Three-decimal currencies (KWD): `3 decimals` (divide by $10^3 = 1000$).

---

### Q2.3: How does the Data Quality Quarantine Engine work in PySpark, and why doesn't it break pipeline execution?
* **What Interviewers Look For:** Understanding of fault tolerance, non-blocking ingestion, and DQ severity tiers.
* **Model Answer:**
  * Rather than failing an entire batch pipeline when a single malformed row arrives (which violates our 15-minute SLA), we use a **3-Tier Severity Model**: `STOP`, `WARNING`, and `QUARANTINE`.
  * **PySpark Execution:**
    1. PySpark evaluates conditions from `meta.dataquality_rule` and assigns a `dq_status` tag (e.g., `QUARANTINE_NULL_ACCOUNT`, `QUARANTINE_INVALID_DATE`).
    2. The DataFrame is split:
       ```python
       silver_valid_df = dq_evaluated_df.filter(col("dq_status") == "PASSED")
       quarantine_df   = dq_evaluated_df.filter(col("dq_status") != "PASSED")
       ```
    3. Valid records are written to `lh_ips_silver.silver_f0911_gl_ledger` and proceed immediately to Gold and Power BI.
    4. Corrupt records are diverted to `lh_ips_silver.silver_quarantine_records` along with the failure reason and ingestion timestamp.
    5. The failure count is logged in `log.dq_rule_run` and `log.dataset_run(rows_rejected)`. If the error percentage breaches `threshold_percent`, an alert is dispatched to Data Stewards.

---

### Q2.4: How is Slowly Changing Dimension Type 2 (SCD2) implemented for the Chart of Accounts (F0901)?
* **What Interviewers Look For:** Delta Lake `MERGE` patterns, record hashing, and maintaining historical validity flags.
* **Model Answer:**
  * For entities where history must be preserved (e.g., account descriptions, posting edit codes, customer credit ratings), we maintain active and historical versions in `lh_ips_silver.dim_account_scd2`.
  * **Implementation Logic (from [02_silver_scd2_dimensions.py](file:///Users/chandu/Documents/Python_practice/Fabric/src/notebooks/silver/02_silver_scd2_dimensions.py)):**
    1. **Change Detection:** Computes a deterministic `record_hash` using `sha2(concat_ws("||", tracked_columns), 256)`.
    2. **Identify Expired Records:** Joins incoming records with existing active records (`is_current = True`). If `account_id` matches but `record_hash` differs, the existing record is closed:
       ```python
       target_delta.alias("t").merge(
           incoming_df.alias("s"),
           "t.account_id = s.account_id AND t.is_current = true AND t.record_hash != s.record_hash"
       ).whenMatchedUpdate(set={
           "is_current": lit(False),
           "valid_to": current_timestamp()
       }).execute()
       ```
    3. **Insert Active Record:** Inserts the updated row as `valid_from = current_timestamp()`, `valid_to = NULL`, and `is_current = True`.

---

### Q2.5: What is the "Unknown Member (-1 Fallback)" pattern, and how does it prevent orphan records in Gold facts?
* **What Interviewers Look For:** Kimball referential integrity, preventing row drops during inner/equi-joins in BI tools.
* **Model Answer:**
  * In ERP environments, transactions frequently arrive before master dimensions are populated (late-arriving dimensions), or transactions reference obsolete account numbers.
  * In a standard inner join, these transaction rows are dropped, corrupting financial reports.
  * **Our Solution:**
    1. Every Dimension table in Gold (`Dim_Account`, `Dim_Company`, `Dim_Customer`) seeds a default record where `Key = -1`, `Description = 'Unknown / Not Applicable'`, and numeric attributes default to `0`.
    2. During PySpark Fact generation, dimension foreign keys use `coalesce()`:
       ```python
       coalesce(col("acc.account_id"), lit("-1")).alias("account_key")
       ```
    3. In Power BI, 100% of financial ledger dollars are preserved; orphan records display under "Unknown Account" for financial auditing rather than disappearing.

---

### Q2.6: How do you handle JDE's multi-company corporate parent fallback (Company 00000)?
* **What Interviewers Look For:** Complex business hierarchy resolution in ERP data engineering.
* **Model Answer:**
  * In JDE EnterpriseOne, certain enterprise-wide master records (such as Address Book entities `F0101` or Customer Master `F03012`) are defined under corporate parent Company `00000` rather than the operational company (`00010`, `00020`).
  * If a query joins solely on `RPCO = CompanyCode`, transactions for corporate customers fail to match.
  * **Resolution Logic:**
    1. Attempt primary join on `Operating Company` + `Customer ID`.
    2. If no match is found, fallback to `Company 00000` + `Customer ID`.
    3. If still unmapped, resolve to default member `-1`.
  * This eliminates false-positive orphan rejections for corporate shared services.

---

## 4. Level 3: Advanced Questions (Orchestration, Performance, Security & Purview)

### Q3.1: Explain the architecture of the Metadata-Driven Ingestion Framework and its 4-schema separation.
* **What Interviewers Look For:** Framework design patterns, configuration vs. state decoupling, and administrative governance.
* **Model Answer:**
  * Rather than creating 97 hardcoded pipelines for each ERP table, the framework uses generic parameterized Fabric pipelines driven by a metadata database (`sqldb-meta-orch-dev`).
  * The database separates responsibilities across **4 distinct schemas (24 tables total)**:
    1. **`meta` (9 tables):** Static system configurations, dataset registry (`meta.dataset`), layer parameters (`dataset_src_to_brnz`, `dataset_brnz_to_silver`, `dataset_silver_to_gold`), schedules, and DQ rules. Low volatility; read-only at runtime.
    2. **`ctl` (2 tables):** High volatility operational state. Tracks dynamic high watermarks (`ctl.watermark_state`) and pipeline locks (`ctl.dataset_state`).
    3. **`log` (4 tables):** Append-only audit telemetry capturing run metrics (`log.pipeline_run`, `log.dataset_run`), rule-level evaluation results (`log.dq_rule_run`), and stack traces (`log.error_event`).
    4. **`stage` (9 tables):** Mirrors the 9 sheets in [Ingestion_metadata_load_template.xlsx](file:///Users/chandu/Documents/Python_practice/Fabric/data/metadata/Ingestion_metadata_load_template.xlsx). Stored procedure `stage.sp_UpsertMetadataFromStage` validates and atomically merges staged configs into `meta` and `ctl`.

---

### Q3.2: What is the "Subtype Inheritance Pattern" in the metadata repository, and what problem does it solve?
* **What Interviewers Look For:** Relational modeling for data engineering metadata and eliminating polymorphic foreign key anti-patterns.
* **Model Answer:**
  * **The Problem:** In naive frameworks, stage-specific tables (`src_to_brnz`, `brnz_to_silver`, `silver_to_gold`) have independent primary key sequences. This breaks referential integrity because audit logs, schedules, and DQ rules cannot point a single foreign key to three separate target tables.
  * **The Solution:** A master registry table `meta.dataset` acts as the single source of truth with primary key `dataset_id`. All stage configuration tables act as **1:1 subtype tables** where `dataset_id` serves simultaneously as **Primary Key (PK)** and **Foreign Key (FK)**.
  * **Benefit:** Unified telemetry, centralized scheduling, and seamless end-to-end lineage tracking across all stages.

---

### Q3.3: How do you prevent "DirectQuery Fallback" in Power BI Direct Lake mode to guarantee sub-800ms SLAs?
* **What Interviewers Look For:** In-depth knowledge of VertiPaq memory engine, Direct Lake modeling rules, and write-time optimizations.
* **Model Answer:**
  * If a Direct Lake model encounters unsupported operations, it silently falls back to **DirectQuery**, converting memory scans into slow SQL queries.
  * To guarantee sub-800ms response times, we enforce **5 Architectural Guardrails**:
    1. **No DAX Calculated Columns:** Direct Lake does not support DAX calculated columns. All calculations (e.g., date formatting, financial class logic) are calculated upstream in PySpark and stored physically in Delta files.
    2. **No DAX Calculated Tables:** Tables cannot be generated via `CALENDARAUTO()`; we use a physical `Dim_Date` table.
    3. **Enable Microsoft V-Order:** In PySpark Gold writes, we enable `spark.sql.parquet.vorder.enabled = true`, which applies write-time sorting and compression compatible with VertiPaq memory mapping.
    4. **Delta Z-ORDER Clustering:** We execute `OPTIMIZE Fact_Table ZORDER BY (DateKey)` to maximize file skipping.
    5. **RLS Exclusively in DAX:** Row-Level Security is implemented in the semantic model using DAX `USERPRINCIPALNAME()`. Defining SQL-level views or security policies on the Lakehouse SQL endpoint forces immediate DirectQuery fallback.

---

### Q3.4: Why should enterprise reporting avoid the "Default Semantic Model" in favor of a "Custom Semantic Model"?
* **What Interviewers Look For:** Fabric governance, security boundaries, and workspace design standards.
* **Model Answer:**
  * Fabric automatically generates a **Default Semantic Model** for every lakehouse, but using it in enterprise production is an **anti-pattern**:
    1. **Uncontrolled Table Exposure:** The default model automatically includes *every* table in the Lakehouse—including Bronze raw extracts, intermediate staging tables, and quarantine error tables.
    2. **No Object-Level Security (OLS):** You cannot hide sensitive columns or tables in the default model.
    3. **Schema Drift Breakage:** If an engineer creates a temporary table in the Lakehouse, it immediately appears in the default semantic model.
  * **Custom Semantic Model Standard:** We author a dedicated Custom Semantic Model (`sm_ips_enterprise_financial`) that explicitly selects only curated Gold tables (`Dim_*` and `Fact_*`), contains enterprise DAX measures, and can be published into separate downstream consumption workspaces.

---

### Q3.5: How is hybrid network security configured for the On-Premises Data Gateway (OPDG) connecting to AS400?
* **What Interviewers Look For:** Network topologies, Azure vWAN, firewall ports, and zero-inbound perimeter security.
* **Model Answer:**
  * The architecture uses **Azure Virtual WAN (`hub-centralindia-vwan`)** and **Azure Firewall Standard (`hub-southindia-afw`)** to bridge cloud and on-premises datacenters.
  * A dedicated Windows Server 2022 Gateway VM (`genie-fabric-prod-01`: `10.100.8.10`) hosts the On-Premises Data Gateway and 64-bit IBM i Access (ACS) ODBC driver.
  * **Zero Inbound Ports:** No public inbound ports are opened. The gateway initiates outbound WebSocket connections over encrypted **TLS 443** to the Azure Service Bus relay.
  * **Internal Ports:** The gateway communicates internally with AS400 (`10.242.2.25`) over dedicated IBM DB2 host ports (`446`, `449`, `8471`, `9471`) restricted to the internal corporate subnet.
  * **Secrets:** All credentials and connection strings are stored in **Azure Key Vault (`ipskv-prod-chennai-01`)**.

---

### Q3.6: How does Microsoft Purview integrate with Microsoft Fabric and AS400 DB2 for end-to-end lineage?
* **What Interviewers Look For:** Data governance integration, column-level lineage, and hybrid metadata scanning.
* **Model Answer:**
  * Microsoft Purview connects hybrid data across two engines:
    1. **On-Premises Scanning:** Purview uses a **Self-Hosted Integration Runtime (SHIR)** co-located on the Gateway VM to scan IBM AS400 DB2 schemas (`CRPOTA`, `CRPCTL`) on a scheduled weekly window.
    2. **Fabric Native Scanning:** Uses the native OneLake scanner to automatically catalog Lakehouses, PySpark notebooks, Data Factory pipelines, and Power BI semantic models without custom scripts.
  * **Column-Level Lineage:** Purview maps the transformation graph from the raw AS400 column (`GLAA`) $\rightarrow$ Bronze Parquet $\rightarrow$ Silver (`amount_domestic`) $\rightarrow$ Gold (`AmountDomestic`) $\rightarrow$ DAX measure (`[Total Revenue]`) $\rightarrow$ Executive Dashboard card tile.
  * **Impact Analysis:** Allows engineers to evaluate downstream dependencies before modifying an AS400 column, preventing broken reports.

---

### Q3.7: How are Fabric Capacity Units (CUs) managed and smoothed to prevent throttling on F32/F64 SKUs?
* **What Interviewers Look For:** FinOps, capacity smoothing, throttling mitigation, and batch concurrency control.
* **Model Answer:**
  * Fabric compute is metered in Capacity Units (CUs) with background smoothing (bursting over 24-hour windows).
  * On an **F32 (Dev)** or **F64 (Prod)** capacity, unthrottled concurrent Spark jobs can trigger interactive query degradation.
  * **Mitigation Strategies in our Architecture:**
    1. **Ingestion Group Sequencing:** Master pipelines run Dimensions (`IG_AS400_BATCH_DIM`) first with high concurrency (10–15 threads), followed by Facts (`IG_AS400_BATCH_FACT`) throttled to 3–5 threads.
    2. **Target File Compaction:** Scheduled off-peak maintenance runs `OPTIMIZE` and `VACUUM` to prevent thousands of small Parquet files from increasing VertiPaq dictionary load times and CU burn.
    3. **Capacity Metric App Monitoring:** Configured alerts trigger when CU consumption exceeds 80% over a 10-minute window, alerting the team before interactive throttling takes effect.

---

## 5. Scenario-Based Behavioral & Problem-Solving Questions

### Scenario 1: Late-Arriving Dimensions & Financial Reconciliation
* **Question:** *"During the month-end close, the finance team reports that General Ledger ledger line totals in Power BI match the AS400 ledger, but certain transactions show an 'Unknown Account'. How do you investigate, and what architectural feature prevented a total variance?"*
* **Response Framework:**
  1. Explain that the **Unknown Member Pattern (`-1` Fallback)** saved the financial total by assigning unmapped `account_id` values to surrogate key `-1` instead of dropping rows via an inner join.
  2. Query `lh_ips_silver.dim_account_scd2` to check whether the new account code was recently created in AS400 but not yet synced.
  3. Verify whether the transaction used a corporate parent company fallback (`Company 00000`).
  4. Trigger an on-demand incremental run of `IG_AS400_BATCH_DIM`, update file pointers via the REST API metadata sync, and verify that the transaction dynamically rebinds to the newly active account dimension.

---

### Scenario 2: Data Quality Quarantine Alert on Julian Date
* **Question:** *"An automated alert notifies you that 500 records from the Accounts Receivable ledger (F03B11) were quarantined during the morning batch run with error code `QUARANTINE_INVALID_DATE`. How do you respond?"*
* **Response Framework:**
  1. Query `lh_ips_silver.silver_quarantine_records` filtering on `dq_status = 'QUARANTINE_INVALID_DATE'`.
  2. Inspect the raw Julian column (`RPDGJ`) and identify the pattern (e.g., malformed date integer `124400` where day 400 does not exist, or century digit `0` when `1` was expected).
  3. Confirm that healthy records continued flowing to Silver and Gold, ensuring zero downtime for valid invoices.
  4. Notify the AR Data Steward with exact transaction document numbers (`RPDOC`) and company codes for upstream correction in AS400 DB2.

---

### Scenario 3: Performance Drop from Direct Lake to DirectQuery
* **Question:** *"A Power BI dashboard that previously loaded in 600ms suddenly takes 12 seconds to render visual tiles. How do you diagnose and fix the issue?"*
* **Response Framework:**
  1. Open **Performance Analyzer** in Power BI Desktop or query the dynamic management views (DMVs) / Fabric Capacity Metrics app to check the **Direct Lake Behavior**.
  2. Confirm whether the semantic model has fallen back to **DirectQuery mode**.
  3. Check the recent commits to the semantic model:
     - Did a developer add a **DAX calculated column** or calculated table? (If yes, move logic upstream to PySpark).
     - Was a column added with an unsupported data type (e.g., binary, complex geometry)?
     - Did the model exceed the capacity RAM limit (10 GB on F32, 25 GB on F64)?
  4. Run `OPTIMIZE ... ZORDER BY` on the underlying Gold Delta table and execute a `clearCacheAndRehydrate` REST API call to re-establish VertiPaq in-memory caching.

---

### Key Documentation References in the Repo:
* **Architecture Overview:** [IPS_Metadata_Driven_Ingestion_Framework_Architecture_Guide.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_Metadata_Driven_Ingestion_Framework_Architecture_Guide.md)
* **Kimball Dimensional Specification:** [IPS_Kimball_Dimensional_Warehouse_Specification.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_Kimball_Dimensional_Warehouse_Specification.md)
* **Direct Lake Semantic Model Design:** [IPS_Fabric_Gold_Layer_Semantic_Model_Design.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_Fabric_Gold_Layer_Semantic_Model_Design.md)
* **Enterprise Security Architecture:** [IPS_Enterprise_Security_Architecture_and_Compliance_Guide.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_Enterprise_Security_Architecture_and_Compliance_Guide.md)
* **Microsoft Purview Governance:** [IPS_Microsoft_Purview_Implementation_and_Operations_Guide.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_Microsoft_Purview_Implementation_and_Operations_Guide.md)
