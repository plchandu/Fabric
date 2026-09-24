# Microsoft Fabric — Naming Convention Standard

> **Project:** IPS Corporation BI Modernization  
> **Topic:** Enterprise Resource Naming Standards, Abbreviation Glossaries, Medallion Identifiers & Pipeline Component Conventions  
> **Document Version:** 1.0  
> **Release Date:** 13-March-2026  
> **Author / Modified By:** Nirmalya Chakraborty (LTI Mindtree / LTM)  
> **Status:** Approved Enterprise Architecture Standard  

---

## Document Control & Version History

| Version No. | Modified By | Reviewed By | Authorized By | Release Date | Modification Description |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1.0** | **Nirmalya Chakraborty** *(LTM)* | Enterprise Architecture | BI Steering Committee | **13-03-2026** | Created initial enterprise release of Fabric naming convention standard. |

---

## Executive Summary

Establishing a structured, enterprise-wide naming convention is a foundational prerequisite for operational governance, maintainability, and security across the **Microsoft Fabric ecosystem** for **IPS Corporation**. 

Drawing directly from the **Microsoft Cloud Adoption Framework (CAF)**, official Microsoft Fabric documentation, and industry best practices, this standard establishes uniform naming rules for all Fabric compute, storage, data engineering, orchestration, semantic, and reporting assets.

Adherence to this standard is **mandatory** for all developers, data engineers, and BI analysts across all project lifecycle stages (`dev`, `tst`, `uat`, `prd`).

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [Why Naming Conventions Matter](#2-why-naming-conventions-matter)
3. [General Naming Principles](#3-general-naming-principles)
4. [Standard Abbreviation Reference](#4-standard-abbreviation-reference)
   - [4.1 Fabric Experience / Service Group Prefixes](#41-fabric-experience--service-group-prefixes)
   - [4.2 Artifact Type Prefixes](#42-artifact-type-prefixes)
   - [4.3 Environment Abbreviations](#43-environment-abbreviations)
   - [4.4 Medallion Layer Abbreviations](#44-medallion-layer-abbreviations)
5. [Naming Convention by Resource Type](#5-naming-convention-by-resource-type)
   - [5.1 Fabric Capacity](#51-fabric-capacity)
   - [5.2 Workspaces](#52-workspaces)
   - [5.3 Lakehouse](#53-lakehouse)
   - [5.4 Warehouse](#54-warehouse)
   - [5.5 Data Pipelines & Pipeline Components](#55-data-pipelines--pipeline-components)
   - [5.6 Notebooks](#56-notebooks)
   - [5.7 Dataflow Gen2](#57-dataflow-gen2)
   - [5.8 Semantic Models (Power BI Datasets)](#58-semantic-models-power-bi-datasets)
   - [5.9 Power BI Reports](#59-power-bi-reports)
6. [Master Naming Convention Quick-Reference Cheat Sheet](#6-master-naming-convention-quick-reference-cheat-sheet)

---

## 1. Purpose

![Naming Convention Standard Cover & TOC](/Users/chandu/Documents/Python_practice/Fabric/images/52_fabric_naming_convention_cover_and_toc_p1.png)

The purpose of this standard is to establish a consistent, industry-aligned naming convention for all Microsoft Fabric resources. This document draws from Microsoft official documentation, the **Azure Cloud Adoption Framework (CAF)**, and enterprise community best practices.

---

## 2. Why Naming Conventions Matter

A standardized naming convention provides tangible operational benefits across five key dimensions:

| Benefit | Description |
| :--- | :--- |
| **Discoverability** | Well-named resources are easy to locate in workspace lists, global search results, and end-to-end lineage views. |
| **Governance** | Consistent names simplify security policy enforcement, access reviews, compliance audits, and FinOps cost allocation. |
| **Collaboration** | Teams across Data Engineering, BI, Data Science, and Operations can immediately understand an artifact's purpose, layer, and domain at a glance. |
| **Automation** | Standardized, predictable names enable reliable CI/CD release pipelines, Infrastructure-as-Code (IaC), deployment scripts, and REST API integrations. |
| **Lifecycle Management** | Environment tags (`dev`, `tst`, `uat`, `prd`) embedded directly in names drastically reduce accidental deployments or modifications to production. |

---

## 3. General Naming Principles

![General Principles & Abbreviation Prefixes](/Users/chandu/Documents/Python_practice/Fabric/images/53_fabric_naming_convention_principles_and_prefixes_p2.png)

All Microsoft Fabric resources must comply with eight universal principles:

1. **Use Lowercase:** All resource names should use lowercase letters for consistency, readability, and cross-tool compatibility.
2. **Use Underscores or Hyphens as Delimiters:** Prefer **`_` (underscores)** for artifact names within Microsoft Fabric (workspaces, lakehouses, notebooks, pipelines). Use **`-` (hyphens)** for Fabric Capacity and Azure cloud resources. **Never use spaces in technical asset names**.
3. **Keep Names Descriptive but Concise:** Put the most important information first. Extremely long names may be truncated in the Microsoft Fabric web portal UI.
4. **Avoid Special Characters:** Stick strictly to alphanumeric characters `a-z`, `0-9`, underscores `_`, and hyphens `-`. Avoid `@`, `&`, `#`, `(`, `)`, `$`, `/`, and `\`.
5. **Use Consistent Abbreviations:** Define standard abbreviation glossaries and apply them uniformly across all project repositories.
6. **Include Environment Tags:** Append or embed `dev`, `tst`, `uat`, or `prd` to distinguish lifecycle stages.
7. **Embed the Medallion Layer:** For data engineering artifacts, clearly indicate `bronze`, `silver`, or `gold` (or numeric indices `100`, `200`, `300`).
8. **Avoid Generic Names:** Never use ambiguous placeholders such as `data`, `report1`, `test`, `new_notebook`, or `pipeline_temp`.

---

## 4. Standard Abbreviation Reference

### 4.1 Fabric Experience / Service Group Prefixes
When classifying artifacts by Fabric workload or service capability:

| Abbreviation | Fabric Experience / Service Group |
| :---: | :--- |
| **`de`** | Data Engineering (Synapse Data Engineering) |
| **`df`** | Data Factory |
| **`ds`** | Data Science |
| **`dw`** | Data Warehousing (Synapse Data Warehouse) |
| **`pbi`** | Power BI |
| **`rta`** | Real-Time Analytics / Real-Time Intelligence |

---

### 4.2 Artifact Type Prefixes
Every artifact inside a Microsoft Fabric workspace must begin with a standardized 2-to-4 character prefix:

| Prefix | Artifact Type | Prefix | Artifact Type |
| :---: | :--- | :---: | :--- |
| **`cap`** | Fabric Capacity | **`rpt`** | Power BI Report |
| **`dom`** | Fabric Domain | **`dash`**| Power BI Dashboard |
| **`ws`** | Workspace | **`es`** | Eventstream |
| **`lh`** | Lakehouse | **`kql`** | KQL Database |
| **`wh`** | Warehouse | **`kqq`** | KQL Queryset |
| **`pl`** | Data Pipeline | **`sjd`** | Spark Job Definition |
| **`nb`** | PySpark / Spark Notebook | **`sc`** | OneLake Shortcut |
| **`df`** | Dataflow Gen2 | **`env`** | Spark Environment |
| **`sm`** | Semantic Model (Power BI Dataset) | **`ml`** | ML Model / Experiment |

---

### 4.3 Environment Abbreviations

![Environments, Capacities & Workspaces](/Users/chandu/Documents/Python_practice/Fabric/images/54_fabric_naming_convention_environments_capacities_workspaces_p3.png)

Lifecycle environments are tagged using standardized 3-character identifiers:

| Abbreviation | Lifecycle Environment | Usage Description |
| :---: | :--- | :--- |
| **`dev`** | **Development** | Active developer engineering, feature branch development, unit testing. |
| **`tst`** | **Test / QA** | System Integration Testing (SIT), automated smoke and regression testing. |
| **`uat`** | **User Acceptance Testing** | Business stakeholder validation, reconciliation audits, and formal sign-off. |
| **`prd`** | **Production** | Live operational reporting, business executive dashboards, client analytics. |
| **`sbx`** | **Sandbox / Experimental** | Isolated exploratory environments for proofs-of-concept; non-persistent. |

---

### 4.4 Medallion Layer Abbreviations

Data processing stages in the Medallion Architecture are designated as:

| Abbreviation | Medallion Processing Stage | Storage & Transformation Context |
| :---: | :--- | :--- |
| **`bronze`** | **Raw / Landing** | Exact source replica, immutable append-only audit trail, zero business logic. |
| **`silver`** | **Cleansed / Conformed** | Standardized types, JDE Julian date conversion, deduplicated, conformed dimensions. |
| **`gold`** | **Curated / Business-Ready** | Kimball dimensional star schemas (Facts & Dimensions), Direct Lake semantic consumption. |

---

## 5. Naming Convention by Resource Type

### 5.1 Fabric Capacity
Fabric Capacities are provisioned in Azure and follow Azure Cloud Adoption Framework (CAF) hyphenated syntax:

$$\mathbf{Pattern:}\quad\text{<org>-<env>-fabric-<sku>-<instance>}$$

| Element | Description | Allowed Values / Examples |
| :--- | :--- | :--- |
| `<org>` | Organization or business unit code | `ips`, `contoso` |
| `<env>` | Lifecycle environment identifier | `dev`, `tst`, `prd` |
| `fabric` | Fixed resource type identifier | `fabric` |
| `<sku>` | Capacity SKU size | `f32`, `f64`, `f128` |
| `<instance>` | Three-digit zero-padded instance number | `001`, `002` |

* **Production Examples:**
  * `ips-prd-fabric-f64-001` *(IPS Production F64 Dedicated Capacity)*
  * `ips-dev-fabric-f32-001` *(IPS Non-Production F32 Capacity)*

---

### 5.2 Workspaces
Fabric Workspaces group related artifacts by business domain, project, and environment:

$$\mathbf{Pattern:}\quad\text{<domain>\_<project>\_<env>}\quad\text{or}\quad\text{<prefix>\_<description>\_<env>}$$

| Element | Description | Examples |
| :--- | :--- | :--- |
| `<domain>` | Business domain or departmental team | `sales`, `finance`, `supplychain`, `bim` |
| `<project>` | Project, functional area, or data capability | `data`, `customer360`, `quarterly_reporting` |
| `<env>` | Lifecycle environment tag | `dev`, `tst`, `prd` |

* **Production Examples:**
  * `bim_data_dev` *(Core BI Modernization Ingestion Workspace - Dev)*
  * `bim_data_prd` *(Core BI Modernization Ingestion Workspace - Prod)*
  * `sales_customer360_dev`
  * `finance_quarterly_reporting_prd`
  * `hr_workforce_analytics_dev`

> [!NOTE]
> Microsoft recommends keeping workspace names short and placing the most critical domain and project identifiers at the start of the name to prevent UI truncation.

---

### 5.3 Lakehouse

![Lakehouse, Warehouse & Data Pipelines](/Users/chandu/Documents/Python_practice/Fabric/images/55_fabric_naming_convention_lakehouse_warehouse_pipelines_p4.png)

Lakehouse instances must specify their domain and medallion layer:

$$\mathbf{Pattern:}\quad\text{lh\_<domain>\_<medallion\_layer>\_<purpose>}$$

| Element | Description | Allowed Values / Examples |
| :--- | :--- | :--- |
| `lh` | Artifact type prefix for Lakehouse | `lh` |
| `<domain>` | Business or data domain | `sales`, `finance`, `supplychain`, `as400` |
| `<medallion_layer>` | Medallion storage zone | `bronze`, `silver`, `gold` |
| `<purpose>` | Specific functional or descriptive purpose | `raw_orders`, `customer_master`, `gl_extracts` |

* **Production Examples:**
  * `lh_bronze_dev` *(General Ingestion Raw Lakehouse - Dev)*
  * `lh_silver_dev` *(General Conformed Lakehouse - Dev)*
  * `lh_gold_dev` *(General Dimensional Mart Lakehouse - Dev)*
  * `lh_sales_bronze_raw_orders`
  * `lh_sales_silver_cleansed_orders`
  * `lh_sales_gold_aggregated_metrics`
  * `lh_finance_bronze_gl_extracts`

---

### 5.4 Warehouse
Fabric Synapse Data Warehouses follow a clean domain-purpose syntax:

$$\mathbf{Pattern:}\quad\text{wh\_<domain>\_<purpose>}$$

* **Production Examples:**
  * `wh_finance_reporting`
  * `wh_sales_dimensional_model`
  * `wh_hr_payroll`

---

### 5.5 Data Pipelines & Pipeline Components

Data Factory pipelines must describe the action, target entity, and execution context:

$$\mathbf{Pattern:}\quad\text{pl\_<action>\_<source/target>\_<detail>}$$

| Element | Description | Allowed Values / Examples |
| :--- | :--- | :--- |
| `pl` | Artifact type prefix for Data Pipeline | `pl` |
| `<action>` | Core data movement or processing action | `ingest`, `load`, `transform`, `refresh`, `copy` |
| `<source/target>` | Upstream source or downstream target system/entity | `as400`, `erp`, `crm`, `silver`, `gold`, `adls` |
| `<detail>` | Cadence or processing mode | `daily`, `incremental`, `full`, `5min` |

* **Pipeline Examples:**
  * `pl_master_batch_orchestrator` *(IPS Master Batch Orchestrator)*
  * `pl_NRT_ingestion` *(IPS Fivetran 5-minute CDC Pipeline)*
  * `pl_ingest_erp_orders_daily`
  * `pl_transform_silver_customer_merge`
  * `pl_load_gold_sales_summary`
  * `pl_copy_adls_to_bronze_full`

#### Pipeline Internal Component Naming Standards:
To maintain consistency within Data Factory pipeline JSON definitions:

| Component Type | Prefix | Naming Syntax | Concrete Production Example |
| :--- | :---: | :--- | :--- |
| **Pipeline Parameter** | `p_` | `p_<parameterName>` or `p_<project>_<name>` | `p_Sales_FilePath`, `p_delete_mode`, `p_watermark_val` |
| **Pipeline Variable** | `v_` | `v_<variableName>` or `v_<project>_<name>` | `v_Sales_Timestamp`, `v_execution_id`, `v_batch_count` |
| **Library Variable** | `lbv_` | `lbv_<variableName>` | `lbv_SalesTimestamp`, `lbv_sql_conn_str`, `lbv_spn_id` |
| **Pipeline Activity** | *(none)* | Clear, self-describing snake_case action | `copy_as400_to_bronze`, `lookup_active_tables`, `execute_silver_engine` |
| **Stored Procedure** | `usp_` / `sp_` | `usp_<procedure_name>` | `usp_get_next_batch_id`, `stage.sp_UpsertMetadataFromStage` |

---

### 5.6 Notebooks

![Notebooks, Dataflows, Semantic Models & Reports](/Users/chandu/Documents/Python_practice/Fabric/images/56_fabric_naming_convention_notebooks_dataflows_semantic_models_reports_p5.png)

Fabric PySpark Notebooks must specify their medallion processing layer, domain, and purpose:

$$\mathbf{Pattern:}\quad\text{nb\_<medallion\_layer>\_<domain>\_<purpose>}$$

* **Production Examples:**
  * `nb_bronze_ingestion` *(Micro-batch landing notebook)*
  * `nb_silver_generic_engine` *(Cleansing, JDE Julian date conversion & Delta MERGE)*
  * `nb_gold_star_schema_engine` *(Dimensional fact/dimension modeling)*
  * `nb_bronze_sales_data_ingestion`
  * `nb_silver_sales_deduplication`
  * `nb_gold_finance_kpi_aggregation`
  * `nb_utility_schema_validation`
  * `nb_ds_customer_churn_model`

---

### 5.7 Dataflow Gen2
Fabric Dataflows Gen2 follow an action-domain-detail convention:

$$\mathbf{Pattern:}\quad\text{df\_<action>\_<domain>\_<detail>}$$

* **Production Examples:**
  * `df_clean_hr_employee_records`
  * `df_merge_finance_gl_mapping`

---

### 5.8 Semantic Models (Power BI Datasets)
Direct Lake or Import semantic models encapsulate curated business domains:

$$\mathbf{Pattern:}\quad\text{sm\_<domain>\_<subject>}$$

* **Production Examples:**
  * `sm_accounts_receivable_directlake` *(IPS AR KPI Direct Lake Model)*
  * `sm_general_ledger_directlake` *(IPS GL Financial Statements Model)*
  * `sm_sales_performance`
  * `sm_finance_budget_vs_actual`
  * `sm_hr_headcount_trends`

> [!TIP]
> **Semantic Model Object Naming Rule:**  
> While the model itself uses `sm_<domain>_<subject>`, **all tables, columns, and measures inside the semantic model MUST use human-friendly business names with spaces** (e.g., `[Product Category]`, `[Invoice Date]`, `[Total Open AR]`). These names are directly exposed to business users, Power BI visuals, and **Microsoft Fabric Copilot**. Reserve `snake_case` strictly for underlying Lakehouse/Warehouse Delta tables.

---

### 5.9 Power BI Reports
Reports built upon certified semantic models describe the domain and target business decision:

$$\mathbf{Pattern:}\quad\text{rpt\_<domain>\_<business\_purpose>}$$

* **Production Examples:**
### 5.10 Event Streams

![Eventstreams, KQL Databases, Spark Jobs & Shortcuts](/Users/chandu/Documents/Python_practice/Fabric/images/57_fabric_naming_convention_eventstreams_kql_shortcuts_p6.png)

Fabric Eventstreams ingest real-time telemetry, IoT feeds, and change streams:

$$\mathbf{Pattern:}\quad\text{es\_<source>\_<purpose>}$$

| Element | Description | Examples |
| :--- | :--- | :--- |
| `es` | Artifact type prefix for Eventstream | `es` |
| `<source>` | Event source system | `iot`, `app_logs`, `kafka`, `pos` |
| `<purpose>` | Streaming telemetry or operational purpose | `device_telemetry`, `clickstream`, `factory_sensors` |

* **Production Examples:**
  * `es_iot_device_telemetry`
  * `es_app_logs_clickstream`

---

### 5.11 KQL Databases & Querysets
Real-Time Intelligence KQL assets follow domain-purpose syntax:

$$\mathbf{Pattern\text{ (Database):}}\quad\text{kql\_<domain>\_<purpose>}$$
$$\mathbf{Pattern\text{ (Queryset):}}\quad\text{kqq\_<domain>\_<purpose>}$$

* **Production Examples:**
  * `kql_security_event_logs`
  * `kql_iot_sensor_readings`
  * `kqq_security_threat_detection`

---

### 5.12 Spark Job Definitions
Production scheduled batch Spark definitions:

$$\mathbf{Pattern:}\quad\text{sjd\_<domain>\_<purpose>}$$

* **Production Examples:**
  * `sjd_sales_etl_daily_orders`
  * `sjd_finance_general_ledger_reconciliation`

---

### 5.13 Environments (Spark)
Custom Spark runtime environments, libraries, and compute settings:

$$\mathbf{Pattern:}\quad\text{env\_<domain>\_<purpose>}$$

* **Production Examples:**
  * `env_de_default_spark`
  * `env_ds_ml_training`

---

### 5.14 Shortcuts
OneLake external shortcuts referencing external storage accounts:

$$\mathbf{Pattern:}\quad\text{sc\_<source\_system>\_<target\_object>}$$

* **Production Examples:**
  * `sc_adls_bronze_raw_files`
  * `sc_s3_external_vendor_data`
  * `landing_as400_crpdta` *(Fivetran OneLake external shortcut)*

---

## 6. Table, Schema & Column Naming (Lakehouse / Warehouse)

![Tables, Schemas, Columns & Master Cheat Sheet](/Users/chandu/Documents/Python_practice/Fabric/images/58_fabric_naming_convention_schemas_tables_columns_cheat_sheet_p7.png)

### 6.1 Schemas
Lakehouses and Warehouses organize objects by functional domain or medallion zone:

$$\mathbf{Pattern:}\quad\text{<domain>}\quad\text{or}\quad\text{<medallion\_layer>}$$

* **Production Examples:** `sales`, `finance`, `bronze`, `silver`, `gold`, `staging`, `meta`, `ctl`, `log`.

---

### 6.2 Tables
Tables within a schema or within a flat Lakehouse table directory follow strict prefixing:

$$\mathbf{Pattern:}\quad\text{<entity>}\quad\text{(within schema)}\quad\text{or}\quad\text{<schema>\_<entity>}\quad\text{(flat structure)}$$

| Table Category | Prefix / Convention | Guidance | Production Example |
| :--- | :---: | :--- | :--- |
| **General Tables** | *(none)* | Always use `snake_case` | `customer_orders`, `product_catalog` |
| **Fact Tables** | `fact_` | Prefix all transaction/accumulating facts with `fact_` | `fact_sales_transactions`, `fact_ar_ledger`, `fact_gl_ledger` |
| **Dimension Tables** | `dim_` | Prefix all conformed and shared dimensions with `dim_` | `dim_customer`, `dim_account`, `dim_date`, `dim_udc` |
| **Staging Tables** | `stg_` | Prefix all intermediate transient staging tables with `stg_` | `stg_raw_invoices`, `stg_f0911_staging` |

---

### 6.3 Columns
Column naming enforces strict cross-tool compatibility across Spark SQL, T-SQL, Python, and dbt:

| Column Category | Standard Suffix / Prefix | Guidance | Production Example |
| :--- | :---: | :--- | :--- |
| **General Columns** | *(none)* | Always use `snake_case` | `order_date`, `first_name`, `unit_price` |
| **Keys & Identifiers** | `_id` / `_key` / `_sk` | Suffix natural IDs with `_id`; surrogate keys with `_sk` | `customer_id`, `product_id`, `customer_sk`, `date_sk` |
| **Date & Timestamps** | `_date` / `_dt` / `_at` | Suffix calendar dates with `_date`; timestamps with `_at` | `created_date`, `modified_dt`, `_ingested_at`, `_fivetran_synced` |
| **Boolean Flags** | `is_` / `_flag` | Prefix with `is_` or suffix with `_flag` | `is_active`, `is_deleted_flag`, `_fivetran_deleted` |
| **Monetary & Quantities** | `_amt` / `_amount` / `_qty`| Suffix financial numbers with `_amount`; counts with `_qty` | `gross_amount`, `open_amount`, `shipped_qty`, `discount_amt` |

> [!TIP]
> Always use `snake_case` for Lakehouse Delta tables and Fabric Warehouse tables and columns. This ensures seamless cross-engine compatibility when querying between Spark SQL, T-SQL Analytics Endpoints, Python, and dbt.

---

## 7. Master Naming Convention Quick-Reference Cheat Sheet

The master reference table below outlines all resource categories, syntax patterns, and examples:

| Resource Type | Standard Pattern | Production Enterprise Example |
| :--- | :--- | :--- |
| **Capacity** | `<org>-<env>-fabric-<sku>-<instance>` | `contoso-prd-fabric-f64-001`, `ips-prd-fabric-f64-001` |
| **Domain** | `<business_function>` | `finance`, `sales`, `operations` |
| **Workspace** | `<domain>_<project>_<env>` | `sales_customer360_prd`, `bim_data_dev`, `bim_data_prd` |
| **Lakehouse** | `lh_<domain>_<layer>_<purpose>` | `lh_sales_bronze_raw_orders`, `lh_bronze_dev`, `lh_silver_dev` |
| **Warehouse** | `wh_<domain>_<purpose>` | `wh_finance_reporting`, `wh_sales_dimensional_model` |
| **Data Pipeline** | `pl_<action>_<target>_<detail>` | `pl_ingest_erp_orders_daily`, `pl_master_batch_orchestrator` |
| **Notebook** | `nb_<layer>_<domain>_<purpose>` | `nb_silver_sales_deduplication`, `nb_silver_generic_engine` |
| **Dataflow Gen2** | `df_<action>_<domain>_<detail>` | `df_clean_hr_employee_records` |
| **Semantic Model** | `sm_<domain>_<subject>` | `sm_sales_performance`, `sm_accounts_receivable_directlake` |
| **Power BI Report** | `rpt_<domain>_<purpose>` | `rpt_exec_monthly_performance`, `rpt_ar_aging_kpis` |
| **Eventstream** | `es_<source>_<purpose>` | `es_iot_device_telemetry` |
| **KQL Database** | `kql_<domain>_<purpose>` | `kql_security_event_logs` |
| **Spark Job Def** | `sjd_<domain>_<purpose>` | `sjd_sales_etl_daily_orders` |
| **Environment** | `env_<domain>_<purpose>` | `env_de_default_spark` |
| **Shortcut** | `sc_<source>_<target>` | `sc_adls_bronze_raw_files`, `landing_as400_crpdta` |
| **Schema** | `<domain>` or `<layer>` | `sales`, `finance`, `bronze`, `meta`, `ctl`, `stage` |
| **Table** | `<prefix>_<entity>` | `fact_sales_transactions`, `dim_customer`, `dim_date` |
| **Column** | `<descriptor>_<suffix>` | `customer_id`, `order_date`, `gross_amount`, `is_active` |

---

## 8. References & Official Microsoft Sources

![References & Official Documentation Links](/Users/chandu/Documents/Python_practice/Fabric/images/59_fabric_naming_convention_references_sources_p8.png)

This standard is aligned with official Microsoft documentation and architectural guidelines:

| # | Architecture Topic | Official Documentation Link |
| :---: | :--- | :--- |
| **1** | **Azure CAF — Resource Naming** | [learn.microsoft.com/.../resource-naming](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming) |
| **2** | **Fabric Workspace Planning — Naming Conventions** | [learn.microsoft.com/.../workspace-level-planning](https://learn.microsoft.com/fabric/governance/workspace-level-planning) |
| **3** | **Fabric Domains — Governance** | [learn.microsoft.com/.../domains](https://learn.microsoft.com/fabric/governance/domains) |
| **4** | **Fabric Lakehouse Overview** | [learn.microsoft.com/.../lakehouse-overview](https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview) |
| **5** | **Fabric Lakehouse Schemas** | [learn.microsoft.com/.../lakehouse-schemas](https://learn.microsoft.com/fabric/data-engineering/lakehouse-schemas) |
| **6** | **Fabric Data Warehousing** | [learn.microsoft.com/.../data-warehousing](https://learn.microsoft.com/fabric/data-warehouse/data-warehousing) |
| **7** | **OneLake Shortcuts** | [learn.microsoft.com/.../onelake-shortcuts](https://learn.microsoft.com/fabric/onelake/onelake-shortcuts) |
| **8** | **Eventstream Overview** | [learn.microsoft.com/.../event-streams/overview](https://learn.microsoft.com/fabric/real-time-analytics/event-streams/overview) |
| **9** | **KQL Database — Create** | [learn.microsoft.com/.../create-database](https://learn.microsoft.com/fabric/real-time-analytics/create-database) |
| **10** | **Deployment Pipelines** | [learn.microsoft.com/.../deployment-pipelines](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines) |
| **11** | **Power BI Semantic Model Guidance** | [learn.microsoft.com/.../usage-scenario-overview](https://learn.microsoft.com/power-bi/guidance/powerbi-implementation-planning-usage-scenario-overview) |

---

## Related Documentation
* **[Core Architecture Design Tenets & Governance Principles](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_BI_Core_Architecture_Design_Tenets_and_Governance_Principles.md)**
* **[Metadata-Driven Ingestion Framework Architecture Guide](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_Metadata_Driven_Ingestion_Framework_Architecture_Guide.md)**
* **[Fabric PySpark Development in VS Code Guidelines](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/Fabric_PySpark_Development_in_VSCode_Guidelines.md)**
* **[Fabric Connection Setup Guide (SPN & Variable Library)](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/Fabric_Connection_Setup_Guide_Service_Principal_Variable_Library.md)**
* **[On-Premises Data Gateway Installation & Configuration Guide](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_On_Premises_Data_Gateway_Installation_and_Configuration_Guide.md)**

