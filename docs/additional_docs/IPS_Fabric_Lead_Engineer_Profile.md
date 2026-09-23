# Professional Profile: Lead Microsoft Fabric & Azure Data Platform Engineer

> **Specialization:** Enterprise Microsoft Fabric Migrations · OneLake Medallion Architecture · Power BI Direct Lake Modeling · Hybrid Mainframe/AS400 Integration · FinOps Capacity Governance · Git-Driven CI/CD  
> **Target Roles:** Lead Data Engineer | Principal Microsoft Fabric Architect | Azure Data Platform Lead  
> **Source Project Reference:** IPS BI Modernization & Enterprise Azure Data Platform  

---

## Executive Summary

Accomplished **Lead Data Platform Engineer / Solutions Architect** with extensive experience architecting and implementing mission-critical enterprise analytics platforms on **Microsoft Fabric** and **Microsoft Azure**. Recognized for leading end-to-end modernization of legacy on-premises mainframe ERP ecosystems (IBM AS400 DB2 / JD Edwards EnterpriseOne) to modern cloud data platforms.

Proven track record directing cross-functional engineering teams (10+ data engineers and QA specialists), designing automated **Metadata-Driven Ingestion Frameworks (MDF)** spanning 121 enterprise datasets, optimizing Ralph Kimball Star Schemas for **Power BI Direct Lake** mode (sub-800ms query latency), establishing enterprise **Okta-to-Entra ID RBAC security architectures**, and driving **FinOps capacity governance** that achieved a 50% compute reduction and over $170,000 in annualized cloud savings.

---

## Core Competencies & Technical Skills

| Domain | Technologies, Frameworks & Standards |
|---|---|
| **Microsoft Fabric Ecosystem** | Fabric Lakehouse, Fabric Data Warehouse, OneLake, Direct Lake Mode, Fabric Data Factory (Pipelines & Dataflows Gen2), Real-Time Hub / Eventhouse, Data Activator (Reflex), OneLake Shortcuts, Fabric Mirroring, Capacity Metrics App |
| **Big Data & Compute Engines** | Apache Spark 3.5, PySpark, Delta Lake 2.4, V-Order Write Optimization, Z-Ordering, File Bin-Packing (`OPTIMIZE`), Dead-File Purging (`VACUUM`), T-SQL, SQL Analytics Endpoints |
| **Data Ingestion & Integration** | On-Premises Data Gateway (OPDG Standard Cluster), IBM i Access Client Solutions (ACS) 64-bit ODBC, CDC Ingestion (Fivetran / Firsthire), REST APIs, Flat Files / Excel, Azure Blob/ADLS Gen2 Storage |
| **Data Modeling & BI** | Ralph Kimball Dimensional Modeling (Conformed Dimensions, Fact Tables, Enterprise Bus Matrix), Custom Direct Lake Semantic Models, DAX (Data Analysis Expressions), TMDL (Tabular Model Definition Language), VertiPaq In-Memory Optimization, Tier-2 Reporting Workspaces & Power BI Apps |
| **Security & Governance** | Microsoft Entra ID RBAC, Okta Directory SCIM Group Push Sync, OneLake Data Access Roles (Folder-level ACLs), Dynamic DAX Row-Level Security (`USERPRINCIPALNAME()`), Microsoft Purview Data Governance, Workspace Tier Segregation |
| **DevOps & Automation** | Fabric Git Integration, GitHub Actions CI/CD (`ci-validate.yml`, `deploy-to-prod.yml`), PySpark `.py` serialization enforcement, TMDL model versioning, Environment Management (`requirements.txt`), Azure Logic Apps, Azure Key Vault |
| **FinOps & Capacity Sizing** | Fabric Capacity Unit (CU) Sizing (F128, F64, F32), 1-Year Capacity Reservations vs. PAYG, ARM REST API Capacity Lifecycle Scheduling (`Microsoft.Fabric/capacities` suspend/resume), Smoothing & Throttling Mitigation |
| **Cloud Networking & Infra** | Azure Virtual WAN (vWAN Hub-Spoke), Azure Firewall, Azure Bastion, Private Endpoints, Central US Region deployment |

---

## Featured Flagship Experience

### **Lead Fabric Data Platform Engineer / Technical Lead**
**Project:** Enterprise Legacy BI Modernization to Microsoft Fabric  
**Client / Domain:** IPS Corporation — Industrial & Enterprise Manufacturing  
**Source Systems:** IBM AS400 DB2 (v7.x4, Host: IPSRR00) / JDE EnterpriseOne (Schemas: `CRPOTA`, `CRPCTL`)  
**Target Architecture:** Microsoft Fabric Medallion Architecture (`th_bronze` $\rightarrow$ `th_silver` $\rightarrow$ `th_gold`) & Power BI Direct Lake

#### Key Architectural & Engineering Leadership Responsibilities:

##### 1. Enterprise Medallion Architecture & OneLake Lakehouse Design
* Architected and implemented an enterprise-grade **Medallion Architecture** on Microsoft Fabric OneLake storing Delta Parquet data across three unified tiers: Bronze (`lh_bronze`), Silver (`lh_silver`), and Gold (`lh_gold`).
* Standardized on **Fabric Lakehouse** over Data Warehouse for the Gold Layer, unlocking direct, high-performance Spark writes, native Direct Lake VertiPaq caching, and read-only SQL endpoint protection against unauthorized business updates.
* Enforced technical audit metadata columns (`_ingested_dt_pipeline`, `_freshwr_synced`, `_source_file`, and a SHA-256 hash `_ingested_at`) across all bronze Delta tables to guarantee 100% data auditability and zero-loss change detection.

##### 2. Hybrid Ingestion & Metadata-Driven Ingestion Framework (MDF)
* Designed a metadata-driven ingestion framework governing **121 enterprise datasets** from JD Edwards EnterpriseOne ERP:
  * **58 Batch Datasets:** Automated scheduled extraction via Fabric Data Factory Copy Activity using a high-availability **On-Premises Data Gateway (OPDG)** cluster running 64-bit IBM i ACS ODBC drivers (`cwbdsede.dll`) connecting securely to IBM AS400 over port 6017 without inbound firewall openings.
  * **63 Near-Real-Time (NRT) Datasets:** Orchestrated continuous CDC replication to ADLS Gen2, connected into Fabric via **OneLake Shortcuts**, eliminating CPU overhead and database connection contention on the production AS400 OLTP core.
* Parameterized ingestion pipelines driven by an Azure SQL metastore (`sqldb-meta-orch-dev`), eliminating hundreds of brittle static pipelines and standardizing dynamic watermark updates and failure notifications.

##### 3. Silver Layer PySpark Transformation & Data Quality Engine
* Built a generic PySpark transformation engine (Spark 3.5 / Delta Lake 2.4) executing **10 standardized transformation categories**, including:
  * Converting legacy 6-digit Julian dates (`CYYDDD`) to standardized ISO date formats.
  * Adjusting cryptic JDE implied-decimal numeric fields based on system control dictionary definitions.
  * Mapping cryptic physical AS400 field names (e.g., `GLCO`, `GLDGJ`, `GLAA`) into normalized business enterprise names.
* Integrated dynamic data quality validation rules with automated dead-letter quarantine routing (`*_entity_quarantine`) to prevent corrupted records from infiltrating the reporting layer.

##### 4. Ralph Kimball Star Schema & Gold Dimensional Modeling
* Designed the enterprise dimensional model following Ralph Kimball best practices, defining a cross-functional **Kimball Bus Matrix** linking conformed dimensions (`Dim_Customer`, `Dim_Date`, `Dim_BranchPlant`, `Dim_Account`, `Dim_Item`) to business facts (`Fact_GL_Transactions`, `Fact_AR_Open`, `Fact_AP_Open`, `Fact_Inventory`).
* Enforced integer surrogate keys across all dimensions to minimize in-memory memory footprint and accelerate table join operations in the VertiPaq storage engine.

##### 5. Power BI Direct Lake Semantic Modeling & Fallback Prevention
* Designed enterprise **Custom Semantic Models** in Direct Lake mode, completely replacing the auto-generated Lakehouse Default Model to prevent schema drift, uncurated table exposure, and performance degradation.
* Implemented strict write-time optimizations using **Fabric V-Order** sorting and distribution (`spark.sql.parquet.vorder.enabled = true`), enabling VertiPaq to project Delta Parquet data directly into RAM without compression transcoding.
* Engineered safeguards against **DirectQuery Fallback**:
  * Pushed all calculated logic and data type casting upstream into PySpark notebooks (enforcing zero DAX calculated columns or tables).
  * Monitored capacity memory constraints (25 GB on F64 PROD / 10 GB on F32 DEV).
  * Set semantic model Direct Lake behavior to `Direct Lake Only` in non-prod validation environments to fail fast and catch query antipatterns before production release.
* Implemented in-memory **Dynamic Row-Level Security (RLS)** using DAX filters (`USERPRINCIPALNAME()`) strictly at the semantic model level, avoiding SQL endpoint RLS which triggers forced DirectQuery fallback.
* Orchestrated automated post-ETL **clearCacheAndRehydrate REST API** refresh calls at the end of data pipelines to force VertiPaq cache rehydration within 1 second.

##### 6. Automated Real-Time Event-Driven Ingestion
* Engineered a serverless ingestion pipeline for self-service spreadsheet uploads (`FlatFile_Repo`) utilizing Fabric **Real-Time Hub** and **Data Activator (Reflex)**.
* Configured automated event triggers matching OneLake `BlobCreated` events on `.csv` files to invoke parameterized Fabric pipelines (`pl_ingest_bronze_flat_files`), slashing ingestion latency from batch schedules down to near-instant execution.

##### 7. Enterprise Security Architecture & Workspace Segregation
* Established a two-tier workspace isolation model separating Data Engineering (`bim_data_dev`) from Consumption / Reporting (`bim_report_dev`):
  * Granted **OneLake Sharing (Read & Build)** exclusively on Gold tables to Tier-2 reporting models, completely shielding Bronze and Silver lakehouses from report authors.
* Synchronized identity access management from **Okta Directory to Microsoft Entra ID** via SCIM Group Push into 5 standardized role groups (`SG-PBI-FabricAdmins`, `SG-PBI-WorkspaceAdmins`, `SG-PBI-Developers`, `SG-PBI-ReportConsumers`, `SG-PBI-GatewayAdmins`).
* Configured granular **OneLake Folder-Level Data Access Roles** (e.g., `FlatFileRepo_Contributor`) enabling designated business users to upload files to restricted directories without granting workspace contributor rights.

##### 8. CI/CD & DevOps Automation with GitHub Integration
* Established a collaborative DevOps roadmap across 10 developers and testers utilizing Fabric Git Integration with **Repository Pattern A (Single Workspace per Branch)**:
  * Enforced text-based PySpark **`.py` format** over `.ipynb` to eliminate Jupyter JSON metadata conflicts and enable clean line-by-line pull request code reviews.
  * Standardized Tabular Model Definition Language (**TMDL**) serialization for semantic models, allowing multiple developers to work concurrently on model measures without merge conflicts.
* Automated build validation and environment promotion workflows (`ci-validate.yml`, `deploy-to-prod.yml`) with automated item rebinding and rollback runbooks.

##### 9. FinOps, Capacity Sizing & Cost Governance Architecture
* Modeled organizational compute needs across two distinct lifecycle states:
  * **Implementation State (192 CUs):** Non-Prod F128 (DEV/SIT/UAT) + Prod F64.
  * **Steady-State State (96 CUs):** Non-Prod F32 (DEV) + Prod F64 (50% compute reduction).
* Formulated the **Hybrid FinOps Procurement Strategy (Option 4)** to circumvent the **Azure Reservation Downscale Trap** (where multi-month commitments cannot be exchanged downward):
  * Secured 1-Year Capacity Reservation on PROD F64 (~40.5% discount).
  * Maintained Non-Prod F128 on Pay-As-You-Go (PAYG) automated scheduling.
* Architected an **Azure Logic App automated scheduler** interfacing directly with Azure ARM REST APIs (`Microsoft.Fabric/capacities` suspend/resume):
  * Automatically pauses non-prod compute during off-hours (Mon–Fri 19:00 to 07:00 and weekends), operating at ~260 hours/month.
  * Created a webhook with a **4-hour automated lease timeout** for self-service developer weekend/after-hours testing overrides.
  * Delivered **$170,824+ in annualized savings** compared to running unmanaged 24/7 PAYG compute.

##### 10. Delta Lake Storage Hygiene, Compaction & Archival
* Designed automated table maintenance pipelines resolving the "Small File Problem" caused by frequent micro-batch CDC syncs:
  * Weekly bin-packing compaction (`OPTIMIZE`) targeted at 128 MB – 512 MB file sizes.
  * Weekly dead-file purging (`VACUUM RETAIN 168 HOURS`) preserving a 7-day Time Travel disaster recovery window while reclaiming stranded OneLake storage.
* Defined data retention matrices: active 3-year rolling hot storage in OneLake Silver/Gold; automated cold tiering to ADLS Gen2 for fiscal years 4 through 7+ to satisfy statutory audit compliance.

---

## Measurable Business & Engineering Impact

```
┌─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│       QUERY PERFORMANCE         │         COST OPTIMIZATION       │         DATA ACCELERATION       │
│             < 800 ms            │           $170,800+ / yr        │             < 6 minutes         │
│   95% Direct Lake report query  │     Achieved through Hybrid     │    NRT data availability SLA    │
│   latency in Power BI visual    │   FinOps & Logic App automated  │    from AS400 source directly   │
│   interactions via V-Order      │   ARM capacity scheduling       │    to executive Gold reports    │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘
┌─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│        COMPUTE FOOTPRINT        │       FINANCIAL AUDITABILITY    │         SYSTEM EFFICIENCY       │
│           50% Reduction         │              100%               │               0%                │
│    Contracted from 192 CUs      │   Variance-free reconciliation  │   ODBC connection load on       │
│    (Implementation) to 96 CUs   │   on GL net balances, AP open   │   production AS400 core via     │
│    (Steady State) at cutover    │   liabilities & AR aging        │   OneLake lakehouse shortcuts   │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘
```

---

## Key Architectural Decision Scenarios (Interview & Defense Talking Points)

### 1. Lakehouse vs. Data Warehouse for Gold Layer
* **Decision:** Implemented Gold as a **Fabric Lakehouse** with SQL Analytics Endpoint rather than a Fabric Data Warehouse.
* **Technical Justification:** Upstream transformations were implemented in PySpark. Writing from Spark into a Fabric Lakehouse commits natively as Delta Parquet in OneLake with full V-Order control. Writing into a Warehouse requires a JDBC connector with transactional overhead. Furthermore, Lakehouse SQL endpoints provide read-only safety, preventing users and external clients from running rogue updates or deletes against enterprise financial facts.

### 2. Default Semantic Model vs. Custom Semantic Model
* **Decision:** Enforced a strict architectural rule banning the Lakehouse Default Semantic Model for production reports in favor of **Custom Semantic Models**.
* **Technical Justification:** Default models automatically expose all upstream staging and raw tables, cannot implement custom DAX measures cleanly, and break downstream reports whenever schema drift occurs. Custom models allow controlled curated exposure of only `Dim_` and `Fact_` tables, custom DAX measures, integer surrogate relationships, and proper workspace boundary segregation.

### 3. Mitigating the Azure Capacity "Reservation Downscale Trap"
* **Decision:** Rejected a 1-year reservation on implementation capacity (F128) and implemented a Hybrid FinOps model (PROD F64 Reserved + Non-Prod F128 Scheduled PAYG).
* **Technical Justification:** Azure reservations are binding financial commitments that do not allow exchanges that downscale total monetary value. Buying an F128 reservation for a 6-month implementation results in paying for 128 CUs for the remainder of the year despite scaling the workspace to F32. Automating F128 pause/resume during business hours reduced monthly non-prod hours to ~260, yielding maximum savings without financial lock-in.

### 4. Direct Lake Mode Preservation vs. DirectQuery Fallback
* **Decision:** Banned DAX calculated columns/tables in semantic models and prohibited SQL endpoint view-based RLS.
* **Technical Justification:** In Fabric, calculated columns or SQL views with RLS force the VertiPaq engine to fall back to DirectQuery mode, increasing query latency from milliseconds to seconds. All date parsing, column joins, and flags were moved to PySpark Silver/Gold stages, and RLS was defined strictly within the Custom Semantic Model via DAX (`LOOKUPVALUE` with `USERPRINCIPALNAME()`).

### 5. Repository Serialization: `.py` vs. `.ipynb`
* **Decision:** Enforced PySpark `.py` script serialization over `.ipynb` in GitHub integration.
* **Technical Justification:** `.ipynb` files store large amounts of JSON execution metadata, outputs, and cell IDs, causing frequent, unreadable merge conflicts in Git. `.py` files provide pure line-by-line code diffs, streamlining peer reviews and automated linting in CI workflows.

---

## Certifications & Technical Proficiencies

* **Microsoft Certified: Fabric Analytics Engineer Associate (DP-600)**
* **Microsoft Certified: Azure Data Engineer Associate (DP-203)**
* **Microsoft Certified: Power BI Data Analyst Associate (PL-300)**
* **Operating Systems & Mainframe:** IBM i (AS400 DB2 v7.x), Windows Server 2022, Linux
* **Languages & Querying:** PySpark, Python 3.10+, DAX, T-SQL, KQL (Kusto Query Language), PowerShell, Shell scripting
