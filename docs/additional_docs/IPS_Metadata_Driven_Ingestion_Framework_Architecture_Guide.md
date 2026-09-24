# Detailed Implementation Document & Developer Guide: Metadata-Driven Ingestion Framework

**Project:** Legacy BI Modernization (IBM AS400 DB2 to Microsoft Fabric)  
**Client:** IPS Corporation  
**Target Database:** `sqldb-meta-orch-dev` (Microsoft Fabric SQL Database)  
**Author:** Principal Data & Framework Architect  
**Version:** 2.0 (Optimized & Production Ready)  

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Framework Architecture & Design](#2-framework-architecture--design)
   - [2.1 Medallion Architecture Data Flow](#21-medallion-architecture-data-flow)
   - [2.2 Schema Architecture & Separation of Concerns](#22-schema-architecture--separation-of-concerns)
   - [2.3 Key Architectural Patterns & Optimizations](#23-key-architectural-patterns--optimizations)
3. [Entity Relationship Diagram (ERD)](#3-entity-relationship-diagram-erd)
4. [SQL DDL Specification (sqldb-meta-orch-dev)](#4-sql-ddl-specification-sqldb-meta-orch-dev)
   - [A. Schema Definitions](#a-schema-definitions)
   - [B. Schema: meta (Configuration & Registry)](#b-schema-meta-configuration--registry)
   - [C. Schema: ctl (Operational State & Watermarks)](#c-schema-ctl-operational-state--watermarks)
   - [D. Schema: log (Execution Auditing & Metrics)](#d-schema-log-execution-auditing--metrics)
   - [E. Schema: stage (Excel Ingestion Staging Tables)](#e-schema-stage-excel-ingestion-staging-tables)
5. [Developer Operational Guide: Excel Load Template](#5-developer-operational-guide-excel-load-template)
   - [5.1 Dependency Order of Data Population](#51-dependency-order-of-data-population)
   - [5.2 Worksheet Guidelines & Field Specifications](#52-worksheet-guidelines--field-specifications)
   - [5.3 Data Validation Rules Summary](#53-data-validation-rules-summary)
6. [Automated Staging & Upsert Workflow](#6-automated-staging--upsert-workflow)
   - [6.1 Orchestration Workflow](#61-orchestration-workflow)
   - [6.2 Production Upsert Stored Procedure Script (stage.sp_UpsertMetadataFromStage)](#62-production-upsert-stored-procedure-script-stagesp_upsertmetadatafromstage)
7. [Developer Operational Walkthrough: Adding a New Dataset](#7-developer-operational-walkthrough-adding-a-new-dataset)
8. [Enterprise Dataset Topology & Ingestion Group Strategy (97 Tables)](#8-enterprise-dataset-topology--ingestion-group-strategy-97-tables)
   - [8.1 Batch vs. NRT Dual-Path Ingestion](#81-batch-vs-nrt-dual-path-ingestion)
   - [8.2 Key Architectural Justifications](#82-key-architectural-justifications)
   - [8.3 Optimum Ingestion Group Topology Matrix](#83-optimum-ingestion-group-topology-matrix)
   - [8.4 Orchestration Execution Pattern in Fabric](#84-orchestration-execution-pattern-in-fabric)
9. [Modernizing Fivetran AS400/DB2 Incremental Ingestion (15-Minute Latency SLA)](#9-modernizing-fivetran-as400db2-incremental-ingestion-15-minute-latency-sla)
   - [9.1 Latency Budget Equation & SLA Compliance Table](#91-latency-budget-equation--sla-compliance-table)
   - [9.2 End-to-End Fivetran CDC to Direct Lake Semantic Model Architecture](#92-end-to-end-fivetran-cdc-to-direct-lake-semantic-model-architecture)
10. [Fivetran NRT Implementation Blueprint & OneLake Shortcut Setup (Phases 1–3)](#10-fivetran-nrt-implementation-blueprint--onelake-shortcut-setup-phases-13)
    - [10.1 Phase 1: Fivetran & Landing Storage Setup (5-Minute Sync SLA)](#101-phase-1-fivetran--landing-storage-setup-5-minute-sync-sla)
    - [10.2 OneLake Landing Shortcut & Service Principal (SPN) Configuration](#102-onelake-landing-shortcut--service-principal-spn-configuration)
    - [10.3 Phase 2: Metadata Catalog Configuration (sqldb_meta_orch)](#103-phase-2-metadata-catalog-configuration-sqldb_meta_orch)
    - [10.4 Phase 3: Bronze & Silver Processing Layers (lh_bronze & lh_silver)](#104-phase-3-bronze--silver-processing-layers-lh_bronze--lh_silver)
11. [Gold Star Schema Architecture & Direct Lake Semantic Modeling (Phases 4–5)](#11-gold-star-schema-architecture--direct-lake-semantic-modeling-phases-45)
    - [11.1 Illustrative Gold Star Schema Architecture Table](#111-illustrative-gold-star-schema-architecture-table)
    - [11.2 Phase 5: Domain-Specific Direct Lake Semantic Models](#112-phase-5-domain-specific-direct-lake-semantic-models)
    - [11.3 Star Schema Relationships & Business DAX Measures](#113-star-schema-relationships--business-dax-measures)
    - [11.4 Phase 6: Orchestration Pipeline (pl_NRT_ingestion)](#114-phase-6-orchestration-pipeline-pl_nrt_ingestion)
12. [Data Structure of lh_bronze & Medallion Pipeline Design](#12-data-structure-of-lh_bronze--medallion-pipeline-design)
    - [12.1 Delta Storage Format & Fivetran System Columns](#121-delta-storage-format--fivetran-system-columns)
    - [12.2 Bronze to Silver to Gold Transformation Specifications](#122-bronze-to-silver-to-gold-transformation-specifications)
13. [Fivetran CDC Append-Only Internals & PySpark Deduplication Engine](#13-fivetran-cdc-append-only-internals--pyspark-deduplication-engine)
    - [13.1 How Fivetran Handles Changes to ADLS (Append-Only Log Stream)](#131-how-fivetran-handles-changes-to-adls-append-only-log-stream)
    - [13.2 Life of a Record Example (Order_ID = 1001 State Progression)](#132-life-of-a-record-example-order_id--1001-state-progression)
    - [13.3 Two-Step Silver Processing Engine (nb_silver_ingestion_NRT)](#133-two-step-silver-processing-engine-nb_silver_ingestion_nrt)
    - [13.4 Critical Considerations to Guarantee 15-Minute SLA](#134-critical-considerations-to-guarantee-15-minute-sla)

---

## 1. Executive Summary

This document serves as the comprehensive technical specification and developer operational guide for IPS Corporation's **Metadata-Driven Ingestion Framework**. The framework orchestrates, logs, monitors, and governs the end-to-end ingestion and transformation of legacy **IBM AS400 (DB2)** tables into a modern **Microsoft Fabric Medallion Architecture (Bronze $\rightarrow$ Silver $\rightarrow$ Gold)**.

Instead of building hardcoded, static pipelines for every source table, this framework utilizes a centralized metadata repository hosted inside a Fabric SQL Database (`sqldb-meta-orch-dev`). Parameterized Microsoft Fabric Data Factory pipelines and PySpark notebooks query this metadata at runtime to dynamically extract, land, cleanse, deduplicate, merge, and transform datasets.

Developers configure new datasets, execution schedules, data quality rules, and transformation logic using a pre-validated Excel template (`Ingestion_metadata_load_template.xlsx`). This workbook is automatically staged and merged into the production metadata repository using automated stored procedures.

> [!IMPORTANT]
> **Core Architectural Governance Principles:**  
> All pipeline orchestration and data modeling within this framework must adhere to the three foundational tenets of the modernization program: **(1) Business First, Technology Second**, **(2) Single Source of Truth**, and **(3) Mandatory Medallion Architecture**. For the full governance charter, see:  
> 👉 **[Core Architecture Design Tenets & Governance Principles Guide](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_BI_Core_Architecture_Design_Tenets_and_Governance_Principles.md)**.


---

## 2. Framework Architecture & Design

### 2.1 Medallion Architecture Data Flow

The ingestion framework operates across four distinct storage and processing zones:

![Metadata-Driven Ingestion Framework - Part 1](/Users/chandu/Documents/Python_practice/Fabric/images/15_metadata_driven_framework_overview_p1.png)

```mermaid
flowchart LR
    SRC[("Source System\nIBM AS400 DB2\n(e.g., CUSTMST)")] 
    -->|"(1) Extract & Land"| BRZ[("Bronze Layer\nRaw Parquet / Delta\n(OneLake Lakehouse)")]
    BRZ -->|"(2) Cleanse & Conform"| SLV[("Silver Layer\nCleanse Delta Tables\n(Lakehouse DB)")]
    SLV -->|"(3) Star Schema Transform"| GLD[("Gold Layer\nDimensions & Facts\n(Semantic Model DB)")]

    subgraph ORCH_ENGINE["Orchestration & Data Quality Engine"]
        META[("Metadata DB: sqldb-meta-orch-dev")]
        PIPE["Fabric Data Pipelines"]
        SPARK["Dynamic PySpark Notebooks"]
    end

    ORCH_ENGINE -.->|Param Driven| SRC
    ORCH_ENGINE -.->|Audit & Metrics| BRZ
    ORCH_ENGINE -.->|DQ Validation| SLV
    ORCH_ENGINE -.->|Model Orchestration| GLD
```

#### Layer Responsibilities
1. **Source $\rightarrow$ Bronze (Extraction & Raw Landing)**:
   * **Engine**: Fabric Data Factory Copy Activity / Pipeline.
   * **Operation**: Connects to IBM AS400 DB2 via ODBC (through Fabric On-Premises Data Gateway - OPDG), extracts incremental table records based on high watermarks, and lands raw output files (Parquet) into the Bronze Lakehouse folder path.
   * **Metadata Source**: `meta.dataset_src_to_brnz`.
2. **Bronze $\rightarrow$ Silver (Standardization, Cleansing & Conforming)**:
   * **Engine**: Dynamic PySpark Notebooks.
   * **Operation**: Reads raw Parquet files, enforces schema data types, trims whitespace, standardizes nulls, applies deduplication logic, evaluates dynamic data quality rules, and performs an incremental `MERGE` into Delta Lake tables.
   * **Metadata Source**: `meta.dataset_brnz_to_silver` & `meta.dataquality_rule`.
3. **Silver $\rightarrow$ Gold (Dimensional Modeling & Business Aggregation)**:
   * **Engine**: PySpark Notebooks / Fabric SQL Stored Procedures.
   * **Operation**: Transforms conformed Silver entities into Star Schema Dimensions (SCD Type 1 / Type 2) and Fact tables with surrogate key lookup and generation.
   * **Metadata Source**: `meta.dataset_silver_to_gold`.

---

### 2.2 Schema Architecture & Separation of Concerns

The repository isolates responsibilities into four distinct database schemas:

| Schema Name | Responsibility | Volatility / Access Profile | Primary Tables |
| :--- | :--- | :--- | :--- |
| **`meta`** | Static system metadata, dataset definitions, transformation rules, schedules, and group mapping. | **Low volatility**. Read-only for runtime engines; updated via Excel staging procedure. | `source_system`, `schedule`, `ingestion_group`, `dataset`, `ingestion_group_dataset`, `dataset_src_to_brnz`, `dataset_brnz_to_silver`, `dataset_silver_to_gold`, `dataquality_rule` |
| **`ctl`** | Active operational state, current high watermarks, and maximum surrogate keys. | **High volatility**. Read/write for runtime engines during every pipeline run. | `watermark_state`, `dataset_state` |
| **`log`** | Historical execution metrics, row counts, data quality rule evaluation results, and exception traces. | **Append-only**. High write volume during pipeline and notebook execution. | `pipeline_run`, `dataset_run`, `dq_rule_run`, `error_event` |
| **`stage`** | Staging tables mirroring the Excel load template sheets for business code resolution. | **Truncate-and-load**. Populated during metadata administrative updates. | `source_system`, `schedule`, `ingestion_group`, `dataset`, `ingestion_group_dataset`, `dataset_src_to_brnz`, `dataset_brnz_to_silver`, `dataset_silver_to_gold`, `dataquality_rule` |

---

### 2.3 Key Architectural Patterns & Optimizations

![Metadata-Driven Ingestion Framework - Part 2](/Users/chandu/Documents/Python_practice/Fabric/images/16_metadata_driven_framework_erd_patterns_p2.png)

#### A. Subtype Inheritance Pattern (Resolving Polymorphic Associations)
* **Problem**: In legacy designs, stage-specific configuration tables (`src_to_brnz`, `brnz_to_silver`, `silver_to_gold`) had independent `dataset_id` sequences. Audit logs and data quality rules could not enforce foreign keys to multiple disparate target tables.
* **Solution**: Introduced a single master dataset registry table: `meta.dataset`. All stage-specific configuration tables act as **1:1 subtype tables** where `dataset_id` serves simultaneously as **Primary Key (PK)** and **Foreign Key (FK)** referencing `meta.dataset(dataset_id)`. Schedules, ingestion groups, DQ rules, and operational execution logs reference `meta.dataset.dataset_id` exclusively.

#### B. Decoupling Configuration and Operational State
* **Problem**: Writing runtime properties such as `last_run_time` or `max_surrogate_key` back into `meta` configuration tables caused database lock contention and required elevated write permissions for Spark worker jobs.
* **Solution**: Completely isolated static configurations in `meta` and dynamic execution states in `ctl.dataset_state` and `ctl.watermark_state`. Spark engines and Fabric pipelines only need `db_datareader` on `meta` and `db_datawriter` on `ctl` and `log`.

#### C. Standardization of Column & Flag Definitions
* Standardized all active boolean indicators to `is_active BIT NOT NULL DEFAULT 1`.
* Standardized composite primary and natural key lists to `key_columns VARCHAR(500)`.
* Converted legacy string flags (`VARCHAR(1)`) to explicit `BIT` types (`use_explicit_mapping`, `is_mandatory_flag`).

---

## 3. Entity Relationship Diagram (ERD) & Relational Data Model

![Metadata-Driven Ingestion Framework - Physical Database Entity Relationship Diagram (ERD)](/Users/chandu/Documents/Python_practice/Fabric/images/60_metadata_framework_physical_database_erd_diagram.png)

The metadata repository database (`sqldb-meta-orch-dev`) is engineered around a normalized, highly extensible relational data model designed to separate pipeline orchestration configuration, runtime execution state, data quality evaluation, and observability logging.

### 3.1 Five Functional Architectural Tiers

```mermaid
flowchart TD
    subgraph Tier1["1. Scheduling & Orchestration Tier"]
        SCH[meta_schedule] -->|1:M schedule_id| IG[meta_ingestion_group]
        IG -->|1:M ingestion_group_id| IGD[meta_ingestion_group_dataset]
    end

    subgraph Tier2["2. Source & Dataset Core Registry"]
        SRC[meta_source_system] -->|1:M source_system_id| DS[meta_dataset]
        DS -->|1:M dataset_id| IGD
    end

    subgraph Tier3["3. Medallion Subtype Extensions (1:1)"]
        DS -->|1:1 dataset_id| S2B[meta_dataset_src_to_brnz]
        DS -->|1:1 dataset_id| B2S[meta_dataset_brnz_to_silver]
        DS -->|1:1 dataset_id| S2G[meta_dataset_silver_to_gold]
    end

    subgraph Tier4["4. Runtime Control State Tier (1:1)"]
        DS -->|1:1 dataset_id| CDS[ctl_dataset_state]
        DS -->|1:1 dataset_id| CWS[ctl_watermark_state]
    end

    subgraph Tier5["5. Data Quality & Observability Logging Hierarchy"]
        DS -->|1:M dataset_id| DQR[meta_dataquality_rule]
        PLR[log_pipeline_run] -->|1:M pipeline_run_id| DSR[log_dataset_run]
        DS -->|1:M dataset_id| DSR
        DSR -->|1:M dataset_run_id| DQL[log_dq_rule_run]
        DQR -->|1:M dq_rule_id| DQL
        DSR -->|1:M dataset_run_id| ERR[log_error_event]
        PLR -.->|1:M pipeline_run_id| ERR
    end

    style Tier1 fill:#f0f7ff,stroke:#0078d4,stroke-width:2px
    style Tier2 fill:#e6f2ff,stroke:#106ebe,stroke-width:2px
    style Tier3 fill:#fef9e7,stroke:#ffb900,stroke-width:2px
    style Tier4 fill:#fdf3f2,stroke:#d13438,stroke-width:2px
    style Tier5 fill:#f3f9f1,stroke:#107c10,stroke-width:2px
```

The database structure is organized into five tightly coupled functional domains:

1. **Scheduling & Group Orchestration Tier (`meta_schedule`, `meta_ingestion_group`, `meta_ingestion_group_dataset`)**:
   * Decouples cron/recurrence triggers from physical tables.
   * Enables batching of 97+ ERP tables into logical execution waves (e.g., `GRP_AS400_JDE_CORE_MASTER_DAILY`, `GRP_AS400_JDE_TRANSACTIONS_HOURLY`) managed via associative bridge table `meta_ingestion_group_dataset`.
2. **Source System & Core Dataset Registry (`meta_source_system`, `meta_dataset`)**:
   * `meta_source_system` tracks physical enterprise hosts (e.g., IBM AS400 DB2 `CRPDTA`, Salesforce CRM, Flat File SFTP).
   * `meta_dataset` acts as the conformed master registry entity for all tables, views, and data products.
3. **Medallion Pipeline Subtype Extension Tier (`meta_dataset_src_to_brnz`, `meta_dataset_brnz_to_silver`, `meta_dataset_silver_to_gold`)**:
   * Employs strict **1:1 table subtype relationships** keyed directly by `dataset_id`.
   * Isolates layer-specific transformation parameters (e.g., source queries, delta merge conditions, SCD Type 2 tracking, and star schema dimensional mappings) without polluting the parent catalog entity.
4. **Runtime Control State Tier (`ctl_dataset_state`, `ctl_watermark_state`)**:
   * Implements strict **1:1 operational state tracking** per dataset.
   * `ctl_dataset_state` manages operational locks (`IN_PROGRESS`, `SUCCESS`, `FAILED`) and high-watermark run timestamps to prevent race conditions during concurrent pipeline executions.
   * `ctl_watermark_state` isolates incremental extraction boundaries (such as JDE Julian dates or CDC transaction IDs).
5. **Data Quality & Observability Logging Hierarchy (`meta_dataquality_rule`, `log_pipeline_run`, `log_dataset_run`, `log_dq_rule_run`, `log_error_event`)**:
   * Implements a 3-tier hierarchical logging structure.
   * Every orchestrator pipeline execution registers in `log_pipeline_run`, which spawns multiple granular `log_dataset_run` records.
   * Each dataset run tracks exact row counts (`rows_read`, `rows_inserted`, `rows_updated`, `rows_rejected`) and links directly to individual rule-level audit logs in `log_dq_rule_run` and diagnostic stack traces in `log_error_event`.

---

### 3.2 Full Physical Database Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    meta_schedule ||--o{ meta_ingestion_group : "1:M schedule_id"
    meta_source_system ||--o{ meta_dataset : "1:M source_system_id"
    meta_ingestion_group ||--o{ meta_ingestion_group_dataset : "1:M ingestion_group_id"
    meta_dataset ||--o{ meta_ingestion_group_dataset : "1:M dataset_id"

    meta_dataset ||--|| meta_dataset_src_to_brnz : "1:1 dataset_id (Subtype)"
    meta_dataset ||--|| meta_dataset_brnz_to_silver : "1:1 dataset_id (Subtype)"
    meta_dataset ||--|| meta_dataset_silver_to_gold : "1:1 dataset_id (Subtype)"
    meta_dataset ||--|| ctl_dataset_state : "1:1 dataset_id (State)"
    meta_dataset ||--|| ctl_watermark_state : "1:1 dataset_id (Watermark)"

    meta_dataset ||--o{ meta_dataquality_rule : "1:M dataset_id"

    log_pipeline_run ||--o{ log_dataset_run : "1:M pipeline_run_id"
    meta_dataset ||--o{ log_dataset_run : "1:M dataset_id"

    log_dataset_run ||--o{ log_dq_rule_run : "1:M dataset_run_id"
    meta_dataquality_rule ||--o{ log_dq_rule_run : "1:M dq_rule_id"

    log_dataset_run ||--o{ log_error_event : "1:M dataset_run_id"
    log_pipeline_run ||--o{ log_error_event : "1:M pipeline_run_id"

    meta_schedule {
        BIGINT schedule_id PK
        VARCHAR schedule_name
        VARCHAR cron_expression
        BIT is_active
        DATETIME2 created_date
    }

    meta_ingestion_group {
        BIGINT ingestion_group_id PK
        BIGINT schedule_id FK
        VARCHAR group_name UK
        INT execution_order
        INT concurrency_limit
        BIT is_active
    }

    meta_ingestion_group_dataset {
        BIGINT group_dataset_id PK
        BIGINT ingestion_group_id FK
        BIGINT dataset_id FK
        INT execution_priority
        BIT is_active
    }

    meta_source_system {
        BIGINT source_system_id PK
        VARCHAR source_system_code UK
        VARCHAR source_system_name
        VARCHAR source_system_type
        VARCHAR connection_secret_name
        BIT is_active
    }

    meta_dataset {
        BIGINT dataset_id PK
        BIGINT source_system_id FK
        VARCHAR dataset_name UK
        VARCHAR domain_name
        VARCHAR data_owner_email
        BIT is_active
        DATETIME2 created_at
    }

    meta_dataset_src_to_brnz {
        BIGINT dataset_id PK_FK
        VARCHAR source_schema_name
        VARCHAR source_table_name
        VARCHAR source_query
        VARCHAR destination_path
        VARCHAR destination_file_name_prefix
        VARCHAR destination_file_type
        VARCHAR bronze_schema_name
        VARCHAR bronze_table_name
        BIT use_explicit_mapping
        VARCHAR key_columns
        VARCHAR source_watermark_column
    }

    meta_dataset_brnz_to_silver {
        BIGINT dataset_id PK_FK
        VARCHAR source_lakehouse_name
        VARCHAR source_table_name
        VARCHAR target_lakehouse_name
        VARCHAR target_table_name
        VARCHAR key_columns
        VARCHAR partition_columns
        VARCHAR merge_query
        BIT deduplication_enabled
    }

    meta_dataset_silver_to_gold {
        BIGINT dataset_id PK_FK
        VARCHAR target_gold_schema
        VARCHAR target_gold_table_name
        VARCHAR table_type
        VARCHAR business_logic_sql
        VARCHAR scd_type
        VARCHAR surrogate_key_column
    }

    ctl_dataset_state {
        BIGINT dataset_id PK_FK
        VARCHAR current_status
        DATETIME2 last_successful_run
        DATETIME2 last_failed_run
        VARCHAR last_execution_id
        INT retry_count
        DATETIME2 updated_at
    }

    ctl_watermark_state {
        BIGINT dataset_id PK_FK
        VARCHAR watermark_column_name
        VARCHAR watermark_value
        VARCHAR watermark_data_type
        DATETIME2 last_extracted_timestamp
        DATETIME2 updated_at
    }

    meta_dataquality_rule {
        BIGINT dq_rule_id PK
        BIGINT dataset_id FK
        VARCHAR rule_name
        VARCHAR rule_type
        VARCHAR target_column
        VARCHAR rule_expression
        VARCHAR error_threshold_action
        BIT is_active
    }

    log_pipeline_run {
        BIGINT pipeline_run_id PK
        BIGINT ingestion_group_id FK
        VARCHAR fabric_pipeline_id
        VARCHAR pipeline_status
        DATETIME2 start_time
        DATETIME2 end_time
        INT total_datasets
        INT failed_datasets
    }

    log_dataset_run {
        BIGINT dataset_run_id PK
        BIGINT pipeline_run_id FK
        BIGINT dataset_id FK
        VARCHAR execution_status
        BIGINT rows_read
        BIGINT rows_inserted
        BIGINT rows_updated
        BIGINT rows_rejected
        DATETIME2 start_time
        DATETIME2 end_time
        VARCHAR error_message
    }

    log_dq_rule_run {
        BIGINT dq_run_id PK
        BIGINT dataset_run_id FK
        BIGINT dq_rule_id FK
        VARCHAR evaluation_status
        BIGINT total_rows_evaluated
        BIGINT failing_rows_count
        VARCHAR failure_sample_json
        DATETIME2 evaluated_at
    }

    log_error_event {
        BIGINT error_event_id PK
        BIGINT pipeline_run_id FK
        BIGINT dataset_run_id FK
        VARCHAR error_severity
        VARCHAR error_component
        VARCHAR error_code
        VARCHAR error_message
        VARCHAR stack_trace
        DATETIME2 logged_at
    }
```

---

### 3.3 Physical Entity Relationship Cardinality Matrix

The following table summarizes all 14 physical relationships modeled in the metadata catalog:

| # | Parent Table | Child Table | Foreign Key Column | Cardinality | Architectural Purpose & Rationale |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1** | `meta_schedule` | `meta_ingestion_group` | `schedule_id` | **1 : Many** | One cron schedule triggers multiple parallel or sequential ingestion groups. |
| **2** | `meta_source_system` | `meta_dataset` | `source_system_id` | **1 : Many** | A source system (e.g. AS400 DB2) owns multiple datasets (e.g. `F0911`, `F4211`). |
| **3** | `meta_ingestion_group` | `meta_ingestion_group_dataset` | `ingestion_group_id` | **1 : Many** | An ingestion group orchestrates multiple assigned datasets. |
| **4** | `meta_dataset` | `meta_ingestion_group_dataset` | `dataset_id` | **1 : Many** | Associative table maps datasets to groups with explicit execution priority. |
| **5** | `meta_dataset` | `meta_dataset_src_to_brnz` | `dataset_id` | **1 : 1** | Strict 1:1 subtype containing source extraction and Bronze Lakehouse landing configurations. |
| **6** | `meta_dataset` | `meta_dataset_brnz_to_silver` | `dataset_id` | **1 : 1** | Strict 1:1 subtype containing Silver cleansing, deduplication, and Delta merge specifications. |
| **7** | `meta_dataset` | `meta_dataset_silver_to_gold` | `dataset_id` | **1 : 1** | Strict 1:1 subtype containing Gold dimensional modeling, fact/dimension logic, and SCD rules. |
| **8** | `meta_dataset` | `ctl_dataset_state` | `dataset_id` | **1 : 1** | Operational runtime state tracking current execution status, locks, and retry counts. |
| **9** | `meta_dataset` | `ctl_watermark_state` | `dataset_id` | **1 : 1** | High-watermark tracking incremental extract boundaries, delta values, and timestamps. |
| **10** | `meta_dataset` | `meta_dataquality_rule` | `dataset_id` | **1 : Many** | Datasets can have multiple active data quality validation rules (null checks, regex, range). |
| **11** | `meta_ingestion_group` | `log_pipeline_run` | `ingestion_group_id` | **1 : Many** | Each pipeline run logs its overall orchestration metrics under its parent ingestion group. |
| **12** | `log_pipeline_run` | `log_dataset_run` | `pipeline_run_id` | **1 : Many** | A pipeline run orchestrates many dataset runs; tracks rows read, inserted, updated, and rejected. |
| **13** | `meta_dataset` | `log_dataset_run` | `dataset_id` | **1 : Many** | Every dataset execution is recorded against the master dataset catalog for historical audit. |
| **14** | `log_dataset_run` | `log_dq_rule_run` | `dataset_run_id` | **1 : Many** | Detailed DQ evaluation outcomes per rule evaluated during each specific dataset run. |
| **15** | `meta_dataquality_rule` | `log_dq_rule_run` | `dq_rule_id` | **1 : Many** | Historical execution performance and failure rates for each specific DQ rule. |
| **16** | `log_dataset_run` | `log_error_event` | `dataset_run_id` | **1 : Many** | Granular failure events, error codes, and exception stack traces captured per dataset run. |
| **17** | `log_pipeline_run` | `log_error_event` | `pipeline_run_id` | **1 : Many** | Orchestration-level pipeline failures not tied to a specific dataset (e.g. gateway timeouts). |

---

## 4. SQL DDL Specification (sqldb-meta-orch-dev)

![Metadata-Driven Ingestion Framework - Part 3](/Users/chandu/Documents/Python_practice/Fabric/images/17_metadata_driven_framework_ddl_spec_p3.png)

Execute this complete DDL script in your Microsoft Fabric SQL Database (`sqldb-meta-orch-dev`) to build the core schemas and tables.

### A. Schema Definitions

```sql
-- Create Schemas for Separation of Concerns
CREATE SCHEMA meta;
GO
CREATE SCHEMA ctl;
GO
CREATE SCHEMA log;
GO
CREATE SCHEMA stage;
GO
```

---

### B. Schema: meta (Configuration & Registry)

```sql
-- 1. Source Systems
CREATE TABLE meta.source_system (
    source_system_id BIGINT IDENTITY(1,1) CONSTRAINT PK_source_system PRIMARY KEY,
    source_system_code VARCHAR(50) NOT NULL CONSTRAINT UQ_source_system_code UNIQUE,
    source_system_name VARCHAR(200) NOT NULL,
    source_system_type VARCHAR(50) NOT NULL, -- 'AS400', 'SQL Server', 'REST API', 'File'
    is_active BIT NOT NULL CONSTRAINT DF_source_system_is_active DEFAULT 1,
    created_on DATETIME2 NOT NULL CONSTRAINT DF_source_system_created_on DEFAULT SYSUTCDATETIME(),
    updated_on DATETIME2 NULL
);
GO

-- 2. Execution Schedules
CREATE TABLE meta.schedule (
    schedule_id BIGINT IDENTITY(1,1) CONSTRAINT PK_schedule PRIMARY KEY,
    schedule_name VARCHAR(150) NOT NULL CONSTRAINT UQ_schedule_name UNIQUE,
    frequency_type VARCHAR(30) NOT NULL, -- 'Hourly', 'Daily', 'Weekly', 'Monthly'
    frequency_interval INT NOT NULL CONSTRAINT DF_schedule_interval DEFAULT 1,
    cron_expression VARCHAR(100) NULL,
    start_datetime DATETIME2 NOT NULL,
    end_datetime DATETIME2 NULL,
    timezone_name VARCHAR(100) NOT NULL CONSTRAINT DF_schedule_timezone DEFAULT 'UTC',
    is_active BIT NOT NULL CONSTRAINT DF_schedule_is_active DEFAULT 1,
    created_on DATETIME2 NOT NULL CONSTRAINT DF_schedule_created_on DEFAULT SYSUTCDATETIME(),
    updated_on DATETIME2 NULL
);
GO

-- 3. Ingestion Groups (Batch Execution Containers)
CREATE TABLE meta.ingestion_group (
    ingestion_group_id BIGINT IDENTITY(1,1) CONSTRAINT PK_ingestion_group PRIMARY KEY,
    group_code VARCHAR(50) NOT NULL CONSTRAINT UQ_group_code UNIQUE,
    group_name VARCHAR(200) NOT NULL,
    group_description VARCHAR(1000) NULL,
    schedule_id BIGINT NOT NULL CONSTRAINT FK_ingestion_group_schedule REFERENCES meta.schedule(schedule_id),
    orchestration_mode VARCHAR(20) NOT NULL CONSTRAINT DF_ingestion_group_mode DEFAULT 'Batch', -- 'Batch', 'NRT'
    is_active BIT NOT NULL CONSTRAINT DF_ingestion_group_is_active DEFAULT 1,
    created_on DATETIME2 NOT NULL CONSTRAINT DF_ingestion_group_created_on DEFAULT SYSUTCDATETIME(),
    updated_on DATETIME2 NULL
);
GO

-- 4. Master Dataset Registry
CREATE TABLE meta.dataset (
    dataset_id BIGINT IDENTITY(1,1) CONSTRAINT PK_dataset PRIMARY KEY,
    source_system_id BIGINT NOT NULL CONSTRAINT FK_dataset_source_system REFERENCES meta.source_system(source_system_id),
    dataset_name VARCHAR(200) NOT NULL CONSTRAINT UQ_dataset_name UNIQUE,
    dataset_description VARCHAR(1000) NULL,
    target_silver_table_name VARCHAR(200) NOT NULL,
    target_gold_table_name VARCHAR(200) NULL,
    is_active BIT NOT NULL CONSTRAINT DF_dataset_is_active DEFAULT 1,
    created_on DATETIME2 NOT NULL CONSTRAINT DF_dataset_created_on DEFAULT SYSUTCDATETIME(),
    updated_on DATETIME2 NULL
);
GO

-- 5. Ingestion Group to Dataset Mapping (Many-to-Many)
CREATE TABLE meta.ingestion_group_dataset (
    group_dataset_id BIGINT IDENTITY(1,1) CONSTRAINT PK_ingestion_group_dataset PRIMARY KEY,
    ingestion_group_id BIGINT NOT NULL CONSTRAINT FK_group_dataset_group REFERENCES meta.ingestion_group(ingestion_group_id),
    dataset_id BIGINT NOT NULL CONSTRAINT FK_group_dataset_dataset REFERENCES meta.dataset(dataset_id),
    is_mandatory_flag BIT NOT NULL CONSTRAINT DF_group_dataset_mandatory DEFAULT 1,
    is_active BIT NOT NULL CONSTRAINT DF_group_dataset_is_active DEFAULT 1,
    effective_from DATETIME2 NOT NULL CONSTRAINT DF_group_dataset_eff_from DEFAULT SYSUTCDATETIME(),
    effective_to DATETIME2 NULL,
    created_on DATETIME2 NOT NULL CONSTRAINT DF_group_dataset_created_on DEFAULT SYSUTCDATETIME(),
    updated_on DATETIME2 NULL
);
GO

-- 6. Stage Subtype: Source to Bronze Extraction
CREATE TABLE meta.dataset_src_to_brnz (
    dataset_id BIGINT CONSTRAINT PK_dataset_src_to_brnz PRIMARY KEY REFERENCES meta.dataset(dataset_id),
    source_schema_name VARCHAR(200) NULL,
    source_table_name VARCHAR(500) NULL,
    source_query VARCHAR(MAX) NULL,
    source_container_or_path VARCHAR(1000) NULL,
    source_file_pattern VARCHAR(500) NULL,
    source_file_path VARCHAR(500) NULL,
    source_file_name VARCHAR(500) NULL,
    column_delimiter VARCHAR(10) NULL,
    row_delimiter VARCHAR(10) NULL,
    destination_path VARCHAR(500) NOT NULL,
    destination_file_name_prefix VARCHAR(200) NOT NULL,
    destination_file_type VARCHAR(200) NOT NULL, -- 'CSV', 'PARQUET', 'EXCEL'
    bronze_schema_name VARCHAR(200) NOT NULL,
    bronze_table_name VARCHAR(200) NOT NULL,
    use_explicit_mapping BIT NOT NULL CONSTRAINT DF_src_to_brnz_mapping DEFAULT 0,
    key_columns VARCHAR(500) NULL,
    source_watermark_column VARCHAR(200) NULL,
    created_on DATETIME2 NOT NULL CONSTRAINT DF_src_to_brnz_created DEFAULT SYSUTCDATETIME(),
    updated_on DATETIME2 NULL
);
GO

-- 7. Stage Subtype: Bronze to Silver Transformation & Conforming
CREATE TABLE meta.dataset_brnz_to_silver (
    dataset_id BIGINT CONSTRAINT PK_dataset_brnz_to_silver PRIMARY KEY REFERENCES meta.dataset(dataset_id),
    source_table_lakehouse VARCHAR(200) NOT NULL,
    source_table_schema VARCHAR(200) NOT NULL,
    source_table_name VARCHAR(200) NOT NULL,
    target_table_lakehouse VARCHAR(200) NOT NULL,
    target_table_schema VARCHAR(200) NOT NULL,
    target_table_name VARCHAR(200) NOT NULL,
    key_columns VARCHAR(500) NOT NULL,
    data_type VARCHAR(200) NULL,
    merge_query VARCHAR(MAX) NULL,
    created_on DATETIME2 NOT NULL CONSTRAINT DF_brnz_to_silver_created DEFAULT SYSUTCDATETIME(),
    updated_on DATETIME2 NULL
);
GO

-- 8. Stage Subtype: Silver to Gold Dimensional Modeling
CREATE TABLE meta.dataset_silver_to_gold (
    dataset_id BIGINT CONSTRAINT PK_dataset_silver_to_gold PRIMARY KEY REFERENCES meta.dataset(dataset_id),
    target_gold_lakehouse VARCHAR(200) NOT NULL,
    target_gold_schema VARCHAR(200) NOT NULL,
    target_gold_table_name VARCHAR(200) NOT NULL,
    table_type VARCHAR(50) NOT NULL, -- 'Dimension', 'Fact', 'Bridge'
    scd_type VARCHAR(20) NOT NULL DEFAULT 'SCD1', -- 'SCD1', 'SCD2', 'Append'
    business_key_columns VARCHAR(500) NOT NULL,
    surrogate_key_name VARCHAR(100) NOT NULL,
    transformation_query VARCHAR(MAX) NULL,
    created_on DATETIME2 NOT NULL CONSTRAINT DF_silver_to_gold_created DEFAULT SYSUTCDATETIME(),
    updated_on DATETIME2 NULL
);
GO

-- 9. Data Quality Rules Engine Configuration
CREATE TABLE meta.dataquality_rule (
    rule_id BIGINT IDENTITY(1,1) CONSTRAINT PK_dataquality_rule PRIMARY KEY,
    dataset_id BIGINT NOT NULL CONSTRAINT FK_dq_rule_dataset REFERENCES meta.dataset(dataset_id),
    target_stage VARCHAR(50) NOT NULL, -- 'Bronze', 'Silver', 'Gold'
    column_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(100) NOT NULL, -- 'NOT_NULL', 'UNIQUE', 'REGEX', 'RANGE', 'REFERENTIAL'
    rule_expression VARCHAR(MAX) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'ERROR', -- 'WARNING', 'ERROR', 'CRITICAL'
    is_blocking BIT NOT NULL DEFAULT 1,
    is_active BIT NOT NULL DEFAULT 1,
    created_on DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
GO
```

---

### C. Schema: ctl (Operational State & Watermarks)

```sql
-- 1. High Watermark Tracking (Incremental Extraction)
CREATE TABLE ctl.watermark_state (
    watermark_id BIGINT IDENTITY(1,1) CONSTRAINT PK_watermark_state PRIMARY KEY,
    dataset_id BIGINT NOT NULL CONSTRAINT UQ_watermark_dataset UNIQUE REFERENCES meta.dataset(dataset_id),
    watermark_column_name VARCHAR(200) NOT NULL,
    watermark_value VARCHAR(255) NOT NULL, -- e.g., '2026-09-24 00:00:00' or '10845920'
    last_extracted_timestamp DATETIME2 NOT NULL CONSTRAINT DF_watermark_last_extracted DEFAULT SYSUTCDATETIME(),
    updated_on DATETIME2 NULL
);
GO

-- 2. Dataset Processing State
CREATE TABLE ctl.dataset_state (
    state_id BIGINT IDENTITY(1,1) CONSTRAINT PK_dataset_state PRIMARY KEY,
    dataset_id BIGINT NOT NULL CONSTRAINT UQ_dataset_state UNIQUE REFERENCES meta.dataset(dataset_id),
    current_status VARCHAR(50) NOT NULL DEFAULT 'IDLE', -- 'IDLE', 'RUNNING', 'FAILED', 'SUCCESS'
    last_successful_run_time DATETIME2 NULL,
    last_failed_run_time DATETIME2 NULL,
    consecutive_failure_count INT NOT NULL DEFAULT 0,
    updated_on DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
GO
```

---

### D. Schema: log (Execution Auditing & Metrics)

```sql
-- 1. Pipeline Run Audit Log
CREATE TABLE log.pipeline_run (
    pipeline_run_id BIGINT IDENTITY(1,1) CONSTRAINT PK_pipeline_run PRIMARY KEY,
    ingestion_group_id BIGINT NOT NULL REFERENCES meta.ingestion_group(ingestion_group_id),
    fabric_pipeline_id VARCHAR(255) NOT NULL,
    fabric_run_id VARCHAR(255) NOT NULL,
    run_status VARCHAR(50) NOT NULL, -- 'InProgress', 'Completed', 'Failed'
    start_time DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    end_time DATETIME2 NULL,
    total_datasets_count INT NOT NULL,
    success_datasets_count INT NULL,
    failed_datasets_count INT NULL,
    error_message VARCHAR(MAX) NULL
);
GO

-- 2. Individual Dataset Execution Metrics
CREATE TABLE log.dataset_run (
    dataset_run_id BIGINT IDENTITY(1,1) CONSTRAINT PK_dataset_run PRIMARY KEY,
    pipeline_run_id BIGINT NULL REFERENCES log.pipeline_run(pipeline_run_id),
    dataset_id BIGINT NOT NULL REFERENCES meta.dataset(dataset_id),
    stage_name VARCHAR(50) NOT NULL, -- 'Source_To_Bronze', 'Bronze_To_Silver', 'Silver_To_Gold'
    status VARCHAR(50) NOT NULL, -- 'Success', 'Failed', 'Skipped'
    start_time DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    end_time DATETIME2 NULL,
    duration_seconds AS DATEDIFF(SECOND, start_time, end_time),
    rows_read BIGINT NULL,
    rows_inserted BIGINT NULL,
    rows_updated BIGINT NULL,
    rows_deleted BIGINT NULL,
    rows_rejected BIGINT NULL,
    error_message VARCHAR(MAX) NULL
);
GO

-- 3. Data Quality Rule Evaluation Logs
CREATE TABLE log.dq_rule_run (
    dq_run_id BIGINT IDENTITY(1,1) CONSTRAINT PK_dq_rule_run PRIMARY KEY,
    dataset_run_id BIGINT NOT NULL REFERENCES log.dataset_run(dataset_run_id),
    rule_id BIGINT NOT NULL REFERENCES meta.dataquality_rule(rule_id),
    rule_status VARCHAR(20) NOT NULL, -- 'PASSED', 'FAILED', 'WARNING'
    failed_record_count BIGINT NOT NULL DEFAULT 0,
    evaluated_on DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- 4. Centralized Exception & Error Event Tracking
CREATE TABLE log.error_event (
    error_id BIGINT IDENTITY(1,1) CONSTRAINT PK_error_event PRIMARY KEY,
    dataset_id BIGINT NULL REFERENCES meta.dataset(dataset_id),
    activity_name VARCHAR(200) NOT NULL,
    error_code VARCHAR(100) NULL,
    error_description VARCHAR(MAX) NOT NULL,
    stack_trace VARCHAR(MAX) NULL,
    logged_on DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
GO
```

---

### E. Schema: stage (Excel Ingestion Staging Tables)

![Excel Template Dependencies & Staging DDL](/Users/chandu/Documents/Python_practice/Fabric/images/18_metadata_framework_excel_template_deps_p4.png)

```sql
-- Staging tables directly mirroring the 9 sheets in Ingestion_metadata_load_template.xlsx
CREATE TABLE stage.source_system (
    source_system_code VARCHAR(50),
    source_system_name VARCHAR(200),
    source_system_type VARCHAR(50),
    is_active VARCHAR(10)
);
GO

CREATE TABLE stage.schedule (
    schedule_name VARCHAR(150),
    frequency_type VARCHAR(30),
    frequency_interval VARCHAR(10),
    cron_expression VARCHAR(100),
    start_datetime VARCHAR(50),
    end_datetime VARCHAR(50),
    timezone_name VARCHAR(100),
    is_active VARCHAR(10)
);
GO

CREATE TABLE stage.ingestion_group (
    group_code VARCHAR(50),
    group_name VARCHAR(200),
    group_description VARCHAR(1000),
    schedule_name VARCHAR(150),
    orchestration_mode VARCHAR(20),
    is_active VARCHAR(10)
);
GO

CREATE TABLE stage.dataset (
    source_system_code VARCHAR(50),
    dataset_name VARCHAR(200),
    dataset_description VARCHAR(1000),
    target_silver_table_name VARCHAR(200),
    target_gold_table_name VARCHAR(200),
    is_active VARCHAR(10)
);
GO

CREATE TABLE stage.ingestion_group_dataset (
    group_code VARCHAR(50),
    dataset_name VARCHAR(200),
    is_mandatory_flag VARCHAR(10),
    is_active VARCHAR(10),
    effective_from VARCHAR(50)
);
GO

CREATE TABLE stage.dataset_src_to_brnz (
    dataset_name VARCHAR(200),
    source_schema_name VARCHAR(200),
    source_table_name VARCHAR(500),
    source_query VARCHAR(MAX),
    source_container_or_path VARCHAR(1000),
    source_file_pattern VARCHAR(500),
    source_file_path VARCHAR(500),
    source_file_name VARCHAR(500),
    column_delimiter VARCHAR(10),
    row_delimiter VARCHAR(10),
    destination_path VARCHAR(500),
    destination_file_name_prefix VARCHAR(200),
    destination_file_type VARCHAR(200),
    bronze_schema_name VARCHAR(200),
    bronze_table_name VARCHAR(200),
    use_explicit_mapping VARCHAR(10),
    key_columns VARCHAR(500),
    source_watermark_column VARCHAR(200)
);
GO

CREATE TABLE stage.dataset_brnz_to_silver (
    dataset_name VARCHAR(200),
    source_table_lakehouse VARCHAR(200),
    source_table_schema VARCHAR(200),
    source_table_name VARCHAR(200),
    target_table_lakehouse VARCHAR(200),
    target_table_schema VARCHAR(200),
    target_table_name VARCHAR(200),
    key_columns VARCHAR(500),
    data_type VARCHAR(200),
    merge_query VARCHAR(MAX),
    comments VARCHAR(1000),
    is_active VARCHAR(10),
    is_incremental VARCHAR(10),
    delete_col_name VARCHAR(200),
    duplication_check VARCHAR(10),
    notebook_pattern VARCHAR(200)
);
GO

CREATE TABLE stage.dataset_silver_to_gold (
    dataset_name VARCHAR(200),
    source_table_lakehouse VARCHAR(200),
    source_table_schema VARCHAR(200),
    source_table_name VARCHAR(200),
    target_table_lakehouse VARCHAR(200),
    target_table_schema VARCHAR(200),
    target_table_name VARCHAR(200),
    key_columns VARCHAR(500),
    surrogate_key_column_name VARCHAR(200),
    load_type_dim_or_fact VARCHAR(100),
    load_order VARCHAR(10),
    is_active VARCHAR(10),
    load_sp_name VARCHAR(200)
);
GO

CREATE TABLE stage.dataquality_rule (
    dataset_name VARCHAR(200),
    rule_name VARCHAR(200),
    rule_type VARCHAR(50),
    rule_expression VARCHAR(MAX),
    severity_code VARCHAR(20),
    threshold_percent VARCHAR(20),
    on_failure_action VARCHAR(50),
    is_active VARCHAR(10)
);
GO
```

---

## 5. Developer Operational Guide: Excel Load Template

Developers configure metadata parameters in `Ingestion_metadata_load_template.xlsx`. The workbook utilizes official Excel Tables (e.g., `tbl_dataset`) and built-in Data Validation dropdowns to guarantee referential integrity before the workbook is uploaded to Fabric.

![Worksheet Guidelines & Field Specifications](/Users/chandu/Documents/Python_practice/Fabric/images/19_metadata_framework_worksheet_guidelines_p5.png)

### 5.1 Dependency Order of Data Population

To maintain referential integrity across foreign keys, developers **must** populate worksheets in the strict top-down sequence illustrated below:

```mermaid
flowchart TD
    S1["Step 1: source_system\n(tbl_source_system)"] --> S3["Step 3: dataset\n(tbl_dataset)"]
    S2["Step 2: schedule\n(tbl_schedule)"] --> S4["Step 4: ingestion_group\n(tbl_ingestion_group)"]
    
    S3 --> S5["Step 5: ingestion_group_dataset\n(tbl_ingestion_group_dataset)"]
    S4 --> S5

    S5 --> S6["Step 6: src_to_brnz\n(tbl_dataset_src_to_brnz)"]
    S5 --> S7["Step 7: brnz_to_silv\n(tbl_dataset_brnz_to_silver)"]
    S5 --> S8["Step 8: silv_to_gold\n(tbl_dataset_silver_to_gold)"]
    S5 --> S9["Step 9: dataquality_rule\n(tbl_dataquality_rule)"]
```

---

### 5.2 Worksheet Guidelines & Field Specifications

#### Sheet 1: `source_system` (Table: `tbl_source_system`)
Defines the upstream source platform/database.
* `source_system_code` *(Required)*: Unique code identifying system (e.g., `AS400_PROD`, `SAP_ERP`).
* `source_system_name` *(Required)*: Full readable name (e.g., `IBM AS400 Production DB2`).
* `source_system_type` *(Required)*: Connection archetype (`AS400`, `SQLServer`, `REST_API`, `SFTP`).
* `is_active` *(Required)*: Select `TRUE` or `FALSE` from dropdown.

#### Sheet 2: `schedule` (Table: `tbl_schedule`)
Defines pipeline execution timers and cron triggers.
* `schedule_name` *(Required)*: Unique schedule name (e.g., `SCH_DAILY_0200_UTC`).
* `frequency_type` *(Required)*: Dropdown: `Hourly`, `Daily`, `Weekly`, `Monthly`.
* `frequency_interval` *(Required)*: Integer interval (e.g., `1` for every 1 day/hour).
* `cron_expression` *(Optional)*: Standard 5-field cron string (e.g., `0 2 * * *`).
* `start_datetime` *(Required)*: ISO start timestamp (e.g., `2026-01-01 00:00:00`).
* `timezone_name` *(Required)*: Timezone string (default: `UTC`).
* `is_active` *(Required)*: `TRUE` / `FALSE`.

#### Sheet 3: `ingestion_group` (Table: `tbl_ingestion_group`)
Groups related datasets into an orchestrated execution unit.
* `group_code` *(Required)*: Unique group identifier (e.g., `GRP_AS400_FINANCE_DAILY`).
* `group_name` *(Required)*: Descriptive group name.
* `schedule_name` *(Required)*: Select existing schedule from dropdown (`=ScheduleNames`).
* `orchestration_mode` *(Required)*: Dropdown: `Batch` or `NRT`.
* `is_active` *(Required)*: `TRUE` / `FALSE`.

#### Sheet 4: `dataset` (Table: `tbl_dataset`)
The master registry sheet for all managed dataset entities.
* `source_system_code` *(Required)*: Select source system from dropdown (`=SourceSystemCodes`).
* `dataset_name` *(Required)*: Globally unique entity identifier (e.g., `as400_custmst`).
* `dataset_description` *(Optional)*: Business/technical description.
* `target_silver_table_name` *(Required)*: Name of target Silver table (e.g., `silver_customer`).
* `target_gold_table_name` *(Optional)*: Name of target Gold table (e.g., `dim_customer`).
* `is_active` *(Required)*: `TRUE` / `FALSE`.

#### Sheet 5: `ingestion_group_dataset` (Table: `tbl_ingestion_group_dataset`)
Maps datasets to execution groups with effective dating.
* `group_code` *(Required)*: Select group from dropdown (`=GroupCodes`).
* `dataset_name` *(Required)*: Select dataset from dropdown (`=DatasetNames`).
* `is_mandatory_flag` *(Required)*: `TRUE` (group aborts if dataset fails) or `FALSE`.
* `is_active` *(Required)*: `TRUE` / `FALSE`.
* `effective_from` *(Required)*: Active start timestamp.

#### Sheet 6: `dataset_src_to_brnz` (Table: `tbl_dataset_src_to_brnz`)
Configures source extraction and raw landing in Bronze Lakehouse.
* `dataset_name` *(Required)*: Dropdown (`=DatasetNames`).
* `source_schema_name` *(Optional)*: DB schema/library name in AS400 (e.g., `LIBPRD`).
* `source_table_name` *(Optional)*: DB table name in AS400 (e.g., `CUSTMST`).
* `source_query` *(Optional)*: Custom SQL override query for extraction.
* `destination_path` *(Required)*: Landing container/path (e.g., `bronze/as400/custmst/`).
* `destination_file_name_prefix` *(Required)*: File prefix (e.g., `custmst_raw`).
* `destination_file_type` *(Required)*: `PARQUET` or `CSV`.
* `bronze_schema_name` *(Required)*: Bronze Lakehouse schema (e.g., `bronze_as400`).
* `bronze_table_name` *(Required)*: Bronze Lakehouse table (e.g., `custmst`).
* `use_explicit_mapping` *(Required)*: `FALSE` (auto schema drift) or `TRUE`.
* `key_columns` *(Optional)*: Business primary keys comma separated (e.g., `CUSNO`).
* `source_watermark_column` *(Optional)*: Timestamp/numeric column for incremental load (e.g., `UPDDAT`).

#### Sheet 7: `dataset_brnz_to_silver` (Table: `tbl_dataset_brnz_to_silver`)
Configures Bronze $\rightarrow$ Silver PySpark cleansing, deduplication, and Delta merge.
* `dataset_name` *(Required)*: Dropdown (`=DatasetNames`).
* `source_table_lakehouse` *(Required)*: Bronze Lakehouse name.
* `source_table_schema` *(Required)*: Bronze schema name.
* `source_table_name` *(Required)*: Bronze table name.
* `target_table_lakehouse` *(Required)*: Silver Lakehouse name.
* `target_table_schema` *(Required)*: Silver schema name.
* `target_table_name` *(Required)*: Silver table name.
* `key_columns` *(Required)*: Primary key(s) for Delta MERGE (e.g., `customer_id`).
* `is_incremental` *(Required)*: `TRUE` (incremental merge) or `FALSE` (full overwrite).
* `duplication_check` *(Required)*: `TRUE` (deduplicate on `key_columns` prior to write).
* `notebook_pattern` *(Optional)*: Custom notebook pattern name (e.g., `pattern_standard_merge`).

#### Sheet 8: `dataset_silver_to_gold` (Table: `tbl_dataset_silver_to_gold`)
Configures Silver $\rightarrow$ Gold dimensional modeling.
* `dataset_name` *(Required)*: Dropdown (`=DatasetNames`).
* `source_table_lakehouse` *(Required)*: Silver Lakehouse name.
* `target_table_name` *(Required)*: Gold table name (e.g., `dim_customer`).
* `key_columns` *(Required)*: Business keys.
* `surrogate_key_column_name` *(Optional)*: Generated SK name (e.g., `customer_sk`).
* `load_type_dim_or_fact` *(Required)*: Dropdown: `Dimension` or `Fact`.
* `load_order` *(Required)*: Integer execution priority (e.g., `10` for Dimensions, `20` for Facts).
* `load_sp_name` *(Optional)*: Stored procedure name if T-SQL driven.

#### Sheet 9: `dataquality_rule` (Table: `tbl_dataquality_rule`)
Defines data quality evaluation rules enforced during Bronze $\rightarrow$ Silver transition.
* `dataset_name` *(Required)*: Dropdown (`=DatasetNames`).
* `rule_name` *(Required)*: Unique rule code (e.g., `DQ_CUST_ID_NOT_NULL`).
* `rule_type` *(Required)*: `NullCheck`, `RangeCheck`, `DuplicateCheck`, `CustomSQL`.
* `rule_expression` *(Required)*: PySpark filter or SQL condition (e.g., `customer_id IS NOT NULL`).
* `severity_code` *(Required)*: Dropdown: `WARN`, `REJECT`, `STOP`.
* `threshold_percent` *(Required)*: Max allowed failure % (e.g., `0.00` for 0%).
* `on_failure_action` *(Required)*: `Warn`, `Quarantine Rows`, `Abort Pipeline`.

---

### 5.3 Data Validation Rules Summary

![Data Validation Rules & Upsert Flow](/Users/chandu/Documents/Python_practice/Fabric/images/20_metadata_framework_validation_rules_staging_p6.png)

| Target Sheet | Column Name | Validation Type | Formula / Allowed List |
| :--- | :--- | :--- | :--- |
| **All Sheets** | `is_active`, `is_mandatory_flag`, etc. | List | `TRUE, FALSE` |
| **`schedule`** | `frequency_type` | List | `Hourly, Daily, Weekly, Monthly` |
| **`ingestion_group`** | `schedule_name` | Relational Dropdown | `=ScheduleNames` |
| **`ingestion_group`** | `orchestration_mode` | List | `Batch, NRT` |
| **`dataset`** | `source_system_code` | Relational Dropdown | `=SourceSystemCodes` |
| **`ingestion_group_dataset`** | `group_code` | Relational Dropdown | `=GroupCodes` |
| **`ingestion_group_dataset`** | `dataset_name` | Relational Dropdown | `=DatasetNames` |
| **`dataset_src_to_brnz`** | `dataset_name` | Relational Dropdown | `=DatasetNames` |
| **`dataset_brnz_to_silver`** | `dataset_name` | Relational Dropdown | `=DatasetNames` |
| **`dataset_silver_to_gold`** | `dataset_name` | Relational Dropdown | `=DatasetNames` |
| **`dataset_silver_to_gold`** | `load_type_dim_or_fact` | List | `Dimension, Fact` |
| **`dataquality_rule`** | `dataset_name` | Relational Dropdown | `=DatasetNames` |
| **`dataquality_rule`** | `severity_code` | List | `WARN, REJECT, STOP` |

---

## 6. Automated Staging & Upsert Workflow

### 6.1 Orchestration Workflow

When an engineer uploads `Ingestion_metadata_load_template.xlsx` to the workspace storage folder, a Fabric Data Factory pipeline executes the following automated pipeline:

```mermaid
flowchart TD
    A["1. Truncate all tables in stage schema"] --> B["2. Fabric Copy Activity: Excel Tables -> stage Schema Tables\n• tbl_source_system -> stage.source_system\n• tbl_dataset -> stage.dataset\n• tbl_dataset_src_to_brnz -> stage.dataset_src_to_brnz\n• ... (all 9 tables)"]
    B --> C["3. Execute Stored Procedure: stage.sp_UpsertMetadataFromStage\n• Resolves business codes to surrogate IDs on the fly\n• Executes T-SQL MERGE into meta & ctl tables"]
```

---

### 6.2 Production Upsert Stored Procedure Script (`stage.sp_UpsertMetadataFromStage`)

![Production Stored Procedure Script - Part 1](/Users/chandu/Documents/Python_practice/Fabric/images/21_metadata_framework_upsert_sp_merges_part1_p7.png)

![Production Stored Procedure Script - Part 2](/Users/chandu/Documents/Python_practice/Fabric/images/22_metadata_framework_upsert_sp_merges_part2_p8.png)

```sql
CREATE OR ALTER PROCEDURE stage.sp_UpsertMetadataFromStage
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;

    TRY
        -- =====================================================================
        -- 1. MERGE Source Systems
        -- =====================================================================
        MERGE INTO meta.source_system AS Target
        USING (
            SELECT 
                source_system_code, 
                source_system_name, 
                source_system_type,
                CASE WHEN UPPER(is_active) = 'TRUE' THEN 1 ELSE 0 END AS is_active
            FROM stage.source_system
        ) AS Source ON Target.source_system_code = Source.source_system_code
        WHEN MATCHED THEN
            UPDATE SET 
                Target.source_system_name = Source.source_system_name,
                Target.source_system_type = Source.source_system_type,
                Target.is_active = Source.is_active,
                Target.updated_on = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (source_system_code, source_system_name, source_system_type, is_active, created_on)
            VALUES (Source.source_system_code, Source.source_system_name, Source.source_system_type, Source.is_active, SYSUTCDATETIME());

        -- =====================================================================
        -- 2. MERGE Schedules
        -- =====================================================================
        MERGE INTO meta.schedule AS Target
        USING (
            SELECT 
                schedule_name, 
                frequency_type,
                CAST(frequency_interval AS INT) AS frequency_interval,
                cron_expression,
                CAST(start_datetime AS DATETIME2) AS start_datetime,
                CASE WHEN end_datetime IS NULL OR end_datetime = '' THEN NULL ELSE CAST(end_datetime AS DATETIME2) END AS end_datetime,
                ISNULL(timezone_name, 'UTC') AS timezone_name,
                CASE WHEN UPPER(is_active) = 'TRUE' THEN 1 ELSE 0 END AS is_active
            FROM stage.schedule
        ) AS Source ON Target.schedule_name = Source.schedule_name
        WHEN MATCHED THEN
            UPDATE SET 
                Target.frequency_type = Source.frequency_type,
                Target.frequency_interval = Source.frequency_interval,
                Target.cron_expression = Source.cron_expression,
                Target.start_datetime = Source.start_datetime,
                Target.end_datetime = Source.end_datetime,
                Target.timezone_name = Source.timezone_name,
                Target.is_active = Source.is_active,
                Target.updated_on = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (schedule_name, frequency_type, frequency_interval, cron_expression, start_datetime, end_datetime, timezone_name, is_active, created_on)
            VALUES (Source.schedule_name, Source.frequency_type, Source.frequency_interval, Source.cron_expression, Source.start_datetime, Source.end_datetime, Source.timezone_name, Source.is_active, SYSUTCDATETIME());

        -- =====================================================================
        -- 3. MERGE Ingestion Groups
        -- =====================================================================
        MERGE INTO meta.ingestion_group AS Target
        USING (
            SELECT 
                stg.group_code, 
                stg.group_name, 
                stg.group_description, 
                sch.schedule_id, 
                stg.orchestration_mode,
                CASE WHEN UPPER(stg.is_active) = 'TRUE' THEN 1 ELSE 0 END AS is_active
            FROM stage.ingestion_group stg
            INNER JOIN meta.schedule sch ON stg.schedule_name = sch.schedule_name
        ) AS Source ON Target.group_code = Source.group_code
        WHEN MATCHED THEN
            UPDATE SET 
                Target.group_name = Source.group_name,
                Target.group_description = Source.group_description,
                Target.schedule_id = Source.schedule_id,
                Target.orchestration_mode = Source.orchestration_mode,
                Target.is_active = Source.is_active,
                Target.updated_on = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (group_code, group_name, group_description, schedule_id, orchestration_mode, is_active, created_on)
            VALUES (Source.group_code, Source.group_name, Source.group_description, Source.schedule_id, Source.orchestration_mode, Source.is_active, SYSUTCDATETIME());

        -- =====================================================================
        -- 4. MERGE Master Dataset Registry
        -- =====================================================================
        MERGE INTO meta.dataset AS Target
        USING (
            SELECT 
                scs.source_system_id, 
                stg.dataset_name, 
                stg.dataset_description, 
                stg.target_silver_table_name, 
                stg.target_gold_table_name,
                CASE WHEN UPPER(stg.is_active) = 'TRUE' THEN 1 ELSE 0 END AS is_active
            FROM stage.dataset stg
            INNER JOIN meta.source_system scs ON stg.source_system_code = scs.source_system_code
        ) AS Source ON Target.dataset_name = Source.dataset_name
        WHEN MATCHED THEN
            UPDATE SET 
                Target.source_system_id = Source.source_system_id,
                Target.dataset_description = Source.dataset_description,
                Target.target_silver_table_name = Source.target_silver_table_name,
                Target.target_gold_table_name = Source.target_gold_table_name,
                Target.is_active = Source.is_active,
                Target.updated_on = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (source_system_id, dataset_name, dataset_description, target_silver_table_name, target_gold_table_name, is_active, created_on)
            VALUES (Source.source_system_id, Source.dataset_name, Source.dataset_description, Source.target_silver_table_name, Source.target_gold_table_name, Source.is_active, SYSUTCDATETIME());

        -- Auto-initialize ctl.dataset_state entry for newly created datasets
        INSERT INTO ctl.dataset_state (dataset_id, current_status, updated_on)
        SELECT d.dataset_id, 'READY', SYSUTCDATETIME()
        FROM meta.dataset d
        LEFT JOIN ctl.dataset_state s ON d.dataset_id = s.dataset_id
        WHERE s.dataset_id IS NULL;

        -- Auto-initialize ctl.watermark_state entry for newly created datasets
        INSERT INTO ctl.watermark_state (dataset_id, watermark_column_name, watermark_value, last_extracted_timestamp)
        SELECT d.dataset_id, 'Datetime', '0', SYSUTCDATETIME()
        FROM meta.dataset d
        LEFT JOIN ctl.watermark_state w ON d.dataset_id = w.dataset_id
        WHERE w.dataset_id IS NULL;

        -- =====================================================================
        -- 5. MERGE Ingestion Group Dataset Mapping
        -- =====================================================================
        MERGE INTO meta.ingestion_group_dataset AS Target
        USING (
            SELECT 
                grp.ingestion_group_id, 
                ds.dataset_id,
                CASE WHEN UPPER(stg.is_mandatory_flag) = 'TRUE' THEN 1 ELSE 0 END AS is_mandatory_flag,
                CASE WHEN UPPER(stg.is_active) = 'TRUE' THEN 1 ELSE 0 END AS is_active,
                CAST(stg.effective_from AS DATETIME2) AS effective_from
            FROM stage.ingestion_group_dataset stg
            INNER JOIN meta.ingestion_group grp ON stg.group_code = grp.group_code
            INNER JOIN meta.dataset ds ON stg.dataset_name = ds.dataset_name
        ) AS Source ON Target.ingestion_group_id = Source.ingestion_group_id AND Target.dataset_id = Source.dataset_id
        WHEN MATCHED THEN
            UPDATE SET 
                Target.is_mandatory_flag = Source.is_mandatory_flag,
                Target.is_active = Source.is_active,
                Target.effective_from = Source.effective_from,
                Target.updated_on = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (ingestion_group_id, dataset_id, is_mandatory_flag, is_active, effective_from, created_on)
            VALUES (Source.ingestion_group_id, Source.dataset_id, Source.is_mandatory_flag, Source.is_active, Source.effective_from, SYSUTCDATETIME());

        -- =====================================================================
        -- 6. MERGE Subtype: meta.dataset_src_to_brnz
        -- =====================================================================
        MERGE INTO meta.dataset_src_to_brnz AS Target
        USING (
            SELECT 
                ds.dataset_id, 
                stg.source_schema_name, 
                stg.source_table_name, 
                stg.source_query,
                stg.source_container_or_path, 
                stg.source_file_pattern, 
                stg.source_file_path, 
                stg.source_file_name,
                stg.column_delimiter, 
                stg.row_delimiter, 
                stg.destination_path, 
                stg.destination_file_name_prefix,
                stg.destination_file_type, 
                stg.bronze_schema_name, 
                stg.bronze_table_name,
                CASE WHEN UPPER(stg.use_explicit_mapping) = 'TRUE' THEN 1 ELSE 0 END AS use_explicit_mapping,
                stg.key_columns, 
                stg.source_watermark_column
            FROM stage.dataset_src_to_brnz stg
            INNER JOIN meta.dataset ds ON stg.dataset_name = ds.dataset_name
        ) AS Source ON Target.dataset_id = Source.dataset_id
        WHEN MATCHED THEN
            UPDATE SET 
                Target.source_schema_name = Source.source_schema_name,
                Target.source_table_name = Source.source_table_name,
                Target.source_query = Source.source_query,
                Target.source_container_or_path = Source.source_container_or_path,
                Target.source_file_pattern = Source.source_file_pattern,
                Target.source_file_path = Source.source_file_path,
                Target.source_file_name = Source.source_file_name,
                Target.column_delimiter = Source.column_delimiter,
                Target.row_delimiter = Source.row_delimiter,
                Target.destination_path = Source.destination_path,
                Target.destination_file_name_prefix = Source.destination_file_name_prefix,
                Target.destination_file_type = Source.destination_file_type,
                Target.bronze_schema_name = Source.bronze_schema_name,
                Target.bronze_table_name = Source.bronze_table_name,
                Target.use_explicit_mapping = Source.use_explicit_mapping,
                Target.key_columns = Source.key_columns,
                Target.source_watermark_column = Source.source_watermark_column,
                Target.updated_on = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (
                dataset_id, source_schema_name, source_table_name, source_query,
                source_container_or_path, source_file_pattern, source_file_path, source_file_name,
                column_delimiter, row_delimiter, destination_path, destination_file_name_prefix,
                destination_file_type, bronze_schema_name, bronze_table_name, use_explicit_mapping,
                key_columns, source_watermark_column, created_on
            )
            VALUES (
                Source.dataset_id, Source.source_schema_name, Source.source_table_name, Source.source_query,
                Source.source_container_or_path, Source.source_file_pattern, Source.source_file_path, Source.source_file_name,
                Source.column_delimiter, Source.row_delimiter, Source.destination_path, Source.destination_file_name_prefix,
                Source.destination_file_type, Source.bronze_schema_name, Source.bronze_table_name, Source.use_explicit_mapping,
                Source.key_columns, Source.source_watermark_column, SYSUTCDATETIME()
            );

        -- =====================================================================
        -- 7. MERGE Subtype: meta.dataset_brnz_to_silver
        -- =====================================================================
        MERGE INTO meta.dataset_brnz_to_silver AS Target
        USING (
            SELECT 
                ds.dataset_id, 
                stg.source_table_lakehouse, 
                stg.source_table_schema, 
                stg.source_table_name,
                stg.target_table_lakehouse, 
                stg.target_table_schema, 
                stg.target_table_name,
                stg.key_columns, 
                stg.data_type, 
                stg.merge_query,
                CASE WHEN UPPER(stg.is_active) = 'TRUE' THEN 1 ELSE 0 END AS is_active
            FROM stage.dataset_brnz_to_silver stg
            INNER JOIN meta.dataset ds ON stg.dataset_name = ds.dataset_name
        ) AS Source ON Target.dataset_id = Source.dataset_id
        WHEN MATCHED THEN
            UPDATE SET 
                Target.source_table_lakehouse = Source.source_table_lakehouse,
                Target.source_table_schema = Source.source_table_schema,
                Target.source_table_name = Source.source_table_name,
                Target.target_table_lakehouse = Source.target_table_lakehouse,
                Target.target_table_schema = Source.target_table_schema,
                Target.target_table_name = Source.target_table_name,
                Target.key_columns = Source.key_columns,
                Target.data_type = Source.data_type,
                Target.merge_query = Source.merge_query,
                Target.updated_on = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (
                dataset_id, source_table_lakehouse, source_table_schema, source_table_name,
                target_table_lakehouse, target_table_schema, target_table_name,
                key_columns, data_type, merge_query, created_on
            )
            VALUES (
                Source.dataset_id, Source.source_table_lakehouse, Source.source_table_schema, Source.source_table_name,
                Source.target_table_lakehouse, Source.target_table_schema, Source.target_table_name,
                Source.key_columns, Source.data_type, Source.merge_query, SYSUTCDATETIME()
            );

        -- =====================================================================
        -- 8. MERGE Subtype: meta.dataset_silver_to_gold
        -- =====================================================================
        MERGE INTO meta.dataset_silver_to_gold AS Target
        USING (
            SELECT 
                ds.dataset_id,
                stg.target_table_lakehouse AS target_gold_lakehouse,
                stg.target_table_schema AS target_gold_schema,
                stg.target_table_name AS target_gold_table_name,
                ISNULL(stg.load_type_dim_or_fact, 'Dimension') AS table_type,
                'SCD1' AS scd_type,
                stg.key_columns AS business_key_columns,
                ISNULL(stg.surrogate_key_column_name, 'sk_' + ds.dataset_name) AS surrogate_key_name
            FROM stage.dataset_silver_to_gold stg
            INNER JOIN meta.dataset ds ON stg.dataset_name = ds.dataset_name
        ) AS Source ON Target.dataset_id = Source.dataset_id
        WHEN MATCHED THEN
            UPDATE SET 
                Target.target_gold_lakehouse = Source.target_gold_lakehouse,
                Target.target_gold_schema = Source.target_gold_schema,
                Target.target_gold_table_name = Source.target_gold_table_name,
                Target.table_type = Source.table_type,
                Target.business_key_columns = Source.business_key_columns,
                Target.surrogate_key_name = Source.surrogate_key_name,
                Target.updated_on = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (dataset_id, target_gold_lakehouse, target_gold_schema, target_gold_table_name, table_type, scd_type, business_key_columns, surrogate_key_name, created_on)
            VALUES (Source.dataset_id, Source.target_gold_lakehouse, Source.target_gold_schema, Source.target_gold_table_name, Source.table_type, Source.scd_type, Source.business_key_columns, Source.surrogate_key_name, SYSUTCDATETIME());

        -- =====================================================================
        -- 9. MERGE meta.dataquality_rule
        -- =====================================================================
        MERGE INTO meta.dataquality_rule AS Target
        USING (
            SELECT 
                ds.dataset_id,
                stg.rule_name,
                stg.rule_type,
                stg.rule_expression,
                stg.severity_code,
                CAST(ISNULL(stg.threshold_percent, '0.00') AS DECIMAL(5,2)) AS threshold_percent,
                ISNULL(stg.on_failure_action, 'Warn') AS on_failure_action,
                CASE WHEN UPPER(stg.is_active) = 'TRUE' THEN 1 ELSE 0 END AS is_active
            FROM stage.dataquality_rule stg
            INNER JOIN meta.dataset ds ON stg.dataset_name = ds.dataset_name
        ) AS Source ON Target.dataset_id = Source.dataset_id AND Target.rule_name = Source.rule_name
        WHEN MATCHED THEN
            UPDATE SET 
                Target.rule_type = Source.rule_type,
                Target.rule_expression = Source.rule_expression,
                Target.severity = Source.severity_code,
                Target.threshold_percent = Source.threshold_percent,
                Target.on_failure_action = Source.on_failure_action,
                Target.is_active = Source.is_active,
                Target.updated_on = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (dataset_id, rule_name, rule_type, rule_expression, severity, threshold_percent, on_failure_action, is_active, created_on)
            VALUES (Source.dataset_id, Source.rule_name, Source.rule_type, Source.rule_expression, Source.severity_code, Source.threshold_percent, Source.on_failure_action, Source.is_active, SYSUTCDATETIME());

        COMMIT TRANSACTION;
        PRINT 'Metadata upsert completed successfully.';
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        INSERT INTO log.error_event (activity_name, error_code, error_description, stack_trace, logged_on)
        VALUES (
            'stage.sp_UpsertMetadataFromStage',
            CAST(ERROR_NUMBER() AS VARCHAR(100)),
            ERROR_MESSAGE(),
            ERROR_PROCEDURE() + ' (Line ' + CAST(ERROR_LINE() AS VARCHAR(10)) + ')',
            SYSUTCDATETIME()
        );

        THROW;
    END CATCH
END;
GO
```

![Production Stored Procedure Script - Part 3](/Users/chandu/Documents/Python_practice/Fabric/images/23_metadata_framework_upsert_sp_merges_part3_p9.png)

---

## 7. Developer Operational Walkthrough: Adding a New Dataset

To onboard a new IBM AS400 DB2 table (e.g., `PRODDTA.F0101` - Address Book Master) into the Microsoft Fabric Medallion Architecture:

### Step 1: Open the Metadata Template
Open `Ingestion_metadata_load_template.xlsx` and populate sheets in dependency order:
1. **`dataset` tab**:
   * `source_system_code`: `AS400_PROD`
   * `dataset_name`: `as400_f0101_address_book`
   * `target_silver_table_name`: `silver_f0101_address_book`
   * `target_gold_table_name`: `dim_customer`
   * `is_active`: `TRUE`
2. **`dataset_src_to_brnz` tab**:
   * `source_schema_name`: `PRODDTA`
   * `source_table_name`: `F0101`
   * `source_query`: `SELECT ABAN8, ABALPH, ABAT1, ABTAX, ABUPMJ FROM PRODDTA.F0101 WHERE ABUPMJ >= ?`
   * `destination_path`: `Files/Bronze/AS400/F0101/`
   * `destination_file_name_prefix`: `f0101_raw`
   * `destination_file_type`: `PARQUET`
   * `bronze_schema_name`: `bronze`
   * `bronze_table_name`: `raw_f0101`
   * `key_columns`: `ABAN8`
   * `source_watermark_column`: `ABUPMJ`
3. **`dataset_brnz_to_silver` tab**:
   * Destination: Silver Lakehouse table `silver_f0101_address_book`
   * Primary business keys: `ABAN8`
   * `is_incremental`: `TRUE`
   * `duplication_check`: `TRUE`
   * MERGE condition:
     ```sql
     MERGE INTO silver_f0101_address_book AS tgt
     USING staging_updates AS src
     ON tgt.address_number = src.ABAN8
     WHEN MATCHED THEN UPDATE SET ...
     WHEN NOT MATCHED THEN INSERT ...
     ```

### Step 2: Upload and Staging Pipeline Execution
Upload `Ingestion_metadata_load_template.xlsx` to the workspace `Files/metadata_templates/` folder. The Fabric orchestration pipeline runs:
1. Truncates all `stage.*` tables.
2. Loads Excel sheets into corresponding `stage` tables.
3. Calls `EXEC stage.sp_UpsertMetadataFromStage;` which executes the atomic `MERGE` transactions, populating `meta.dataset`, the subtype tables, and automatically inserting baseline readiness records into `ctl.dataset_state` and `ctl.watermark_state`.

### Step 3: Trigger Master Ingestion Pipeline
The master Fabric Data Pipeline executes dynamically:
1. Queries `meta.dataset` joined with `ctl.watermark_state` to fetch active datasets and last processed watermarks.
2. Extracts incremental records from IBM AS400 DB2 via the On-Premises Data Gateway into Bronze Parquet files.
3. Invokes PySpark Silver cleansing notebook, applying deduplication and data quality validation rules.
4. Executes incremental Delta Lake merge into Silver.
5. Updates `ctl.watermark_state` with the latest extracted timestamp and logs execution telemetry into `log.dataset_run`.

---

## 8. Enterprise Dataset Topology & Ingestion Group Strategy (97 Tables)

In your modernization framework, the total operational scope comprises **97 AS400/DB2 tables** split into two parallel architectural streams:

* **Batch Ingestion (Fabric ODBC Pipeline)**: **58 Tables** (43 Dimensions + 15 Facts) running twice daily (09:00 AM & 05:00 PM CET).
* **NRT Ingestion (Fivetran $\rightarrow$ ADLS Gen2 $\rightarrow$ Lakehouse Shortcut)**: **39 Tables** (3 Dimensions + 36 Facts) running every 10 minutes.

![AS400 Dataset Topology & Batch/NRT Dual Paths](/Users/chandu/Documents/Python_practice/Fabric/images/24_as400_dataset_topology_and_ingestion_groups_p10.png)

### 8.1 Batch vs. NRT Dual-Path Ingestion

```mermaid
flowchart TD
    SOURCE[("Source: IBM AS400 DB2 (IPSPROD)")]

    subgraph PATH1["Path 1: Batch Ingestion (Twice Daily: 09:00 & 17:00 CET)"]
        BATCH_SRC["58 Batch Tables (ODBC)\n(43 Dimensions + 15 Facts)"]
        COPY_ACT["Fabric Pipeline ODBC Copy Activity"]
        LH_BRONZE["Lakehouse Bronze (Raw Files)"]
        SPARK_LOAD["Fabric PySpark Load"]
        LH_SILVER_BATCH["Lakehouse Silver (Conformed Delta)"]

        BATCH_SRC --> COPY_ACT --> LH_BRONZE --> SPARK_LOAD --> LH_SILVER_BATCH
    end

    subgraph PATH2["Path 2: Near Real-Time (NRT) Pipeline (10 Min Schedule)"]
        NRT_SRC["39 NRT Tables (CDC)\n(3 Dimensions + 36 Facts)"]
        FIVETRAN["Fivetran Continuous CDC Sync"]
        ADLS["ADLS Gen2 Container"]
        SHORTCUT["OneLake External Shortcut"]
        LH_BRONZE_SHORTCUT["Lakehouse Bronze (Shortcut)"]
        SPARK_MERGE["Fabric PySpark MERGE"]
        LH_SILVER_NRT["Lakehouse Silver (Conformed Delta)"]

        NRT_SRC --> FIVETRAN --> ADLS --> SHORTCUT --> LH_BRONZE_SHORTCUT --> SPARK_MERGE --> LH_SILVER_NRT
    end

    SOURCE --> BATCH_SRC
    SOURCE --> NRT_SRC

    LH_SILVER_BATCH --> GOLD[("Lakehouse Gold (Star Schema)\nDirect Lake / Power BI")]
    LH_SILVER_NRT --> GOLD
```

> [!TIP]
> **On-Premises Data Gateway (OPDG) Infrastructure Setup:**  
> For the 58 batch tables extracted via the Fabric ODBC Copy Pipeline, secure hybrid connectivity to IBM AS400 DB2 (`10.242.2.25`) is established using the standard On-Premises Data Gateway (`gwips-fabric-prod-01`) and the official 64-bit IBM i Access (ACS) ODBC Driver. For the complete VM prerequisites, network firewall port validation (446, 449, 8471), gateway tuning (`SpoolingDirectory`), and Fabric connection setup (`conn-as400-db2-prod`), see:  
> 👉 **[On-Premises Data Gateway Installation & Configuration Guide](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_On_Premises_Data_Gateway_Installation_and_Configuration_Guide.md)**.

---


### 8.2 Key Architectural Justifications

Splitting the batch pipeline into two separate ingestion groups (`IG_AS400_BATCH_DIM` and `IG_AS400_BATCH_FACT`) is an **industry best practice** for metadata-driven frameworks:

1. **Strict Dependency Order (Dimensions First, Facts Second)**:
   - In any Medallion / Star Schema architecture, **Dimension tables must land and process before Fact tables** so that foreign key lookups and surrogate key generation in Silver/Gold succeed without creating orphaned fact records.
   - Separate ingestion groups allow chained pipeline execution: `IG_AS400_BATCH_DIM` finishes successfully $\rightarrow$ automatically triggers `IG_AS400_BATCH_FACT`.

2. **Stateless vs. Stateful Processing**:
   - **Dimensions (Truncate & Load)**: Fast, stateless, and idempotent. If a dimension load fails, re-running the group cleanly overwrites the target without data skew.
   - **Facts (Incremental via Watermark)**: Stateful. Requires querying `ctl.watermark_state`, generating dynamic source queries (e.g., `WHERE UPDDAT >= ?`), and advancing `ctl.watermark_state` post-commit.

3. **Resource Allocation & Source Database Load Control**:
   - **43 Master/Dimension Tables**: Executed with **high parallelism** (10–15 concurrent threads in Fabric Copy Activity) since full loads on smaller lookup tables generate negligible overhead on `IPSPROD`.
   - **15 Fact Tables**: Query large transactional ledgers on AS400 over ODBC and must be throttled (3–5 concurrent threads) to prevent connection pool exhaustion and database locks on `IPSPROD`.

#### Recommended Strategy for NRT Tables (36 Facts, 3 Master/Dimensions)
For NRT tables, **Fivetran handles the heavy lifting** of extracting CDC micro-batch logs from AS400 into ADLS Gen2. Microsoft Fabric accesses these raw files via **OneLake External Shortcuts**.
* **Zero ODBC Copy Activity overhead in Fabric**: Fabric pipelines never issue ad-hoc queries against AS400 for NRT tables.
* **Micro-batch Silver Delta MERGE**: Every 10 minutes, a Fabric PySpark notebook reads `meta.dataset_brnz_to_silver` and executes a dynamic `MERGE INTO silver_table USING bronze_shortcut ON key_columns`.
* **Watermark & File Batch Tracking**: The 10-minute trigger tracks the high-watermark timestamp or file batch ID in `ctl.watermark_state` to ensure only newly arrived Fivetran files are merged into Silver.

---

### 8.3 Optimum Ingestion Group Topology Matrix

![Optimum Ingestion Group Topology Matrix](/Users/chandu/Documents/Python_practice/Fabric/images/25_optimum_ingestion_group_topology_matrix_p11.png)

To configure `Ingestion_metadata_load_template.xlsx`, define **4 distinct Ingestion Groups** mapped to **2 Schedules**:

| Group Code | Ingestion Mode | Table Count & Type | Load Mechanism | Schedule | Execution Dependency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`IG_AS400_BATCH_DIM`** | Batch | 43 Dimensions | Full Load (Truncate & Load via Fabric ODBC Copy) | `SCH_BATCH_TWICE_DAILY`<br>(09:00 & 17:00 CET) | Runs first at scheduled window |
| **`IG_AS400_BATCH_FACT`** | Batch | 15 Facts | Incremental (Fabric ODBC Copy via `ctl.watermark_state`) | `SCH_BATCH_TWICE_DAILY`<br>(09:00 & 17:00 CET) | Runs after `IG_AS400_BATCH_DIM` succeeds |
| **`IG_AS400_NRT_DIM`** | NRT | 3 Dimensions | Fivetran Sync $\rightarrow$ Fabric PySpark MERGE into Silver | `SCH_NRT_10MIN`<br>(Every 10 mins) | Runs every 10 minutes |
| **`IG_AS400_NRT_FACT`** | NRT | 36 Facts | Fivetran Sync $\rightarrow$ Fabric PySpark MERGE into Silver | `SCH_NRT_10MIN`<br>(Every 10 mins) | Runs every 10 minutes (Priority 2) |

---

### 8.4 Orchestration Execution Pattern in Fabric

1. **Master Batch Orchestrator Pipeline (`pl_master_batch_orchestrator`)**:
   - Triggers at 09:00 and 17:00 CET.
   - **Step 1**: Execute `pl_ingest_group` with parameter `group_code = 'IG_AS400_BATCH_DIM'`.
   - **Step 2 (On Success)**: Execute `pl_ingest_group` with parameter `group_code = 'IG_AS400_BATCH_FACT'`.
2. **Master NRT Orchestrator Pipeline (`pl_master_nrt_orchestrator`)**:
   - Triggers every 10 minutes.
   - Executes PySpark notebooks for `IG_AS400_NRT_DIM` and `IG_AS400_NRT_FACT`, reading from ADLS shortcuts and executing Delta Lake upserts.

---

## 9. Modernizing Fivetran AS400/DB2 Incremental Ingestion (15-Minute Latency SLA)

### 9.1 Latency Budget Equation & SLA Compliance Table

To satisfy the non-functional requirement (**NFR**):
> **"Data once entered in the source system (AS400/DB2) must be visible in the consumer layer (Power BI report) no later than 15 minutes."**

![Fivetran NRT Latency Budget & SLA Breakdown](/Users/chandu/Documents/Python_practice/Fabric/images/26_fivetran_nrt_latency_budget_and_sla_table_p12.png)

#### The End-to-End Latency Equation:
To guarantee compliance, the total latency budget $T_{total}$ must satisfy:
$$T_{total} = T_{\text{Fivetran Extract \& Land}} + T_{\text{Pipeline Wait}} + T_{\text{Bronze Ingest}} + T_{\text{Silver Engine}} + T_{\text{Gold Fact/Dim Engine}} + T_{\text{PBI Direct Lake Refresh}} \le 15\text{ minutes}$$

#### SLA Contribution & Latency Audit Matrix:

| Architectural Stage | Processing Activity | Technical Standard | SLA Contribution | Cumulative Latency |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1: Source $\rightarrow$ Landing** | Fivetran CDC Sync from AS400 DB2 | Fivetran Sync Frequency set to 5 mins | 0.0 – 5.0 mins | 5.0 mins |
| **Stage 2: Trigger & Bronze Ingestion** | OneLake Shortcut read into `lh_bronze` | Micro-batch trigger every 5 mins + PySpark Overwrite/Append | 0.5 – 1.0 min | 6.0 mins |
| **Stage 3: Silver Transformation** | Schema projection, JDE Julian date conversion, Type casting | Master Generic Silver Engine (`nb_silver_generic_engine`) | 1.0 – 1.5 mins | 7.5 mins |
| **Stage 4: Gold Fact/Dim Modeling** | Business logic, surrogate keys, Fact/Dim Delta MERGE | Master Gold Modeling Engine (`nb_gold_star_schema_engine`) | 1.5 – 2.0 mins | 9.5 mins |
| **Stage 5: Direct Lake Semantic Model** | Model metadata resolution on Delta tables | Direct Lake Mode (Zero Import/Refresh Delay) | 0.0 seconds | 9.5 mins |
| **Stage 6: Power BI Visual Display** | AR KPI Report / Financial Reports rendering | Automatic Page Refresh (APR) / Direct Lake query | Instant (< 5 sec) | **~9.5 – 11.5 mins** |
| **NFR VERDICT** | Guaranteed End-to-End Latency $\le$ 15 Minutes | **STRICT COMPLIANCE** | **PASS** | **PASS** |

---

### 9.2 End-to-End Fivetran CDC to Direct Lake Semantic Model Architecture

![End-to-End Fivetran CDC to Direct Lake Semantic Model Architecture](/Users/chandu/Documents/Python_practice/Fabric/images/27_fivetran_nrt_end_to_end_medallion_architecture_p13.png)

```mermaid
flowchart TD
    AS400["AS400 DB2 / JDE Core Tables\n(F0901, F0902, F0911, F03B11, F0411)"]
    -->|Fivetran Continuous CDC| ADLS["ADLS Gen2 / OneLake Landing\n(fivetran-as400-db2-destination/test_crpdta)"]
    
    ADLS -->|OneLake External Shortcut| S2["Stage 2: Bronze Layer (lh_bronze)\nDelta Tables: bronze.f0911, bronze.f0902, bronze.f03b11"]
    
    S2 -->|nb_silver_generic_engine| S3["Stage 3: Silver Layer (lh_silver)\nDelta Tables: silver.f0911_account_ledger,\nsilver.f03b11_customer_ledger, silver.f0411_ap_ledger"]
    
    S3 -->|nb_gold_star_schema_engine| S4_DIM["Stage 4: Gold Star Schema (lh_gold)\nDimensions:\ngold.dim_customer, gold.dim_account, gold.dim_date"]
    S3 -->|nb_gold_star_schema_engine| S4_FACT["Stage 4: Gold Star Schema (lh_gold)\nFacts:\ngold.fact_ar_ledger, gold.fact_gl_ledger, gold.fact_ap_ledger"]
    
    S4_DIM -->|Direct Lake Zero-Latency Metadata Connection| S5_AR["Stage 5: Domain Direct Lake Semantic Models\nsm_accounts_receivable_directlake\n(AR Domain Semantic Model)"]
    S4_FACT -->|Direct Lake Connection| S5_AR
    
    S4_DIM -->|Direct Lake Connection| S5_GL["Stage 5: Domain Direct Lake Semantic Models\nsm_general_ledger_directlake\n(GL Domain Semantic Model)"]
    S4_FACT -->|Direct Lake Connection| S5_GL
    
    S5_AR -->|Automatic Page Refresh < 5 sec| REP_AR["Consumer Power BI Reports\nAccounts Receivable KPI Report\n(Open Invoices, Aging, DSO)"]
    S5_GL -->|Direct Lake Query Refresh| REP_GL["Consumer Power BI Reports\nGeneral Ledger & Financial Report\n(Income Statement, Trial Balance)"]
```

#### Architectural Stage Highlights:
1. **Source Tier**: Captures real-time transactions from core JDE accounting tables (`F0911` - General Ledger, `F03B11` - AR Ledger, `F0411` - AP Ledger).
2. **OneLake Shortcut Ingestion**: Zero-copy mount of the Fivetran ADLS landing container eliminates secondary data movement.
3. **Master Silver Engine (`nb_silver_generic_engine`)**: Automatically unpacks JDE Julian dates (`CYYDDD`), trims fixed-width CHAR padding, and enforces Delta ACID upserts.
4. **Master Gold Engine (`nb_gold_star_schema_engine`)**: Conforms dimensional keys and builds fact tables with incremental surrogate key resolution.
5. **Direct Lake Semantic Models**: Power BI connects directly to OneLake Delta Parquet files without importing data into memory cache (VertiPaq import mode eliminated), resulting in **0-second semantic model refresh latency**.

---

## 10. Fivetran NRT Implementation Blueprint & OneLake Shortcut Setup (Phases 1–4)

![Fivetran Setup Phases & Gold Schema Architecture](/Users/chandu/Documents/Python_practice/Fabric/images/28_fivetran_setup_phases_and_gold_schema_table_p14.png)

> [!TIP]
> **Fivetran Destination Architecture Strategy (Option A vs. Option B):**  
> While Option A utilizes an ADLS Gen2 landing container with OneLake external shortcuts, the enterprise standard recommendation is **Option B (Direct to Fabric Lakehouse `lh_bronze_dev`)** to eliminate intermediate storage hops and unlock instant Direct Lake queryability. For the full comparative analysis, architectural evaluation, and migration runbook, see:  
> 👉 **[Fivetran to Microsoft Fabric Destination Architecture & Migration Guide](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/Fivetran_to_Microsoft_Fabric_Destination_Architecture_and_Migration_Guide.md)**.

### 10.1 Phase 1: Fivetran & Landing Storage Setup (5-Minute Sync SLA)
1. **Configure Fivetran Sync Frequency**:
   * Open the **Fivetran Dashboard**.
   * Navigate to the **IBM AS400 / DB2 Connector** syncing the core transactional ledger tables: `F0911`, `F0902`, `F03B11`, `F0011`, and `F0411`.
   * Set the **Sync Frequency to 5 Minutes**.
2. **Verify OneLake Landing Shortcut**:
   * Ensure that the Fabric Lakehouse shortcut `lh_bronze/Files/landing_as400_test_crpdta` points directly to the Azure Data Lake Storage (ADLS Gen2) container `fivetran-as400-db2-destination` subfolder `test_crpdta/`.

---

### 10.2 OneLake Landing Shortcut & Service Principal (SPN) Configuration

![OneLake Shortcut Settings & SPN Credentials](/Users/chandu/Documents/Python_practice/Fabric/images/30_fivetran_onelake_shortcut_connection_and_spn_p16.png)

To establish the headless, high-speed OneLake External Shortcut connecting Microsoft Fabric to Fivetran's ADLS Gen2 landing container, configure the connection properties as specified:

| Shortcut & Connection Field | Parameter Value | Architectural Notes |
| :--- | :--- | :--- |
| **Shortcut Name** | `landing_as400_crpdta` | Target directory in `lh_bronze/Files/` |
| **URL / Endpoint** | `https://ipsazfdl.dfs.core.windows.net` | Primary ADLS Gen2 DFS endpoint |
| **Container** | `fivetran-as400-db2-destination` | Fivetran landing storage container |
| **Subpath** | `/fivetran-as400-db2-destination/test_crpdta` | JDE environment target directory |
| **Authentication Kind** | `Service principal` | Dedicated non-interactive authentication |

#### Dedicated Service Principal Credentials:
* **Service Principal Name**: `Fivetran-Fabric-Destination-SP`
* **Application (client) ID**: `d3ace6c2-c791-4193-94e0-640eb5abf8d9`
* **Directory (tenant) ID**: `2097bb0c-110b-414c-9b7f-293ddc46d353`
* **Secret Value**: `eY78Q~Tzwb3vYslLcmy5OS8RI~qWK.1_1mkX.cjw`

> [!NOTE]
> Once registered in Fabric under **Settings > Manage connections and gateways**, the connection appears as `landing_as400_crpdta` and enables instant, zero-copy querying of Fivetran Parquet files directly from OneLake.

---

### 10.3 Phase 2: Metadata Catalog Configuration (`sqldb_meta_orch`)
Register the 39 NRT dataset definitions, high watermarks, and stage mappings inside `sqldb-meta-orch-dev`:
* Insert entries into `meta.dataset` pointing to target Silver tables (`silver_f03b11_customer_ledger`, `silver_f0911_account_ledger`, etc.).
* Map dataset targets to the `IG_AS400_NRT_FACT` and `IG_AS400_NRT_DIM` groups in `meta.ingestion_group_dataset`.
* Baseline `ctl.watermark_state` with `watermark_column_name = '_fivetran_synced'`.

---

### 10.4 Phase 3: Bronze & Silver Processing Layers (`lh_bronze` & `lh_silver`)
1. **Bronze Ingestion Notebook (`nb_bronze_ingestion`)**:
   * Reads new files landing in the OneLake shortcut path.
   * Micro-batches landing data into `lh_bronze` Delta tables (`bronze.f0911`, `bronze.f03b11`, etc.) appending audit columns: `_ingested_at` and `_pipeline_run_id`.
2. **Silver Master Transformation Engine (`nb_silver_generic_engine`)**:
   * Powered by `src/transformations/cleansing.py` and `nb_silver_generic_engine.py`.
   * Renames cryptic JDE columns (e.g., `RPAG` $\rightarrow$ `gross_amount`, `RPAAP` $\rightarrow$ `open_amount`, `RPAN8` $\rightarrow$ `customer_number`).
   * Converts JDE Julian dates (`CYYDDD` format where $C = 1900 + C \times 100$) into standard ISO `YYYY-MM-DD` dates.
   * Enforces data quality assertions and performs an **idempotent Delta MERGE** into target Silver tables.

---

## 11. Gold Star Schema Architecture & Direct Lake Semantic Modeling (Phases 4–5)

### 11.1 Illustrative Gold Star Schema Architecture Table

In **Phase 4**, conformed business tables from `lh_silver` are modeled into dimensional facts and shared dimensions:

| Target Gold Table | Source Silver Tables | Entity Type | Key Business Measures / Attributes | Primary / Surrogate Keys |
| :--- | :--- | :--- | :--- | :--- |
| **`gold.fact_ar_ledger`** | `silver.f03b11_customer_ledger` | Transaction Fact | Gross Amount (`RPAG`), Open Amount (`RPAAP`), Discount Available, Payment Status | `ar_ledger_sk`<br>`company_code`<br>`doc_type`<br>`doc_number`<br>`pay_item` |
| **`gold.fact_gl_ledger`** | `silver.f0911_account_ledger` | Transaction Fact | GL Amount (`GLAA`), Units (`GLU`), Ledger Type (`GLLT`) | `gl_ledger_sk`<br>`company_code`<br>`doc_type`<br>`doc_number`<br>`gl_date` |
| **`gold.fact_ap_ledger`** | `silver.f0411_ap_ledger` | Transaction Fact | AP Gross Amount (`RPAG`), Open Amount (`RPAAP`), Discount | `ap_ledger_sk`<br>`company_code`<br>`doc_type`<br>`doc_number`<br>`pay_item` |
| **`gold.dim_customer`** | `silver.f03b11_customer_ledger`<br>+ `Address Book (F0101)` | Conformed Dimension | Customer Name, Credit Limit, Payment Terms, Customer Group | `customer_sk`<br>`customer_number (AN8)` |
| **`gold.dim_account`** | `silver.f0901` / `silver.f0902` | Conformed Dimension | Account Number (`AID`), Business Unit (`MCU`), Object (`OBJ`), Sub-account (`SUB`) | `account_sk`<br>`account_id` |
| **`gold.dim_date`** | Date Master Generator | Shared Dimension | Calendar Date, Fiscal Year, Fiscal Quarter, Fiscal Period | `date_sk`<br>`calendar_date` |

---

### 11.2 Phase 5: Domain-Specific Direct Lake Semantic Models

![Direct Lake Semantic Models & NRT Pipeline](/Users/chandu/Documents/Python_practice/Fabric/images/29_direct_lake_semantic_models_and_nrt_pipeline_p15.png)

To guarantee zero refresh delay, domain-specific semantic models connect directly to Gold tables in **Direct Lake Mode**:

```mermaid
flowchart TD
    subgraph GOLD_LH["Gold Lakehouse (lh_gold)"]
        F_AR["gold.fact_ar_ledger"]
        F_GL["gold.fact_gl_ledger"]
        D_CUST["gold.dim_customer"]
        D_ACCT["gold.dim_account"]
        D_DATE["gold.dim_date"]
    end

    subgraph AR_DOMAIN["Accounts Receivable Domain"]
        SM_AR["sm_accounts_receivable_directlake\n(Direct Lake Mode - 0s Refresh)"]
        REP_AR["Power BI AR KPI Report\n• Open AR Invoices\n• Aging Buckets\n• Days Sales Outstanding (DSO)"]
    end

    subgraph GL_DOMAIN["General Ledger Domain"]
        SM_GL["sm_general_ledger_directlake\n(Direct Lake Mode - 0s Refresh)"]
        REP_GL["Power BI Financial Statements Report\n• Balance Sheet\n• Income Statement\n• Trial Balance"]
    end

    F_AR & D_CUST & D_DATE --> SM_AR --> REP_AR
    F_GL & D_ACCT & D_DATE --> SM_GL --> REP_GL
```

#### Step 5.1: Create Accounts Receivable (AR) Semantic Model (`sm_accounts_receivable_directlake`)
1. In Microsoft Fabric Workspace, open the **Gold Lakehouse** (`lh_gold`).
2. Click **+ New semantic model**.
3. Name: `sm_accounts_receivable_directlake`.
4. Select target Gold tables: `gold.fact_ar_ledger`, `gold.dim_customer`, `gold.dim_date`.

---

### 11.3 Star Schema Relationships & Business DAX Measures

#### Relationship Configuration:
* `fact_ar_ledger.customer_number` $\rightarrow$ `dim_customer.customer_number` (**Many-to-One `*:1`**)
* `fact_ar_ledger.invoice_date` $\rightarrow$ `dim_date.calendar_date` (**Many-to-One `*:1`**)

#### Core DAX Measures:
```dax
// 1. Total Open AR
Total Open AR = SUM(fact_ar_ledger[open_amount])

// 2. Total Gross AR
Total Gross AR = SUM(fact_ar_ledger[gross_amount])

// 3. Overdue AR Amount
Overdue AR Amount = 
CALCULATE(
    [Total Open AR], 
    fact_ar_ledger[due_date] < TODAY()
)
```

#### Step 5.2: Point Power BI AR KPI Report
* Connect Power BI Desktop or Service to `sm_accounts_receivable_directlake`.
* Visuals displaying Open AR, Aging Buckets, and DSO automatically update within seconds of the Gold Delta commit, incurring **0 seconds dataset refresh latency**.

---

### 11.4 Phase 6: Orchestration Pipeline (`pl_NRT_ingestion`)

The end-to-end near real-time orchestration pipeline triggers every 5 minutes:

```mermaid
flowchart TD
    REC["Recurrence Schedule: Every 5 Minutes (or Webhook Trigger)"]
    --> S1["Step 1: Bronze Ingestion\nRuns nb_bronze_ingestion (Parallel x5 tables)\nDuration: ~30 sec"]
    
    S1 -->|Upon Success| S2["Step 2: Silver Engine\nRuns nb_silver_generic_engine (Parallel x5 tables)\nDuration: ~45 sec"]
    
    S2 -->|Upon Success| S3["Step 3: Gold Fact/Dim Engine\nRuns nb_gold_star_schema_engine\nDuration: ~60 sec"]
    
    S3 --> S4["Delta MERGE Commits to lh_gold"]
    S4 --> S5["Power BI AR KPI Report Visuals Auto-Update\nvia Direct Lake (0 Sec Lag)"]
```

---

## 12. Data Structure of `lh_bronze` & Medallion Pipeline Design

![Data Structure of lh_bronze & Medallion Design](/Users/chandu/Documents/Python_practice/Fabric/images/31_fivetran_bronze_structure_and_medallion_design_p17.png)

### 12.1 Delta Storage Format & Fivetran System Columns

When Fivetran syncs DB2i tables (such as JDE User Defined Codes `F0005` or transactional ledgers `F4211`, `F0911`) into `lh_bronze`:
* **Storage Format**: Open Delta Lake format (`.parquet` files + `_delta_log`) in OneLake.
* **Source Business Columns**: All DB2i table columns (e.g., `DRSY`, `DRRT`, `DRKY`, `DRDL01`, `DRDL02` for `F0005`) mapped to Delta types.
* **Fivetran System Columns**:
  * `_fivetran_synced` *(Timestamp, UTC)*: Exact time Fivetran inserted or updated the row. Serves as the primary incremental watermark.
  * `_fivetran_deleted` *(Boolean)*: Soft-delete tombstone (`TRUE` if deleted in AS400; `FALSE` if active).
  * `_fivetran_id` *(String)*: Unique row identifier generated by Fivetran when tables lack composite primary keys.

---

### 12.2 Bronze to Silver to Gold Transformation Specifications

#### A. Bronze to Silver Pipeline (`lh_silver`):
1. **Incremental Processing**: Queries only new/updated records where:
   $$\text{\_fivetran\_synced} > \max(\text{last\_processed\_timestamp})$$
2. **Data Cleansing**: Trims trailing whitespace from fixed-width DB2 CHAR columns, converts Julian dates (`CYYDDD`), and standardizes NULL values.
3. **Data Quality Quarantine**: Enforces non-null validation; invalid records are routed to `lh_bronze_quarantine`.
4. **Deterministic Hash Key Generation**:
   * **Business Key (BK)**: Composite natural key trimmed and normalized:
     $$\text{BK} = \text{CONCAT\_WS('\_', UPPER(TRIM(DRSY)), UPPER(TRIM(DRRT)), UPPER(TRIM(DRKY)))}$$
   * **Surrogate Key (SK)**: Deterministic hash key calculated using `SHA2(Business_Key, 256)`.
     > [!TIP]
     > Deterministic SHA256 surrogate keys eliminate distributed database locking and sequential auto-increment bottlenecks across Spark worker nodes.
5. **Target Operation**: Delta `MERGE INTO` `lh_silver` on `surrogate_key`.

#### B. Silver to Gold Pipeline (`lh_gold`):
1. **Dimensional Modeling**: Constructs conformed dimensions (e.g., `dim_udc`, `dim_customer`, `dim_item`) and fact tables (`fact_sales`, `fact_gl_ledger`).
2. **Target Operation**: Incremental Delta `MERGE INTO` or dynamic partition overwrite.

---

## 13. Fivetran CDC Append-Only Internals & PySpark Deduplication Engine

![Fivetran CDC Append-Only Internals & Deduplication](/Users/chandu/Documents/Python_practice/Fabric/images/32_fivetran_cdc_append_internals_and_dedup_code_p18.png)

### 13.1 How Fivetran Handles Changes to ADLS (Append-Only Log Stream)

Because cloud object stores (ADLS Gen2) cannot perform arbitrary in-place row mutations at high speeds, Fivetran captures AS400 journal events and **appends new records for every event**:

| Source Action (AS400 DB2) | What Fivetran Writes to ADLS / Landing | `_fivetran_deleted` | `_fivetran_synced` |
| :--- | :--- | :--- | :--- |
| **`INSERT`** (New record) | Appends a new row with initial column values | `FALSE` | $T_1$ |
| **`UPDATE`** (Column changed) | Appends a new row with the modified column values | `FALSE` | $T_2$ *(newer timestamp)* |
| **`DELETE`** (Record deleted) | Appends a new tombstone row with the primary key | `TRUE` | $T_3$ *(newer timestamp)* |

---

### 13.2 Life of a Record Example (`Order_ID = 1001` State Progression)

If an order record (`Order_ID = 1001`) is created, updated twice, and subsequently deleted in DB2:

In ADLS Landing & Bronze Layer, **Bronze retains all 4 rows as an immutable audit history**:

| `Order_ID` | `Status` | `Amount` | `_fivetran_deleted` | `_fivetran_synced` |
| :---: | :---: | :---: | :---: | :---: |
| 1001 | OPEN | 100 | `FALSE` | 2026-08-31 10:00:00 |
| 1001 | PROCESSING | 100 | `FALSE` | 2026-08-31 10:15:00 |
| 1001 | SHIPPED | 120 | `FALSE` | 2026-08-31 10:30:00 |
| 1001 | SHIPPED | 120 | `TRUE` | 2026-08-31 11:00:00 |

---

### 13.3 Two-Step Silver Processing Engine (`nb_silver_ingestion_NRT`)

Because Bronze contains multiple appended versions of the same primary key, the **Silver Ingestion Engine (`nb_silver_ingestion_NRT`)** performs two critical operations:

![Fivetran Silver Delta Lake MERGE (Upsert & Delete Modes)](/Users/chandu/Documents/Python_practice/Fabric/images/33_fivetran_silver_merge_upsert_delete_p19.png)

#### 1. In-Batch Deduplication (Window Function)
If a single micro-batch contains multiple updates for the same primary key, it isolates only the **latest state**:

```python
from pyspark.sql import Window
import pyspark.sql.functions as F

# Define primary key columns for the entity
pk_cols = ["order_id"]

# Window partition across primary keys ordered by sync timestamp descending
window_dedup = Window.partitionBy(*pk_cols).orderBy(
    F.col("_fivetran_synced").desc(), 
    F.col("_ingested_at").desc()
)

# Isolate only the latest transactional state per primary key
df_bronze_deduped = (
    df_bronze_slice.withColumn("_row_seq", F.row_number().over(window_dedup))
    .filter(F.col("_row_seq") == 1)
    .drop("_row_seq")
)
```

#### 2. Delta Lake `MERGE` (Upsert & Delete)
The deduplicated micro-batch is merged into the target Silver Delta table using Delta Lake MERGE semantics:

* **When updated (`_fivetran_deleted = false`)**: Performs an in-place `UPDATE` on the existing Silver record matching the Primary Key, rather than creating duplicates.
* **When deleted (`_fivetran_deleted = true`)**: Depending on the configured `p_delete_mode` parameter in `meta.dataset`:
  * **Soft Delete (`p_delete_mode = 'soft'`)**: Updates the record in Silver, setting `_is_deleted = true` and preserving row history for auditing.
  * **Hard Delete (`p_delete_mode = 'hard'`)**: Deletes the record physically from the Silver Delta table (`DELETE WHERE target.pk = source.pk`).

```python
from delta.tables import DeltaTable

silver_delta_table = DeltaTable.forName(spark, f"lh_silver.{target_table_name}")

if p_delete_mode.lower() == "soft":
    # Upsert with soft delete flag
    (
        silver_delta_table.alias("tgt")
        .merge(
            df_bronze_deduped.alias("src"),
            " AND ".join([f"tgt.{col} = src.{col}" for col in pk_cols])
        )
        .whenMatchedUpdate(
            set={
                **{col: f"src.{col}" for col in business_cols},
                "_is_deleted": "src._fivetran_deleted",
                "_updated_at": "current_timestamp()"
            }
        )
        .whenNotMatchedInsert(
            condition="src._fivetran_deleted = false",
            values={
                **{col: f"src.{col}" for col in business_cols},
                "_is_deleted": "lit(false)",
                "_created_at": "current_timestamp()",
                "_updated_at": "current_timestamp()"
            }
        )
        .execute()
    )
else:
    # Upsert active records and hard delete tombstones
    (
        silver_delta_table.alias("tgt")
        .merge(
            df_bronze_deduped.alias("src"),
            " AND ".join([f"tgt.{col} = src.{col}" for col in pk_cols])
        )
        .whenMatchedDelete(condition="src._fivetran_deleted = true")
        .whenMatchedUpdate(
            condition="src._fivetran_deleted = false",
            set={
                **{col: f"src.{col}" for col in business_cols},
                "_updated_at": "current_timestamp()"
            }
        )
        .whenNotMatchedInsert(
            condition="src._fivetran_deleted = false",
            values={
                **{col: f"src.{col}" for col in business_cols},
                "_created_at": "current_timestamp()",
                "_updated_at": "current_timestamp()"
            }
        )
        .execute()
    )
```

---

### 13.4 Critical Considerations to Guarantee 15-Minute SLA

To ensure the 15-minute end-to-end SLA is met consistently in production:

1. **Eliminate Spark Cold Starts**: Standard Spark sessions take 30–60 seconds to initialize. Enable **Microsoft Fabric Starter Pools** to reduce cluster spin-up to **~5 seconds**.
2. **Deterministic Hash Keys (`SHA256`)**: Avoid sequential auto-incrementing integer identity columns. Use `SHA256(Business_Key)` for lock-free parallel execution across distributed Spark executor nodes.
3. **Prevent Small File Performance Degradation**: 5-minute micro-batch writes generate numerous small Parquet files. Schedule an automated hourly **`OPTIMIZE & VACUUM`** job with **Fabric V-Order** enabled on all Delta tables.
4. **Incremental Watermarking**: Never perform full table scans. Always query using `_fivetran_synced > last_watermark`.
5. **Direct Lake Auto-Framing**: Trigger a Power BI Semantic Model Framing Refresh (via TMSL or Fabric REST API) immediately after Gold pipeline execution completes to ensure reports reflect new data instantly.


