# IPS BI Modernization Project Design Document

> **LTM**
> *IPS BI Modernization project design document*
>
> **Document Version Details:** Ver. 1.4 / 18-Sep-2026
> **IPS BI Modernization Project**

---

## Record Release

| Version No. | Modified By | Reviewed By | Authorized By | Release Date | Modifications Done |
|-------------|-------------|-------------|---------------|-------------|-------------------|
| **1.0** | Nirmalya Chakraborty | Prathiba Gayam | Enterprise Architecture | 11-Aug-2026 | Initial Architecture Baseline & Medallion Framework Design |
| **1.1** | Nirmalya Chakraborty | Prathiba Gayam | Enterprise Architecture | 02-Sep-2026 | Approved Ingestion Framework V1.1 Integration (121 Datasets, 6 Ingestion Groups, Lakehouse Shortcuts, MDF Metastore sqldb-meta-orch-dev) |
| **1.2** | Nirmalya Chakraborty | Prathiba Gayam | Enterprise Architecture | 15-Sep-2026 | OPDG AS400 DB2 Connectivity Architecture (IPSRROD, Port 6017) & Microsoft Fabric CI/CD GitHub Actions Implementation |
| **1.3** | Nirmalya Chakraborty | Prathiba Gayam | Enterprise Architecture | 16-Sep-2026 | Incorporated Section 5: FinOps, Capacity Sizing & Cost Governance Architecture based on the Microsoft Fabric Capacity Cost & Financial Analysis baseline |
| **1.4** | Nirmalya Chakraborty | Prathiba Gayam | Enterprise Architecture | 18-Sep-2026 | Incorporated Section 6: Data Retention, Archival & Storage Layer Lifecycle Architecture (Retention Matrix, Delta Time Travel & Vacuum, Small File Compaction, and Maintenance Pipeline) |

---

## Table of Contents

- [1. Executive Summary & Project Overview](#1-executive-summary--project-overview)
  - [1.1 Purpose of the Document](#11-purpose-of-the-document)
  - [1.2 Business Objectives & Drivers](#12-business-objectives--drivers)
  - [1.3 Scope of Modernization](#13-scope-of-modernization)
  - [1.4 Architectural Scope & Core Pillars](#14-architectural-scope--core-pillars)
- [2. Architecture](#2-architecture)
  - [2.1 Architectural Diagram](#21-architectural-diagram)
  - [2.2 Source System & Dataset Inventory](#22-source-system--dataset-inventory)
  - [2.3 On-Premises Data Gateway (OPDG) Architecture & AS400 DB2 Connectivity](#23-on-premises-data-gateway-opdg-architecture--as400-db2-connectivity)
  - [2.4 Metadata-Driven Ingestion Framework (MDF) Architecture](#24-metadata-driven-ingestion-framework-mdf-architecture)
  - [2.5 Staging Area (Bronze Layer) & Lakehouse Shortcuts](#25-staging-area-bronze-layer--lakehouse-shortcuts)
  - [2.6 Data Transformation Layer (Silver Conformed Layer & DQ)](#26-data-transformation-layer-silver-conformed-layer--dq)
  - [2.7 Dimensional & Analytical Serving Layer](#27-dimensional--analytical-serving-layer)
    - [2.7.1 Technology and Processing Engine](#271-technology-and-processing-engine)
    - [2.7.2 Architectural Thought Process & Design Tenets](#272-architectural-thought-process--design-tenets)
    - [2.7.3 Star Schema Dimension Catalogue](#273-star-schema-dimension-catalogue)
    - [2.7.4 Star Schema Fact Catalogue](#274-star-schema-fact-catalogue)
    - [2.7.5 Enterprise Kimball Bus Matrix](#275-enterprise-kimball-bus-matrix)
  - [2.8 Power BI Semantic Layer & Analytical Reporting Architecture](#28-power-bi-semantic-layer--analytical-reporting-architecture)
  - [2.9 System Integration & SLA Alignment](#29-system-integration--sla-alignment)
- [3. CI/CD & DevOps Automation Architecture](#3-cicd--devops-automation-architecture)
  - [3.1 Prerequisites](#31-prerequisites)
  - [3.2 Reference Architecture](#32-reference-architecture)
  - [3.3 Deployment Mechanism Decision](#33-deployment-mechanism-decision)
  - [3.4 Repository and Branching Model](#34-repository-and-branching-model)
  - [3.5 Branching Strategy & Pull Request Policy](#35-branching-strategy--pull-request-policy)
  - [3.6 Authentication, Permissions and Secrets](#36-authentication-permissions-and-secrets)
  - [3.7 Implementation Procedure](#37-implementation-procedure)
  - [3.8 CI Validation Workflow](#38-ci-validation-workflow)
- [4. Testing Strategy, Quality Gates & Verification](#4-testing-strategy-quality-gates--verification)
  - [4.1 Unit & Integration Testing Quality Gates](#41-unit--integration-testing-quality-gates)
  - [4.2 Performance Benchmarking & User Acceptance Testing (UAT)](#42-performance-benchmarking--user-acceptance-testing-uat)
- [5. FinOps, Capacity Sizing & Cost Governance Architecture](#5-finops-capacity-sizing--cost-governance-architecture)
  - [5.1 Architectural Objectives & Operational Lifecycle Topology](#51-architectural-objectives--operational-lifecycle-topology)
  - [5.2 Fabric Capacity Unit (CU) Sizing & Regional Price Baseline](#52-fabric-capacity-unit-cu-sizing--regional-price-baseline)
  - [5.3 State 1: Implementation Phase Procurement & Scheduling Model (F128 + F64)](#53-state-1-implementation-phase-procurement--scheduling-model-f128--f64)
  - [5.4 State 2: Steady State Optimization & Rightsizing Model (F32 + F64)](#54-state-2-steady-state-optimization--rightsizing-model-f32--f64)
  - [5.5 Critical FinOps Governance: The Reservation Downscale Trap & Exchange Policies](#55-critical-finops-governance-the-reservation-downscale-trap--exchange-policies)
  - [5.6 Automated Capacity Lifecycle & Scheduler Architecture](#56-automated-capacity-lifecycle--scheduler-architecture)
  - [5.7 Compute Consumption Governance, Smoothing & Throttling Mitigation](#57-compute-consumption-governance-smoothing--throttling-mitigation)
  - [5.8 Milestones-Driven Implementation-to-Steady-State Transition Plan](#58-milestones-driven-implementation-to-steady-state-transition-plan)
  - [5.9 Deployment and Post-Deployment Activities](#59-deployment-and-post-deployment-activities)
  - [5.10 Testing Rollback and Operations](#510-testing-rollback-and-operations)
- [6. Data Retention, Archival & Storage Layer Lifecycle Architecture](#6-data-retention-archival--storage-layer-lifecycle-architecture)
  - [6.1 Architectural Scope & Storage Governance Tenets](#61-architectural-scope--storage-governance-tenets)
  - [6.2 Layer-Wise Data Retention Policy Matrix](#62-layer-wise-data-retention-policy-matrix)
  - [6.3 Delta Lake Lifecycle Management: Time Travel, Compaction & VACUUM Policies](#63-delta-lake-lifecycle-management-time-travel-compaction--vacuum-policies)
  - [6.4 Operational Implementation Plan & Maintenance Runbooks](#64-operational-implementation-plan--maintenance-runbooks)

---

## 4. Testing Strategy, Quality Gates & Verification

### 4.1 Unit & Integration Testing Quality Gates

Unit testing verifies individual PySpark transformation functions (Delta data converter, decimal shifter, whitespace trimmers).

Integration testing validates the complete end-to-end data pipeline in the SIT workspace: extracting test records from AS400 environment, landing in Bronze, executing Silver generic transformations, evaluating DQ rules, merging into Gold Star Schema, and verifying Direct Lake query responses.

### 4.2 Performance Benchmarking & User Acceptance Testing (UAT)

Performance benchmarks verify that:

1. **Batch extraction** of 58 tables across OPDG completes within the 45-minute scheduled window without exceeding 70% CU consumption.
2. **Silver PySpark** generic engine processes incremental rows in under 10 minutes on Fabric Starter Pools.
3. **Power BI Direct Lake** reports render executive visual queries in under 800 milliseconds for 95% of user interactions.
4. **Overall**, the 98% of data being available in consumption layer within 6 minutes of ingestion — verified for reports which are prepared from NRT datasets primarily with few exceptions.

During UAT in Pre-Production, Finance and Operations business stakeholders reconcile Power BI report figures against legacy JDE financial reports. A 100% variance-free reconciliation across General Ledger net balances, Accounts Receivable aging totals, and Accounts Payable open liability is required for formal production deployment sign-off.

> **NOTE — Testing strategy document:**
> For a detailed description of how the strategy for testing activity has been planned please refer to the document available at the shared location: *IPS Testing Strategy Document.url/link*

---

## 5. FinOps, Capacity Sizing & Cost Governance Architecture

### 5.1 Architectural Objectives & Operational Lifecycle Topology

A core architectural tenet of the IPS BI Modernization platform is financial predictability, fiscal efficiency, and automated capacity governance. Microsoft Fabric shifts compute procurement from traditional per-service infrastructure (e.g., dedicated Azure Data Factory integration runtimes, standalone Synapse/Databricks Spark clusters, and Analysis Services instances) to an aggregated, tenant-wide pool of Capacity Units (CUs).

To reconcile enterprise compute demand with fiscal responsibility, the platform architecture establishes two mutually exclusive operational lifecycle states:

- **State 1: Project Implementation Phase (192 CUs Total Footprint)**

  Non-Production Capacity (F128 – 128 CUs): Consolidates DEV, SIT, and UAT workspaces into a single high-throughput compute boundary. This capacity absorbs large-scale historical backfills across JDE AS400 tables, multi-tenant PySpark Silver and Gold Medallion transformations, dynamic DQ evaluations against metadata-driven rules, and high-concurrency UAT reporting queries without encountering compute throttling.

  Production Capacity (F64 – 64 CUs): Dedicated, fully isolated environment reserved for cutover preparation, synthetic end-to-end dry runs, and final production go-live cutover.

- **State 2: Steady State Operational Phase (96 CUs Total Footprint – SFR Compute Rated)**

  Non-Production Capacity (F32 – 32 CUs): Post go-live and formal UAT sign-off, SIT and UAT workloads are decommissioned. Non-production scales down to F32 for maintenance, enhancements, and ongoing DEV, while PROD remains on F64. Total organizational compute footprint contracts by 50% (from 192 CUs to 96 CUs).

  Production Capacity (F64 – 64 CUs): Remains dedicated to operational production workloads, orchestrating 58 scheduled batch extractions across the OPDG, continuous ingestion of 63 Near-Real-Time (NRT) delta streams via OneLake shortcuts, automated Gold-dimension calculation, Star Schema merges, and Direct Lake semantic model caching maintaining the sub-800ms query latency SLA.

> **ARCHITECTURAL MANDATE: TWO-PHASE TOPOLOGY**
>
> The platform explicitly distinguishes the temporary high-capacity requirements of implementation (192 CUs) from permanent steady-state operations (96 CUs). Compute commitments must never assume that implementation-level capacity is required permanently.

---

### 5.2 Fabric Capacity Unit (CU) Sizing & Regional Price Baseline

Microsoft Fabric compute billing is standardized on Capacity Units (CUs) consumed per second with ~5-minute resource allocation. Based on standard enterprise Azure commercial regions (e.g., East US / standard commercial regions), the architectural pricing baseline is established as follows:

- **Pay-As-You-Go (PAYG) Standard Rate:** $0.18 per CU / hour ($5.76/hr for F32, $11.52/hr for F64, $23.04/hr for F128).
- **1-Year Capacity Reservation Discount:** ~40.5% committed savings against continuous 24/7 PAYG compute rates.
- **Operational Billing Baseline:** 730 operating hours per calendar month (standard 24/7/365 operational availability).
- **Persistent Storage (OneLake):** Decoupled from compute; billed separately at Azure Data Lake Storage Gen2 standard rates ($0.023 per GB / month for active Delta Parquet storage).

| Fabric SKU | Compute (CUs) | PAYG Hourly | PAYG Monthly ($,760hr) | PAYG Annual | 1-Yr Reserved Monthly | 1-Yr Reserved Annual | Savings (%) |
|-----------|--------------|------------|----------------------|------------|---------------------|--------------------|----|
| **F32** | 32 CUs | $5.76 / hr | $4,204.80 | $50,457.60 | $2,509.00 | $51,072.00 | 40.5% |
| **F64** | 64 CUs | $11.52 / hr | $8,409.60 | $100,915.20 | $5,018.00 | $60,216.00 | 40.5% |
| **F128** | 128 CUs | $23.04 / hr | $16,819.20 | $201,830.40 | $10,036.00 | $100,036.00 | 40.5% |

---

### 5.3 State 1: Implementation Phase Procurement & Scheduling Model (F128 + F64)

During the implementation phase, DEV, SIT, and UAT share a high-throughput F128 capacity to support heavy data backfills, complex transformation testing (Bronze/Silver/Gold ingestion), and user acceptance testing, while PROD F64 is isolated for production cutover prep and go-live. Total compute footprint is 192 CUs.

To determine the optimal financial procurement strategy, four commercial procurement options were evaluated against cost, flexibility, and risk:

| Procurement Strategy | Non-Prod (F128) | Prod (F64) | Total Mo. Cost | Annualized Cost | Architectural Governance & Assessment |
|---------------------|----------------|-----------|---------------|----------------|--------------------------------------|
| **Option 1: 100% Pay-As-You-Go (24/7)** | $16,819.20 | $8,409.60 | $25,228.80 | $302,745.60 | Unrestricted agility; quick scale-in / scale-out for sprints |
| **Option 2: 100% 1-Year Reserved** | $10,036.00 | $5,018.00 | $15,054.00 | $180,648.00 | Lowest fixed-cost on paper; assumes both capacities run continuously for 12 months |
| **Option 3: Hybrid (Prod Reserved + Non-Prod PAYG 24/7)** | $16,819.20 | $5,018.00 | $21,837.20 | $262,046.40 | Business-critical PAYG continuity; high cost for non-production workloads |
| **Option 4: Hybrid (Prod Reserved + Non-Prod Scheduled PAYG)** | $8,995.84 | $5,018.00 | $14,013.84 | $168,166.08 | **(Recommended Baseline)** |

#### The Math Behind Option 4: Operational Mechanics & Mathematical Breakdown (Recommended Baseline)

Option 4 capitalizes on the cloud-native characteristics of Azure Resource Manager (ARM) Fabric capacity resources (Microsoft.Fabric/capacities): when a capacity is suspended/paused, Fabric billing ceases immediately ($0/hr). Storage in OneLake also persists at standard Gen2 rates.

> **Formula:** Total Monthly Cost = Cost(PROD Reserved) + Cost(Non-Prod Scheduled)
>
> Total Monthly Cost = $5,018.00 + (960 hours x $23.04/hour) = $5,018.00 + $8,995.84
> = **$10,983.40 / month ($131,920.88 annualized)**

---

### 5.4 State 2: Steady State Optimization & Rightsizing Model (F32 + F64)

Following project implementation, formal UAT sign-off, and production cutover, SIT and UAT are decommissioned. Non-production scales down to F32 for maintenance, enhancements, and ongoing DEV, while PROD remains on F64. Total organizational compute footprint contracts by 50% (from 192 CUs to 96 CUs).

| Pricing Strategy | Non-Prod (F32) | Prod (F64) | Total Monthly Spend | Total Annualized Spend | Key Notes & Recommendations |
|-----------------|---------------|-----------|--------------------|-----------------------|----------------------------|
| **Option 1: 100% Pay-As-You-Go (24/7)** | $4,204.80 | $8,409.60 | $12,614.40 | $151,372.80 | Unrestricted; highly inefficient for permanent steady-state operations |
| **Option 2: 100% 1-Year Reserved** | $2,509.00 | $5,018.00 | $7,504.00 | $90,048.00 | **RECOMMENDED:** Maximum steady-state commitment; ~40.5% lower than PAYG and $61,324.80/yr lower than initial 24/7 baseline |

---

### 5.5 Critical FinOps Governance: The Reservation Downscale Trap & Exchange Policies

> **CRITICAL FINOPS WARNING: THE RESERVATION DOWNSCALE TRAP**
>
> Do NOT purchase a 1-Year Capacity Reservation for F128 if implementation lasts less than 12 months! Azure Capacity Reservations are contractual commitments that CANNOT be exchanged to downscale total monetary value.

---

### 5.6 Automated Capacity Lifecycle & Scheduler Architecture

Fabric capacities are native Azure ARM resources under the provider namespace `Microsoft.Fabric/capacities`. When paused (suspended), all compute billing stops immediately ($0/hr). Only persistent OneLake storage is billed ($0.023/GB/month). Automation is implemented via native Azure ARM REST API endpoints:

**Suspend:**
```
POST https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/
Microsoft.Fabric/capacities/{capacityName}/suspend?api-version=2022-07-01-preview
```

**Resume:**
```
POST https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/
Microsoft.Fabric/capacities/{capacityName}/resume?api-version=2022-07-01-preview
```

#### Implementation Pattern: Automation Orchestration & Governance Mechanics

1. **Azure Logic Apps / Automation:** Scheduled recurring workflow triggers Mon–Fri at 07:00 AM (Resume) and 19:00 PM (Suspend) using a Managed Identity with *Contributor* role on the Non-Prod Resource Groups.

2. **Developer Self-Service Override with Auto Timeout:** For off-hours testing or weekend builds, authorized developers trigger an ad-hoc resume via a webhook. The Logic App enforces an automated 4-hour lease timeout, automatically re-suspending the capacity after 4 hours if not extended.

---

### 5.7 Compute Consumption Governance, Smoothing & Throttling Mitigation

Microsoft Fabric manages Capacity Unit consumption through advanced pooling and sliding-window smoothing algorithms:

- **Interactive Operations** (Power BI, Direct Lake queries, interactive notebooks): Smoothed over a 5-minute sliding window.
- **Background Operations** (Scheduled MDF batch ingestion, PySpark Silver/Gold pipelines): Smoothed over a 24-hour sliding window.

#### Workload Optimization: Platform Optimization Tenets

- **Fabric Capacity Metrics App:** Deploy the official Capacity Metrics App to monitor hourly CU burn, with automated alerts when capacity utilization exceeds 80% for two consecutive 15-minute intervals.

---

### 5.8 Milestones-Driven Implementation-to-Steady-State Transition Plan

The transition from the high-throughput implementation phase (192 CUs) to the cost-optimized steady state (96 CUs) is governed by strict, measurable quality and financial gate criteria:

| Phase Milestone | Verification & Exit Criteria | Accountable Owner | Financial & Estimated Response |
|----------------|-----------------------------|--------------------|-------------------------------|
| **M1: Foundation & Backfill** | Ensure F128 Logic App scheduler is active; completed at 40.5% discount vs. PAYG baseline | Data Engineering Lead | Verify F128 capacity scheduled (Mon-Fri business hours, ~960 hrs/mo). Total Cost = $5,018.00 + (960 hours x $23.04/hr) = $5,018.00 + $8,995.84 = **$10,983.40 / month** ($131,920.88 annualized) |
| **M2: UAT Execution** | Validate end-to-end connectivity; multi-user concurrency load tests | Finance Lead | Verify F128 capacity running; App confirms interactive throttling |
| **M3: Production Cutover** | GA Live; completed F128 operations; 24/7 auto-scaling data reference between JDE Architecture | Data Engineering Lead | PROD F64 at full 24/7; confirm cutover to steady-state |
| **M4: 14-Day Hypercare** | 14 consecutive business days without critical pipeline failures and sub-800ms reporting latency | Platform Lead | Confirm SIT and UAT are decommissioned; prepare for capacity downscale |
| **M5: Steady-State Reservation Purchase** | Formal sign-off of SIT and UAT decommissioning; workspace Git branch tagged and archived | — | Decommission F128 capacity. F32 Reservation on Azure Portal |

#### Steady-State Component Sizing

| Component | Sizing & Rate Baseline | Operational Hours | Monthly Calculation | Total Monthly Cost |
|-----------|----------------------|-------------------|--------------------|--------------------|
| **Non-Prod** | F64 (64 CUs) (14 hr/day x 20 business days) | Scheduled at 40.5% discount (Mon-Fri business hours, ~280 hrs/mo) | $11.52/hr x 280hrs | $3,225.60 |
| **Prod** | F64 (64 CUs) (24/7) | Reserved + Non-Prod Scheduled PAYG 24/7 | $5,018.00/mo | $5,018.00 |

---

### 5.9 Deployment and Post-Deployment Activities

| # | Step | Description |
|---|------|-------------|
| 1 | Deploy Fabric item definitions | Fabric .conf.log and deployment manifest |
| 2 | Resolve environment-specific values | Apply parameter file or variable-library value set |
| 3 | Rebind notebooks, lakehouses, connections, or semantic models where supported | Post-deployment script output and target ID verification |
| 4 | Run setup notebooks or DDL scripts for lakehouses/schemas/tables | Idempotent CREATE/ALTER scripts; execution status returned |
| 5 | Enable schedules and failure notifications | Only after functional validation; use an approved environment distribution list |
| 6 | Run smoke tests | API responses, item existence, connection test, and critical pipeline/notebook executions |
| 7 | Record release | Commit SHA, tag, target workspace, approver, result, and rollback reference |

#### Rollback Strategy

- Identify the last well-known Git tag and deployment manifest.
- Disable affected schedules before rollback if continuing execution could cause duplicate or incorrect processing.
- Redeploy the last good definitions using the same workflow and target GitHub Environment.

#### Monitoring & Support

- Store GitHub Actions logs and deployment manifests according to organizational policy.
- Monitor critical Fabric jobs after deployment and capture item/job IDs in incident records.
- For intermittent workspace branching or Git synchronization failures, record capacity region, GitHub region/provider, workspace limits, correlation IDs, and timestamps before raising a Microsoft support request.

---

### 5.10 Testing Rollback and Operations

#### Quality Gates

| Environment | Minimum Checks | Pass Criteria |
|------------|---------------|---------------|
| **PR / CI** | Syntax, lint, secrets, definition integrity, naming, scope | All automated checks pass and require reviewer approval |
| **QA Deployment** | Deploy, bind, configure, execute representative notebook/pipeline | No failed items; environment references point to QA |
| **Pre-production** | Regression, permissions, schedule readiness, data validation | Business/technical sign-off recorded |
| **Production** | Approved tag, environment approval, smoke tests, monitoring | Deployment and post-deployment steps all succeed |

---

## 6. Data Retention, Archival & Storage Layer Lifecycle Architecture

### 6.1 Architectural Scope & Storage Governance Tenets

In the Microsoft Fabric Medallion Architecture of the IPS BI Modernization platform, storage management transitions from siloed database disks to a unified, globally distributed enterprise lake (OneLake). All tables across Bronze, Silver, and Gold persist as open-format Delta Lake (Delta Parquet) files.

While OneLake eliminates data silos through shortcuts and unified storage ($0.023 per GB / month), an unmanaged Delta Lake environment introduces critical architectural, operational, and financial risks:

1. **Delta Log & Version Accumulation:** Frequent micro-batch ingestions (63 Near-Real-Time tables) and periodic batch pipelines (58 AS400 tables) generate hundreds of thousands of microscopic Parquet files and obsolete Delta log commits (`_delta_log`), causing severe metadata bloat, query degradation, and compounding storage costs.

2. **Quarantine Data Abandonment:** Without a formal retention policy, defective records routed to dataset-specific quarantine tables (`*_entity_quarantine`) grow unbounded, consuming high-cost hot storage.

3. **Direct Lake Cache Eviction:** Excessive Delta file fragmentation directly impedes Power BI Direct Lake performance, triggering expensive memory-paging fallbacks to DirectQuery mode.

> **ARCHITECTURAL MANDATE: ONELAKE STORAGE HYGIENE**
>
> The platform mandates deterministic layer-wise retention, automated weekly file compaction (OPTIMIZE with V-Order), weekly dead-file vacuuming (VACUUM RETAIN 7 DAYS), and cold ADLS Gen2 archival for closed historical fiscal years. Reclaims stranded OneLake storage, directly preventing capacity storage creep.

---

### 6.2 Layer-Wise Data Retention Policy Matrix

Data retention across the IPS BI Modernization platform is governed by functional requirements, business audit obligations, and statutory regulations. The lifecycle of each data artifact is deterministic and automated.

| Storage Layer | Data Artifact / Entity | Retention Window | Retention Tier | Storage Target | Purge & Archival Action |
|--------------|----------------------|-----------------|---------------|---------------|------------------------|
| **Bronze** (th_bronze) | Batch Raw Staging Tables (53 AS400 / 502 Tables) | 90 Days (Rolling History) | Hot | OneLake | Enables backfill replay and historical reconciliation / recovery in the event of pipeline upstream source failure. Automated truncation of staging partitions older than 90-day via scheduled maintenance. |
| **Bronze** (th_bronze) | NRT Delta Shortcuts (63 Eventstream Tables) | Synchronized with Source (In-place Shortcut) | Hot | OneLake | Drives storage; retention lifecycle is managed in the source Eventstream publisher. Pass-through retention governance — lifecycle is publisher-managed. |
| **Silver** | Conformed Master & Transaction Tables (Cleansed JDE Data) | 3 Years (Rolling Active Window) | Warm | OneLake | Operational reporting, multi-year trend analysis, & source of truth for dimensional models. Records older than 3 years are automatically archived to Cold ADLS Gen2. |
| **Gold** (th_silver) | Silver Archive Tables (th_delta_named_quarantine) | 90 Days | Warm | OneLake | Provides data stewards sufficient time to investigate, remediate, and replay failed records. Quarantine sub-90 day records auto-investigated, remediated, consumed and purged. |
| **Gold** (th_gold) | Active Financial Facts (Fact_GL_Transactions, Fact_All_Aging, Fact_AP_Open, Fact_AP_Close, Fact_AR_Open) | Current FY + Preceding 3 FYs (Direct Access) | Hot (Direct) | OneLake | Guarantees sub-100ms reporting latency for 99% of active enterprise queries without consuming unnecessary RM4. |
| **Gold** (th_gold) | Historical Financial Facts (Fiscal Years 4 through 7+) | 7 Years Total (statutory Audit) | Cold | ADLS Gen2 (Archive Shortcut) | Mandatory compliance with SEC, ILC and statutory requirements. Compressed and moved to external ADLS Gen2 archive. |

---

### 6.3 Delta Lake Lifecycle Management: Time Travel, Compaction & VACUUM Policies

Because all tables in Microsoft Fabric are stored in Delta Lake format, standard database retention operations must be implemented with storage-level file hygiene mechanisms:

1. **Delta Time Travel Retention Configuration** allows 7 days. Time travel is engineered to 7 days for all historical tables via `delta.logRetentionDuration = 7 days` (SELECT * FROM table_name TIMESTAMP AS OF `timestamp`).
   - If an accidental or erroneous overwrite occurs, *Time travel duration must NEVER be set below 7 days* in Production to protect concurrent Direct Lake reporting queries.

2. **File Compaction (OPTIMIZE)** & the **Small File Problem:** Micro-batch ingestion generates thousands of small (< 1MB) Parquet files. The platform enforces automated execution of OPTIMIZE across all active tables to bin-pack small files into 128 MB – 1 GB target files, the optimal V2 boundary for OneLake and VertiPaq Direct Lake projections.

3. **Microsoft Fabric V-Order Dictionaries:** Proprietary variable-length run-time-optimized dictionary that sorts, encodes, and compresses Parquet files to maximize the V1/V2 in-memory columnar compression — compatibility with Power BI VertiPaq. Mandated for all Silver (conformed) and Gold tables.

#### Delta Settings / Parameter Table

| Target Lakehouse | Delta Setting / Parameter | Target Value | Operational Cadence | Architectural Objective |
|-----------------|--------------------------|-------------|--------------------|-----------------------|
| **All Lakehouses** | `delta.deletedFileRetentionDuration` | interval 7 days | Continuous (Property) | Enforces 7-day disaster recovery Time Travel window while expiring stale file storage |
| **All Lakehouses** | `delta.logRetentionDuration` | interval 30 days | Continuous (Table Property) | Retains transaction log commit history for 30 days — enables checkpoint transactions |
| **Bronze** (th_bronze) | OPTIMIZE (Bin-Packing) | Target 128 MB (~999 CUs) | Weekly (Sunday 09:00 UTC) | Compacts batch/live partitions, file application |
| **Silver** (th_silver) | OPTIMIZE + V-Order | Target 256 MB | Weekly (Sunday 09:00 UTC) | Maximizes PolySpark read throughput; enables Fast V-Order Dictionaries |
| **Gold** (th_gold) | OPTIMIZE + V-Order + Z-ORDER BY | Target 512 MB | Weekly (Sunday 09:00 UTC) | Guarantees sub-100ms Power BI direct query latency |

#### VACUUM Policies

| Target Lakehouse | Delta Setting / Parameter | Target Value | Operational Cadence | Architectural Objective |
|-----------------|--------------------------|-------------|--------------------|-----------------------|
| **All** | VACUUM | RETAIN 168 HOURS (7 Days) | Weekly (Sunday 04:00 UTC) | Permanently reclaims Parquet files; prevents storage bill inflation |

> **CAUTION: HARD DELETE VACUUM OVERRIDE**
>
> Executing VACUUM with RETAIN HOURS which is less than 168 (7 days) requires explicit authorization from the a person with administrative rights and must be scheduled during dedicated maintenance windows to prevent disrupting concurrent Direct Lake reporting queries.

#### Storage Layer Retention & Archival Runtime Details

| Storage Layer | Data Artifact / Entity | Retention Window | Storage Target | Retention & Archival Runtime |
|--------------|----------------------|-----------------|---------------|------------------------------|
| **Gold** (th_gold) | Conformed Dimensions (DIM_Business_Unit, DIM_Account, IDCD 1 & 2) | Indefinite | Hot OneLake | Monotonic data accumulation requiring 1-year audit trails. Master dimension archives on hot cache; preserve Type 2 versioning. Triggered via surplus file merge. |
| **Metastore** (meta) | Pipelines & Ingestion Logic (log_th_ingestion_metrics) | 180 Days | Hot Azure Data Lake (OneLake) | Day-to-day operational visibility; deleted from hot tier after 6 months. Trend analysis of ingestion and SLA reporting. |
| **Metastore** (meta) | Data Quality Audit Logs (log_th_evaluation_metrics) | 1 Year / Active | Hot Azure Data Lake (OneLake) | Trend analysis of quality and SLA reporting. |

---

### 6.4 Operational Implementation Plan & Maintenance Runbooks

Storage governance is fully operationalized through a dedicated, scheduled orchestration pipeline at Fabric, storage, maintenance. The pipeline executes weekly during off-peak hours (Sunday 09:00 AM – 06:00 AM UTC), coordinating maintenance across all Lakehouse items.

| Maintenance Job | Execution Cadence | Target Workspace | Processing Engine | SLA / Expected Runtime |
|----------------|-------------------|-----------------|-------------------|----------------------|
| **Bronze Partition Pruning** | Weekly (Sunday 09:00 UTC) | DEV, SIT, SRC, PROD | PySpark (nb_function_processing) | ~15 minutes |
| **Quarantine Table Purge** | Weekly (Sunday 09:30 UTC) | DEV, SIT, SRC, PROD | PySpark (nb_quarantine_purge) | — |
| **Delta OPTIMIZE & V-Order** | Weekly (Sunday 10:00 UTC) | DEV, SIT, SRC, PROD | Spark Starter Pool (nb_optimize) | ~45 minutes |
| **Gold Z-Order Clustering** | Weekly (Sunday 10:00 UTC) | PROD Only | High-Concurrency Spark Pool | — |
| **Delta VACUUM** | Weekly (Sunday 04:00 UTC) | DEV, SIT, SRC, PROD | PySpark (nb_vacuum) | ~35 minutes |

---

## 2. Data Model & Analytical Architecture (Continued)

### 2.7.4 Star Schema Fact Catalogue

The analytical fact layer models the organization's core financial and operational lifecycles across five distinct Fact tables.

| Fact Table Name | Source Tables & Entities | Fact Grain & Keys | Fact Type | Conformed Foreign Keys (FK) | Key Metrics & Load Strategy |
|----------------|------------------------|-------------------|-----------|---------------------------|---------------------------|
| **Fact_GL_Transactions** | CRPOTA.F0911, etc. | Individual Journal Entry Line (BU/OBJ/SUB/DOC/LN/JE/LN/OUT) | Transactional | fk_dim_Account, fk_Dim_Company, fk_Dim_Account_Balance_c, fk_dim_Supplier_Address, fk_Dim_Doc_type, fk_dim_Business_Unit, sb_pmtd_vn, sb_adj_vn | General Ledger journal transactions; full audit trail of financial postings |
| **Fact_AR_Open_Receivable** | CRPOTA.F03B11 | Open Receivable Line (RPxOG/RPDCT/RPDOC/RPSFX) | Transactional | fk_dim_Company, fk_dim_Account, fk_Dim_Calendar, fk_Dim_Business_Unit, fk_Dim_Doc_type, rp_chn, rp_crr, rp_rmrk, fk_dim_Address, fk_dim_Customer_adj | Open receivables tracking; aging buckets, amounts, due dates, payment terms |
| **Fact_Account_Payable_Voucher** | CRPOTA.F0411 | Accounts Payable Voucher Line (RPRCO/RPDCT/RPVOD/RPDSFX) | Financial | fk_Dim_Company, fk_dim_Account, fk_Dim_Calendar, fk_Dim_Business_Unit, fk_dim_Supplier_Address, fk_Dim_Doc_type | AP voucher lifecycle; payment status, discount calculations, open liability |
| **Fact_Prct_Balance** | CRPOTA.PERCC | Account + Ledger + Year + SubLedger | Period | fk_dim_Account, fk_Dim_Company, fk_Dim_Calendar, fk_Dim_Business_Unit | Periodic balance snapshots; budget vs. actual comparisons, variance analysis |
| **Fact_Customer_AB** | Derived from Customer + Snapshot Date | Customer + Snapshot Date | Snapshot | fk_dim_Address, fk_Dim_Calendar, fk_dim_Customer_adj | Customer account balance snapshots; balance tracking over time |

---

### 2.7.5 Enterprise Kimball Bus Matrix

The conformed bus matrix demonstrates how the 16 enterprise dimensions intersect across the 5 core business process fact tables.

**Dimension Legend:**
COB=Customer, CMP=Company, CAL=Calendar, ACC=Account, BU=Business Unit, SUP=Supplier, ADD=Address, CNT=Contact, DOC=Document Type, PMT=Payment Term, CRR=Currency, FX=Currency Exchange Rate, BAL=Account Balance, AST=Asset, ABAL=Asset Account Balance.

#### Conformed Dimension Reference

| Dimension | Source Table | Key Columns | Grain | SCD Type | Description |
|-----------|-------------|-------------|-------|----------|-------------|
| **DIM_Currency_Exchange_Rate** | CRPCL1.F0015 | CRCHCD, CRCRDC, CRCRT1, CXEFT | From + To + Type + Date | SCD Type 1 | Conversion Rate, Divisor Rate, Spot vs. Budget Rate, Effective Range. Rates table for currency standardization. |
| **DIM_Account_Balance** | CRPOTA.F0902 | GBAID1, GBFY (GELT, GBBB, GBCRCD, GBCO) | Account + Ledger + Year + SubLedger | SCD Type 1 | SubLedger, SubLedger Type, Fiscal Year, Currency Code. Supports multi-ledger balance comparisons (AA vs. CA). |
| **DIM_Asset** | CRPOTA.F1201 | FA#UMB | Asset Item Number | SCD Type 2 | Major Accounting Class, Asset Description, Depreciation Method, Serial Number, Cost Account. Fixed asset register. |
| **DIM_Asset_Account_Balance** | CRPOTA.F1202 | Account_ID1, FA#UMB1, CarNum1 | Asset + Item + CarNum | SCD Type 1 | Historical cost, accumulated depreciation, capitalization methods (ITD / Remaining). Asset balance tracking. |

> **[INTERACTIVE MODEL ARTIFACT: ENTERPRISE STAR SCHEMA & BUS MATRIX VISUALIZER]**
>
> A dedicated, interactive, web-based Star Schema Visualizer has been engineered and published directly into the project repository to provide data architects, engineers, and BI analysts with an exploratory model interface for all gold tier entities (5 Facts and 16 Conformed Dimensions).
>
> **Key Visualizer Capabilities:**
> 1. Star Schema Visual Canvas with pan/zoom and relational highlighting
> 2. Interactive Kimball Bus Matrix with click-to-filter grain explorers
> 3. Multilevel Lineage tracing from raw AS400 tables to Bronze to Direct Lake
> 4. Multi-Fact coverage (General Ledger, All & Risk, AP, Fixed Assets, SCID2)
> 5. Instant search across JDE source tables (e.g., F0911, F03B11, F0411, F0191)
>
> **Interactive Visualizer Link:** *[Enterprise Star Schema Visualizer (schema_viewer.html)]*
>
> *Note: It will render perfectly if you download the HTML in local folder and render it in Chrome or any other browser.*

---

### 2.8 Power BI Semantic Layer & Analytical Reporting Architecture

#### Direct Lake Mode Architecture & In-Memory VertiPaq Caching

Power BI reports connect to Gold Delta Lake tables using Direct Lake mode. Direct Lake mode reads Delta Parquet files directly from OneLake into the VertiPaq memory engine without data copying or scheduled dataset refreshes, combining the schema performance of import mode with the real-time freshness of DirectQuery.

#### Lakehouse SQL Analytics Endpoint Automatic Sync & Fallback Prevention

To ensure semantic models never fall back from Direct Lake to DirectQuery (which degrades performance on complex DAX calculations), the architecture enforces direct batch writes:

**Control 1: Synchronized Delta Metadata.** Following notebook batch write, `nb_force_sync_lakehouse_api_endpoint` triggers an automatic metadata sync ensuring the SQL Endpoint and semantic model reflect updated Delta transaction log state.

**Control 2: Compatible Data Types.** Strict avoidance of unsupported types (VARCHAR(MAX), binary, blob). All string attributes are bounded VARCHAR(N) and amounts are Decimal(19,4).

**Control 3: Direct Lake Only Enforcement.** Semantic model properties enforce `Direct.LakeBehavior` is set to `Automatic/DirectLakeOnly`, rejecting queries rather than silently falling back to slow DirectQuery over JDBC.

**Control 4: V-Order Parquet Optimization.** All Gold tables are written with Spark configuration:
```
spark.sql.parquet.vorder.enabled = true
```
Maximizing columnar VertiPaq encoding.

> **NOTE — Semantic Models, Measures & Enterprise Reporting Inventory**
>
> For a detailed description of how the Power BI Semantic Models serve enterprise analytics refer to the document at the shared location:
> *IPS_CORP_PowerBI_Fabric_Deployment_Architecture_Final.docx*

---

### 2.9 System Integration & SLA Alignment

#### Step-by-Step Runtime Execution Flow (7-Step Lifecycle)

The ingestion framework executes across seven distinct, automated lifecycle stages for every pipeline invocation:

- **Step 1: Pipeline Initiation & Parameter Resolution:** When a Fabric pipeline triggers for a specific `group_code`, it queries `meta.ingestion_group` and `meta.ingestion_group_dataset` to retrieve all active, enabled `dataset_id` instances mapped to that group.

- **Step 2: Master Run Logging:** The orchestration engine inserts a new record into `log.pipeline_runs` with `per_status_code = IN_PROGRESS` and receives a generated `pipeline_run_id`.

- **Step 3: Source-to-Bronze Extraction:** For each `dataset_id`, the Copy Activity pairs `meta.dataset_src_to_brz` with `ctl.watermark_state` to determine dynamic queries or watermark boundaries (e.g., `WHERE UPDATE > '2025-05-01'`). Row files and time are entity-logged in `log_dataset_run`.

- **Step 4: Bronze-to-Silver Cleansing & DQ Enforcement:** A generic PySpark notebook is invoked with `dataset_id` as a parameter. It reads configuration parameters from `meta.dataset_brz_to_silver`, fetches active DQ rules from `meta.dq_rules` (mandatory, nullable, `rule_expression`), evaluates them against the PySpark Detail name.

- **Step 5: Dynamic Quarantine Routing:** Evaluation metrics (`rows_evaluated`, `rows_passed`, `rows_failed`) are written to `log_dq_eval`. If invalid rows exist, they are directed into dataset-specific Delta quarantine tables. If a retry rule (`STOP_IF_PERCENT`) fires, execution is stopped; an exception is logged to `log_event` and event aborts.

- **Step 6: Silver-to-Gold Dimensional Transformation:** PySpark notebooks merge conformed Silver entities into Gold Star Schema Dimensional and Fact tables.

- **Step 7: State & Watermark Finalization:** Upon successful completion, the framework executes atomic T-SQL updates: `ctl.watermark_state.last_success_watermark`, status with the `max_extracted_watermark`, updates `ctl.dataset_state.last_run_status = 'SUCCESS'` and finalizes `log.dataset_run` and `log.pipeline_run` with timestamps and total processed row counts.

#### Non-Functional Requirement: End-to-End Latency

To satisfy the non-functional requirement (NFR):

*"Data once entered in the source system (AS400/DB2) must be visible in the consumer layer (Power BI report) no later than 15 minutes."*

**The End-to-End Latency Equation:**

To guarantee compliance, the total latency budget T<sub>total</sub> must satisfy:

> T<sub>total</sub> = T(Evenstream Extract & Land) + T(Pipeline_Wait) + T(Bronze_Ingest) + T(Silver_Engine) + T(Gold Fact/Dim Engine) + T(PBI Direct Lake Refresh) **≤ 15 minutes**

#### Automating Metadata Refresh

Although Direct Lake reads files directly, the semantic model must query the latest transaction logs to discover newly written Parquet files. To ensure this happens instantly upon Spark notebook completion, the ETL pipeline must trigger a metadata sync.

This is accomplished by adding a **Web Activity** at the end of the Fabric Pipeline that calls the Power BI REST API to refresh the semantic model. Because this is a metadata-only sync (not a data load), the execution completes in under 1 second.

**REST API Refresh Configuration:**

- **Endpoint:**
  ```
  https://app.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes
  ```
- **Method:** POST
- **Request Body:**
  ```json
  {
      "type": "clearCacheAndRehydrate"
  }
  ```

---

## 3. CI/CD & DevOps Automation Architecture

This section defines an enterprise-ready approach for implementing continuous integration and continuous delivery for Microsoft Fabric content using GitHub Actions. It is designed for teams working with Fabric notebooks, data pipelines, lakehouses, warehouses, environments, variable libraries, semantic models, and reports, subject to the current support matrix for each deployment mechanism.

| Stage | Primary Activity | Outcome |
|-------|-----------------|---------|
| **Dev workspaces** (shared workspaces) | Create or update Fabric items in a shared workspace linked to a dev branch | Changes are version-controlled modifying the shared development workspace |
| **Pull request / CI** | Validate repository structure, item definitions, naming, security, and merge readiness | Only reviewed and validated changes enter the integration branch |
| **SIT/UAT** | Deploy selected Fabric definitions using fabric-cicd or Fabric APIs, then run post-deployment automation | A repeatable test environment is created from Git |
| **Production** | Deploy an approved tag or release through a protected GitHub environment | Production receives an immutable, traceable release |

---

### 3.1 Prerequisites

| Area | Requirement |
|------|-------------|
| **GitHub** | Repository admin access, Actions enabled, protected branches, GitHub Environments, and permission to manage secrets/variables |
| **Identity** | Microsoft Entra app registration or workload identity. For client secret authentication, retain the tenant ID, client ID, and secret value |
| **Fabric tenant** | Tenant configuration must permit the service principal to use Fabric APIs. Add the identity to each target workspace with the least role that supports the required operations |
| **Runner** | GitHub-hosted or approved self-hosted runner with Python 3.10+ and network access to required Microsoft endpoints |
| **Repository content** | Fabric item definitions synchronized to Git and deployment scripts stored alongside the definitions |

---

### 3.2 Reference Architecture

```
Developer → Features/Fabric workspace → Feature branch → Pull request
                    ↓
            Commit Fabric item definitions
                    ↓
Pull request → CI validation → Review/approval → Merge to develop/main
                    ↓                                      ↓
            SIT workspace                           UAT workspace → Prod workspace
                    ↓                                      ↓              ↓
            post-deploy scripts              post-deploy scripts    post-deploy scripts
```

---

### 3.3 Deployment Mechanism Decision

| Mechanism | Description | Outcome |
|-----------|-------------|---------|
| **Fabric/Git updates-from-Git API** | Each target stage has a dedicated branch and workspace Git connection | GitOps-style, branch-per-stage deployment |
| **Fabric Items APIs / fabric-cicd** | A single source branch is transformed and deployed to unconnected target workspaces | Supports environment-specific replacement and code-first deployment |
| **Fabric deployment pipelines** | The team wants a Fabric-native deployment promotion mechanism | Fabric workspace is the delivery source; Git is typically connected to development |
| **Hybrid** | Some items require alternative or manual handling | Combines definition deployment with controlled post-deployment steps |

---

### 3.4 Repository and Branching Model

#### Repository Structure

```
.github/
  workflows/
    ci-validate.yml
    deploy-fabric.yml
config/
  parameter-dev.yml
  parameter-sit.yml
  parameter-uat.yml
  parameter-prod.yml
deploy/
  deploy_workspace.py
  validate_repo.py
  post_deploy.py
fabric/
  <workspace item folders generated by Fabric Git integration>
tests/
  test_definitions.py
requirements.txt
README.md
CODEOWNERS
```

---

### 3.5 Branching Strategy & Pull Request Policy

| Branch | Purpose | Outcome |
|--------|---------|---------|
| **dev** | Shared integration branch mapped to the shared Dev workspace | Shared code will be available in this branch |
| **main** | Release-ready source of truth | Protected; merge from develop/release only; production deployment uses an approved tag or release |
| **release** | Stabilization for a planned release | Pull request, successful CI checks, at least one reviewer |

**The pull request policy will be constituted as:**

- Require successful repository validation and secret scanning.
- Require CODEOWNERS review for workflow, deployment, and configuration files.
- Prevent direct pushes to develop and main.
- Resolve Fabric item definition conflicts before merge.
- Use squash or merge commits consistently and preserve traceability to the work item.

**Developer Workflow:**

- Each developer works in shared workspace. And Commit Fabric-generated item definitions to the dev branch with commit messages.
- Commit message: `<featurename>` in GitHub Activity.
- Open a pull request from this dev branch to release branch and complete CI checks and review.

---

### 3.6 Authentication, Permissions and Secrets

#### GitHub Environment Assets

| Variable | Type | Description |
|----------|------|-------------|
| `AZURE_TENANT_ID` | Secret or variable | Microsoft Entra tenant identifier |
| `AZURE_CLIENT_ID` | Secret | Deployment application client identifier |
| `AZURE_CLIENT_SECRET` | Environment secret | Only when secret-based authentication is used |
| `FABRIC_WORKSPACE_ID` | Environment variable | Target workspace GUID for the selected GitHub Environment |
| `FABRIC_ENVIRONMENT` | Environment variable | SIT, UAT, PROD |
| `FABRIC_ITEMS_IN_SCOPE` | Environment variable | Comma-separated supported item types or deployment scope |

#### Least-Privilege Checklist

- Create a dedicated deployment identity rather than using a personal user.
- Enable the required Fabric tenant setting for service principal API access.
- Add the identity only to target workspaces it must deploy to.
- Protect the identity credentials with GitHub Environments.
- Avoid printing tokens, secrets, or full access responses in workflow logs.
- Rotate or revoke credentials immediately after suspected exposure.

---

### 3.7 Implementation Procedure

Configure Fabric and GitHub integration for development:

- Create or identify the shared Dev workspace and connect it to the approved GitHub repository and dev branch.

#### Python Dependencies

```txt
# requirements.txt
fabric-cicd
azure-identity
requests
```

#### Deployment Script Template

```python
# deploy/deploy_workspace.py
import os
from azure.identity import ClientSecretCredential
from fabric_cicd import FabricWorkspace, publish_all_items

credential = ClientSecretCredential(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"],
)

workspace = FabricWorkspace(
    workspace_id=os.environ["FABRIC_WORKSPACE_ID"],
    environment=os.environ["FABRIC_ENVIRONMENT"],
    item_type_in_scope=os.environ.get("FABRIC_ITEMS_IN_SCOPE", "").split(","),
    repository_directory=".",
)

publish_all_items(workspace)
```

#### GitHub Actions Deployment Workflow

```yaml
name: Deploy Microsoft Fabric

on:
  workflow_dispatch:
  push:
    branches: [develop]
    paths: ["fabric/**", "deploy/**", "config/**"]

permissions:
  contents: read

concurrency:
  group: fabric-${{ github.event.inputs.target || 'us' }}
  cancel-in-progress: false

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python deploy/validate_repo.py

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.target || 'SIT' }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - name: Deploy Fabric Items
        env:
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          FABRIC_WORKSPACE_ID: ${{ vars.FABRIC_WORKSPACE_ID }}
          FABRIC_ENVIRONMENT: ${{ vars.FABRIC_ENVIRONMENT }}
          FABRIC_ITEMS_IN_SCOPE: ${{ vars.FABRIC_ITEMS_IN_SCOPE }}
        run: python deploy/deploy_workspace.py
      - name: Post-deployment verification
        env:
          FABRIC_WORKSPACE_ID: ${{ vars.FABRIC_WORKSPACE_ID }}
        run: python deploy/post_deploy.py
```

#### Post-Deployment Verification

```yaml
      - name: Post-deployment verification
        env:
          FABRIC_WORKSPACE_ID: ${{ vars.FABRIC_WORKSPACE_ID }}
        run: python deploy/post_deploy.py
```

---

### 3.8 CI Validation Workflow

- Validate required folders and JSON/YAML syntax.
- Reject empty or malformed Fabric item definitions.
- Check that environment IDs, connection strings, and secrets are not hard-coded.
- Run Python linting and unit tests for deployment scripts.
- Verify that only approved item types and paths changed.
- Produce a deployment manifest as a workflow artifact.

#### Lakehouse Specific Approach

- Treat the Git-synchronized Lakehouse definition as metadata, not as the transport for OneLake data.
- Maintain schema creation and evolution as idempotent notebook or SQL deployment scripts.
- Execute setup notebooks after the workspace definitions are deployed.
- Keep static configuration or lookup files in a controlled repository path and upload them to approved OneLake/Fabric APIs when required.
- Never hard-code workspace or Lakehouse IDs. Resolve them from environment configuration Fabric APIs.

#### Variable Library and Naming Consistency

**Operational lesson:** Environment keys must be identical across variable libraries, metadata tables, notebook logic, and workflows. A mismatch such as PRD versus PROD can allow the deployment to succeed while runtime schedules fail. Add a CI check that compares the permitted environment codes.

---

## 1. Project Overview (Continued)

### 1.4 Architectural Scope & Core Pillars

The architectural and technical scope detailed in this document encompasses the following core pillars:

1. **Ingestion Scope (121 Datasets):** Extraction of 121 enterprise datasets (58 Batch datasets via Fabric Copy Activity over ODBC, and 63 Near Real-Time datasets via Firsthire CDC into ADLS Gen2 connected to Fabric via Lakehouse Shortcuts).

2. **Raw Bronze Staging & Shortcuts:** Establishment of an enterprise OneLake Bronze staging layer (Lakehouse: `th_bronze`) preserving raw JDE table and column names for zero-loss landing and 100% audit traceability.

3. **Hybrid OPDG Connectivity:** Architecture, installation, and performance tuning of the On-Premises Data Gateway (OPDG) in Standard Mode on Windows Server 2022, leveraging IBM i Access Client Solutions (ACS) 64-bit ODBC drivers for secure hybrid connectivity to AS400 DB2.

4. **Metadata Control Repository:** Deployment of the centralized Microsoft Fabric SQL Database (`sqldb-meta-orch`) housing the 4-schema control plane (meta, ctl, log, stage) and automated developer onboarding via `ingestion_metadata_load_template.xlsx`.

5. **Silver Cleansing & Governance:** Implementation of the dynamic PySpark generic transformation engine (`nb_silver_generic_engine`) and configurable Data Quality (DQ) framework executing 10 Silver transformation categories and routing rejected records to dataset-specific Delta quarantine tables.

6. **Gold Star Schema:** Design and automated population of an enterprise Ralph Kimball Star Schema in the Gold Layer (`th_gold`) comprising core Fact tables and Conformed Dimensions.

7. **Direct Lake Semantic Layer:** Configuration of high-performance Power BI Semantic Models in Direct Lake mode over Gold Delta tables, eliminating import refresh bottlenecks while preserving VertiPaq in-memory caching performance.

8. **Event-Driven Flat File Upload:** Event-driven Real-Time Hub and Data Activator ingestion for business-uploaded Excel/CSV files with folder-level least-privilege security.

9. **GitHub Actions CI/CD Automation:** Implementation of enterprise CI/CD deployment pipelines using GitHub Actions, fabric-cicd Python libraries, Fabric REST APIs, and definition-based workspace deployment across Dev, SIT, UAT and Prod.

#### Ingestion Load Patterns

- **Incremental Batch Loads:** Daily scheduled delta copies of dimensions and transaction tables using watermark columns.
- **Near Real-Time (NRT) Loads:** Log-based Change Data Capture (CDC) for critical operational tables to meet a 15-minute data freshness SLA.
- **Downstream Delivery:** Re-building core executive dashboards, sales trackers, and financial reports in Power BI utilizing Direct Lake mode.

---

## 2. Architecture

The IPS BI Modernization architecture follows the Microsoft Fabric Medallion Architecture pattern. All data assets reside within OneLake and are governed centrally, enabling seamless transitions from raw landing to executive analytical consumption.

### 2.1 Architectural Diagram

The diagram below provides an end-to-end view of the approved Microsoft Fabric Medallion Architecture. It shows data from IBM AS400 DB2 and external business files entering the bronze layer through batch, CDC, shortcut and event-driven ingestion paths; progressing through metadata-driven PySpark transformation, validation and quarantine into conformed silver tables; and being modelled in the gold layer as a Ralph Kimball star schema. The curated data is then exposed through Power BI Direct Lake semantic models for governed, high-performance enterprise reporting.

> **MICROSOFT FABRIC APPROVED BASELINE ARCHITECTURE (MEDALLION PATTERN)**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IPS_CORP_GOLD_2022_BRONZE01 (RPROD)                      │
│                                                                             │
│  CRPOTA                           Standard ODBC (ACS)                       │
│  ├── 53 NRT datasets via CDC      Pipelines for AS/400                      │
│  │   └── Standard Cluster                                                   │
│  │       └── Firsthire Hub → ADLS Gen2                                      │
│  │       └── Fabric Lakehouse Shortcuts                                     │
│  │                                                                          │
│  └── 58 Batch datasets            Fabric Data Factory                       │
│      └── Copy Activity            Copy Activity via OPDG                    │
│                                                                             │
│  Bronze (th_bronze) → Silver (th_silver) → Gold (th_gold)                   │
│                                    ↓                                        │
│                          Direct Lake Semantic Model                         │
│                                    ↓                                        │
│                              Power BI Reports                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Source System & Dataset Inventory

The primary enterprise source system is the on-premises JD Edwards EnterpriseOne ERP application hosted on IBM AS400 DB2 (v7.x4). The primary production system is named **IPSRR00**. Source tables are structured in 3rd Normal Form (3NF) relational operational models across two primary schemas: **CRPOTA** (transactional ledgers and master entities) and **CRPCTL** (system controls, User Defined Codes, and configuration tables). In total, the modernization framework encompasses exactly **121 enterprise datasets** divided between Batch and Near-Real-Time ingestion strategies:

| Ingestion Category | Dataset Count | Ingestion Mechanism | Dataset Network & Characteristics |
|-------------------|--------------|--------------------|---------------------------------|
| **Batch Datasets** | 58 Datasets | Fabric Data Factory, Copy Activity over On-Premises Data Gateway (ODBC) | Runs twice daily (08:00/14:00 M-S); execution Master Data Copy Activity triggers OLTP Watermark |
| **NRT Datasets** | 63 Datasets | Firsthire CDC → ADLS Gen2 → Fabric Lakehouse Shortcuts | Continuous CDC extract to ADLS Gen2; PySpark ingestion metrics; Silver refresh every 5 minutes (Zero ODBC overhead on AS400) |
| **Total Framework** | 121 Datasets | Hybrid Fabric FDF & Firsthire | Comprehensive coverage of JDE Financials, Inventory, Pricing, Sales, and Ops |

---

### 2.3 On-Premises Data Gateway (OPDG) Architecture & AS400 DB2 Connectivity

To establish secure, enterprise-grade hybrid connectivity between the Microsoft Fabric SaaS cloud environment and the on-premises IBM AS400 DB2 server without opening inbound firewall ports, the On-Premises Data Gateway (OPDG) is deployed in Standard Mode.

| Gateway Parameter | Configuration Value | Driver / Protocol | High Availability Role |
|-------------------|-------------------|-------------------|----------------------|
| **Gateway Node 1** | genie-fabric-prod-01 | Standard Mode / Azure Relay (Primary) | Active Load Balancing |
| **ODBC Driver** | IBM i Access Client Solutions (ACS) 64-bit | Driver 64-bit, certified AS400 DB2 `cwbdsede.dll` | Client |
| **AS400 Target Host** | IPSRR00 (10.342.2.26:6097) | TCP Port 6017 & 8471 | JDE Production Farm |
| **OS Platform** | Windows Server 2022 | 16 vCPU, 64 GB RAM, 350 GB SSD | Production Enterprise Datacenter Gateway |

#### Hybrid Network Flow

The hybrid network flow operates as follows:

**Security Mandate 1: Outbound Port 443 Communication:** The OPDG client on Windows Server initiates an outbound TLS 1.2/1.3 connection to Azure Service Bus Relay endpoints (`*.servicebus.windows.net`) and Fabric gateway control endpoints (`*.gateway.core.windows.net`). Inbound firewall ports from the internet into the on-premises network are strictly disabled.

**Security Mandate 2: Bilateral IBM i Port Connectivity:** The gateway machine communicates internally to IBM AS400 DB2 via 1422 Central Server, 449 (Host Server Map), 6017/6017 (Database Server Session), 8471/8476 (Signon Server Directory), and the configured FT custom database port 6017.

**Configuration Metadata 3: Driver Configuration:** Configured via 64-bit ODBC Administrator (System DSN `DB2_AS400_PROD`), Connection String:
```
IBM i Access ODBC Driver | System=A10.242.2.26 | Port=6017 |
CRTStandbyDBCS=Y | Naming=1 | LibraryView=0 | CommitMode=0/Autocommit |
Dynamic=Y | Plugins=1 | BlockSizeSec=512 | ABrowLargeDataCompression=1
```

> **NOTE — Ingestion Framework Design Document**
>
> For a detailed description of how the OPDG has been configured please refer to the document available at the shared location: *OPDG Installation & Configuration Guide.docx*.
> This document serves as the comprehensive guide for the OPDG installation and current configuration.

---

### 2.4 Metadata-Driven Ingestion Framework (MDF) Architecture

As part of the project, we are migrating legacy IBM AS400 DB2 data structures into modern Microsoft Fabric Medallion Architecture. Rather than building hundreds of custom static Data Factory pipelines or PySpark notebooks, which are brittle, hard to maintain, and prone to code duplication, the engine framework is driven and centrally described from the metadata control structures. The framework orchestrates, logs, monitors, and governs the end-to-end ingestion and transformation of IBM AS400 (DB2) tables into a modern Microsoft Fabric Medallion Architecture (Bronze → Silver → Gold).

Rather than using rigid, hard-coded, static pipelines for individual dataset loads, the framework uses a metadata repository in a SQL database. Parameterized Data Factory pipelines and PySpark notebooks read this metadata at runtime to dynamically extract, land, cleanse, deduplicate, merge, and transform data.

> **NOTE — Ingestion Framework Design Document**
>
> For a detailed description of the ingestion framework, refer to *Ingestion Framework Design Document V1.1.docx*, available at the shared location.
> This document serves as the comprehensive technical specification and developer operational guide for IPS's Comprehensive Metadata-Driven Ingestion framework.

---

### 2.5 Staging Area (Bronze Layer) & Lakehouse Shortcuts

The Bronze layer serves as the immutable, high-fidelity landing zone within Microsoft Fabric OneLake. Its primary architectural purpose is to land data as received — preserving a zero-loss historical record of all incoming transactions in their native structures.

The Bronze layer is implemented as a Microsoft Fabric Lakehouse named **`th_bronze`**. Source data from batch ingestion is persisted in Apache Delta Lake format, laid by Fabric Copy Activity into Azure Data Lake Gen2 (ADLS) Gen2 parquet format.

#### NRT Extraction Pattern: OneLake Shortcuts

**Architectural Role for NRT Datasets:** For the 63 Near-Real-Time datasets, Firsthire extracts CDC changes — batch-to-batch directly from AS400 and ADLS Gen2. Microsoft Fabric accesses these files seamlessly via OneLake/Lakehouse Shortcuts. Consequently, Fabric incurs NO ODBC overhead (Shortcuts) → Silver Delta (Spark) every 5 minutes. This completely eliminates connection saturation and CPU cycles on the AS400 production core (IPSROD).

#### Bronze Table Naming & Audit Columns

To ensure 100% auditability and simplify reconciliation against the AS400 DB2 raw tables, Bronze tables strictly preserve original JDE table and column names (e.g., `shr_F0902`, `shr_F0911`, `dbr_F0905`, `dbr_F0911`, `dbr_F03B1`, `dbr_F0411`). Cryptic physical names (such as GLCO, GLDGJ, GLDCL, ABA#B) are maintained intact. No loose type conversions or column renaming occurs during Bronze ingestion.

Every Bronze table is automatically enriched with technical audit metadata columns during ingestion:

| Audit Metadata | Column Name | Description |
|---------------|-------------|-------------|
| 1 | `_ingested_dt_pipeline` | Timestamp when the record persisted in Delta Lake |
| 2 | `_ingested_pipeline` | Identifier for the Fabric pipeline which inserted the data |
| 3 | `_freshwr_deleted` | A flag to indicate rows deleted |
| 4 | `_freshwr_synced` | The timestamp of Firsthire sync |
| 5 | `_ingested_at` | SHA-256 hash of all non-audit column values, utilized for fast change detection |
| 6 | `_pipeline_name` | The Fabric pipeline which ingested the data from Firsthire synced ADLS Gen2 layer through shortcuts |
| 7 | `_source_file` | The absolute path of the underlying delta tables for Firsthire sync data |

---

### 2.6 Data Transformation Layer (Silver Conformed Layer & DQ)

The Silver Layer is hosted in Microsoft Fabric Lakehouse **`th_silver`**. Transformations are powered by Fabric Apache Spark 3.5 runtime (PySpark and Delta Lake 2.4). All Silver tables are conformed, 3NF normalized relational entities. The generic transformation engine reads parameters from `meta.dataset_brz_to_silver`, dynamically constructs PySpark transformation DAGs, applies standard cleansers, checks data quality rules, and executes Delta MERGE operations.

#### Silver Generic Engine: 10 Enterprise Transformation Categories

- **Category 1: Column Renaming & Business Alignment:** Mapping cryptic 8-character JDE names to enterprise camelCase/snake_case business names (e.g., `GLCO` → `company_code`, `GLDGJ` → `document_number`, `GLAA` → `transaction_amount_unit`).

- **Category 2: Julian Date Conversion:** AS400 JDE stores dates in 6-digit Julian format (CYYDDD), where C=1 indicates 2000s. Formula:
  ```python
  to_date(concat(cast(1900 + cast(substring(col, 1, 1) as int) as string),
          substring(col, 2, 5)), 'yyyyDDD')
  ```

- **Category 3: Implicit Decimal Scaling:** JDE stores currency amounts as unscaled integers depending on currency definitions (e.g., USD has 2 decimals; ¥23450 represents $1,234.50; JPY has 0 decimals). Scaled dynamically against meta rules.

- **Category 4: User Defined Code (UDC) Decoding:** Joining raw (`CRPCTL.F0005`) against encoded attribute fields to attach readable English descriptions.

- **Category 5: Trimming Whitespace & Padding Removal:** AS400 fixed-width CHAR fields are stripped of trailing and leading whitespace.

- **Category 6: Null Value Normalization:** Source blank spaces, zero dates (000000), and empty strings are converted to standard SQL NULLs or sentinel default values (UNKNOWN).

- **Category 7: Deduplication & Windowed Ranking:** Deduplicating transactions based on composite business keys using `row_number() over (partition by keys order by _ingested_at desc)`.

- **Category 8: Data Type Enforcement:** Casting raw string fields into strict Spark SQL types (`Decimal(19,4)`, `IntegerType`, `TimestampType`, `BooleanType`).

- **Category 9: Business Key & Surrogate Key Preparation:** Computing natural hash keys (SHA-256) for downstream gold dimension look-ups.

- **Category 10: Audit & Lineage Enrichment:** Preserving `_source`, `_file`, `_batch_id`, and appending `_silver_processed_at` timestamps.

#### Quarantine Architecture

A critical and architectural requirement is that quarantine tables MUST be **dataset-specific** rather than a single unified dumping table. This ensures that quarantined records retain the exact schema and data types of the parent entity, allowing data stewards to inspect, correct, and re-inject failed records without complex schema conversion.

- **Mandate 1: Quarantine Table Naming Convention:** Each Silver entity has an associated quarantine table: `silver.{target_table}_quarantine` (e.g., `silver.DIM_Defined_Code_Value_Quarantine`, `silver.General_ledger_quarantine`, `silver.SalesOrderDetail_quarantine`).

- **Mandate 2: Quarantine Schema Structure:** Matches the target table structure exactly, plus three quarantine audit columns: `_dq_rule_id` (INT), `_dq_rule_name` (STRING), `_quarantine_ts` (TIMESTAMP).

- **Mandate 3: Dynamic Rule Enforcement:** Rules fetched from `meta.dataquality_rule`. If severity = 'WARNING' or 'QUARANTINE', invalid rows are redirected to the quarantine table while valid rows continue downstream. If severity = 'STOP', execution halts immediately.

- **Mandate 4: Audit Logging:** Every evaluation writes `rows_evaluated`, `rows_passed`, and `rows_failed` to `log.dq_rule_run`.

---

### 2.7 Dimensional & Analytical Serving Layer

The Gold Layer resides in Microsoft Fabric Lakehouse **`th_gold`**. It is engineered strictly following **Ralph Kimball Dimensional Modelling** principles. Data tables are optimized with Microsoft Fabric V-Order sorting to maximize in-memory compression and sub-second query performance over Power BI Direct Lake mode. The dimensional model implements a pure Star Schema: semantic transaction metrics are centralized in Fact tables, foreign-keyed to conformed Dimensions. **Snowflaking is strictly prohibited** to maximize Direct Lake performance.

#### 2.7.1 Technology and Processing Engine

The end-to-end transformation and loading pipeline is driven by the parameterized PySpark engine `nb_gold_ingestion`.

All Gold Delta tables are optimized with Microsoft Fabric V-Order sorting to maximize in-memory compression, row-group indexing, and sub-second query performance in Power BI Direct Lake mode. Multi-dimensional Z-Ordering is systematically applied to primary surrogate keys and foreign keys, with target Parquet file sizes calibrated to 128 MB to guarantee optimal VertiPaq memory caching without query fallbacks to DirectQuery.

#### 2.7.2 Architectural Thought Process & Design Tenets

The dimensional architectures finalized in the IPS Dim and Fact Specification (IFS) resolve key BI modernization challenges through six core design tenets:

1. **Decoupling ERP Complexity & Standardizing Nomenclature:** Legacy JD Edwards entities (F0911, F03B1, F0411, F0901, F1201), and cryptic 8-character column names (GLAID, GLDGJ, GLDCL, GBAID) are converted into clear, intuitive business terminology. Century-Julian dates (CYYDDD) are systematically converted to standard Gregorian calendar keys, and explicit (SRP) integer decimals are scaled according to currency precision.

2. **Deterministic Hash Surrogate Keys (FNV HASH / xxhash64):** To atomize distributed join bottlenecks and synchronization locks in Apache Spark, surrogate keys (`SB_*`) are generated as deterministic 64-bit integer hashes of standardized natural business keys. Identical natural keys generate identical surrogate keys across pipelines, enabling stateless and concurrent dimensional joins. Surrogate keys are explicitly stored as `SB_` prefixed columns for end-to-end audit lineage and accessibility.

3. **Default Member & Referential Integrity Safeguards:** To ensure zero orphan facts, dedicated lookups implement an enforced default `row_id = -1` ('Unknown / Not Applicable') rather than foreign key errors; ensuring dimension records resolve as -1s (N/A) instead of hard errors during ingestion.

4. **Slowly Changing Dimension (SCD) Lifecycle Governance:** A strict archival pattern is maintained between reference entities and enterprise master dimensions. Reference codes and structural structures (e.g., DIM_Document_Type, DIM_Payment_Term, DIM_Company, DIM_Account, DIM_Currency) are governed by **SCD Type 1** (overwrite-in-place) given their transactional and institutional context, but for personal dimensions (DIM_Customer, DIM_Supplier, DIM_Address) which use **SCD Type 2** with `effective_start_date`, `effective_end_date`, `is_current`, and `event_flag`.

5. **Dual-Currency Valuation & Standardized USD Reporting:** All transactions preserve native transaction/local currency amounts while simultaneously carrying DIM_Currency Exchange metadata for real-time cross-currency analysis (e.g., converting Brazilian BRL to corporate reporting currency Amount USD). This enables corporate multi-entity financial consolidation without custom DAX calculation latency.

6. **Multi-Company Hierarchical Fallback Resilience:** In JDE, Accounts Receivable, customer, and terms may be defined at a specific operating company or globally at Company 00000. The logic applies an automated hierarchical fallback (F03B1.RPCO → F00067) to guarantee accurate customer master association without data loss.

> **NOTE — The star schema catalogue contents is a work in progress**
>
> The dimension and fact catalogues are still a work in progress and will change incrementally as different modules are delivered across the project timeline. The list serves as an indicative list and on final revision of the document will be containing all the gold layer objects.

---

### 2.7.3 Star Schema Dimension Catalogue

The Gold serving tier establishes **16 conformed dimensions** acting as the enterprise query base across all financial, receivable, payable, and asset accounting domains.

| Dimension | Source Table | Key Columns | Grain | SCD Type | Key Attributes & Rationale |
|-----------|-------------|-------------|-------|----------|---------------------------|
| **DIM_Customer** | CRPOTA.F0301, 2_F0101, CRPCTL.F0006 | AKA#B, AKCO | Customer + Company | SCD Type 2 | Customer Name, Collector Code, Credit Limit, Credit Rating, Payment Terms, Risk Code, Tax ID. Supports AR aging and credit risk analytics. |
| **DIM_Company** | CRPOTA.F0010 | CCCO | Company Code | SCD Type 1 | Company Name, Fiscal Pattern, Multi-Currency Flag, Reporting Currency, Begin Date. Corporate roll-up entity. |
| **DIM_Calendar** | Enterprise Fiscal & F0008 | Calendar_Date | Calendar Day | SCD Type 1 | GL_Dim_Julian_Calendar (CYYDDD), Calendar Date, Fiscal Quarter, Fiscal Year, Period Begin/End dates. Universal time axis. |
| **DIM_Account** | CRPOTA.F0901 | GMAID | Account ID | SCD Type 1 | Object Account, Subsidiary, Account Description, Level of Detail (LOD), Account Non-Posting Code, Chart of Accounts, SubAccount. |
| **DIM_Business_Unit** | CRPOTA.F0006, 5_F0093, F0005 | MCMCU | Business Unit | SCD Type 1 | Business Unit Code, Description, Company Code, Division, Category. |
| **DIM_Supplier** | CRPOTA.F0401 | AKA#B | Supplier Code | SCD Type 1 | Supplier Name, Search Type, Payment Term, Withholding Tax, Address Line ID. Supports AP liability reporting. |
| **DIM_Address** | CRPOTA.F0101, F0116 | ABA#B | Address Book | SCD Type 2 | Legal Name, Postal Code, City, State, Country, Search Type. Geographic entity for tax and logistics. |
| **DIM_Contact** | CRPOTA.F0111, (DIM).F01161 | WWAN#B, WWDLN | Address + Line | SCD Type 2 | Primary Email, Telephone, Contact — is Primary, Contact Rep (WWDLIN). Direction communication. |
| **DIM_Document_Type** | CRPCTL.F0005, 5_(DOC.06.DT) | DRSY, DRRT (SY#Y) | System + Type | SCD Type 1 | Document Type Code (e.g., RI, PV, JE), Description. Financial journal types, sub-ledger. Codes, Departmental and cost centre rollup. |
| **DIM_Payment_Term** | CRPCTL.F0014 | PNTC | Payment + Terms | SCD Type 1 | Description, Net Days to Pay, Discount Percent, Discount Days. Working capital management. |
| **DIM_Currency** | CRPCTL.F0013 | CRCD | Currency Code | SCD Type 1 | ISO Currency Code, Currency Name, Decimal Positions. |
| **DIM_Currency_Exchange_Rate** | CRPCL1.F0015 | CRCHCD, CRCRDC, CRCRT1, CXEFT | From + To + Type + Date | SCD Type 1 | Conversion Rate, Divisor Rate, Spot vs. Budget Rate, Effective Range. Rates table for currency standardization. |
| **DIM_Account_Balance** | CRPOTA.F0902 | GBAID1, GBFY (GELT, GBBB, GBCRCD, GBCO) | Account + Ledger + Year + SubLedger | SCD Type 1 | SubLedger, SubLedger Type, Fiscal Year, Currency Code. Supports multi-ledger balance comparisons (AA vs. CA). |
| **DIM_Asset** | CRPOTA.F1201 | FA#UMB | Asset Item Number | SCD Type 2 | Major Accounting Class, Asset Description, Depreciation Method, Serial Number, Cost Account. Fixed asset register. |
| **DIM_Asset_Account_Balance** | CRPOTA.F1202 | Account_ID1, FA#UMB1, CarNum1 | Asset + Item + CarNum | SCD Type 1 | Historical cost, accumulated depreciation, capitalization methods (ITD / Remaining). Asset balance tracking. Governs decimal scaling. |

---

## 1. Executive Summary & Project Overview

### 1.1 Purpose of the Document

This document presents the design for the IPS BI Modernization initiative, defining the target architecture, implementation approach, integration patterns, and operational considerations required to modernize the business intelligence platform. It establishes a shared baseline for stakeholders and delivery teams, supporting consistent design decisions throughout implementation.

This document defines the comprehensive technical architecture, ingestion patterns, transformation engine, data quality framework, Ralph Kimball star schema dimensional model, Power BI Direct Lake semantic layer, security boundaries, and DevOps automation for the IPS Business Intelligence (BI) Modernization project. It incorporates the approved Ingestion Framework design, the On-Premises Data Gateway (OPDG) Installation & Configuration Guide, and the Microsoft Fabric CI/CD GitHub Actions Implementation specification.

Historically, IPS enterprise reporting suffered from severe operational bottlenecks: heavy transactional locks on DB2 production databases, brittle point-to-point ETL pipelines and multi-hour latency for critical financial reconciliation. The modernization project decouples the operational AS400 transactional core, establishes an automated Medallion Architecture (Bronze Raw Landing → Silver Standardized 3NF → Gold Kimball Star Schema), and delivers sub-second analytical reporting via Power BI Direct Lake mode.

---

### 1.2 Business Objectives & Drivers

IPS Corporation is executing a modern BI platform transition to eliminate fragmented, on-premises legacy data systems and consolidate analytics onto Microsoft Fabric, a unified Software-as-a-Service (SaaS) data platform.

- **Elimination of Data Silos:** Moving from isolated databases and flat-file storage to a single, unified data lake (OneLake).

- **Reduction of Technical Debt:** Decommissioning complex on-premises legacy ETL/SSIS workflows and custom mainframe scripts that require manual intervention.

- **Transition to SaaS Ecosystem:** Replacing traditional infrastructure management (machines, database clusters) with a serverless, managed SaaS model to lower operational overhead.

- **Modernization of the Mainframe Interface:** Moving away from direct, high-overhead querying of the production mainframe to protect transaction processing capability to more agile CDC-based query on mainframe infrastructure.

---

### 1.3 Scope of Modernization

**In-Scope Data Sources:** The primary data source is a third-party vendor-hosted IBM AS400 database running DB2 on i/4 OS on POWER hardware.

**Ingestion Scope:** Ingestion of approximately 121 datasets from DB2 and some Excel/CSV files into Microsoft Fabric OneLake.

**Data Migration Strategy:**

- **Historical Load:** Bulk migration of data dating back to January 2020 (± 5.5 years of history) partitioned using sequential time slices.
- **Incremental Batch Loads:** Daily scheduled delta copies of dimensions and transaction tables using watermark columns.
- **Near Real-Time (NRT) Loads:** Log-based Change Data Capture (CDC) for critical operational tables to meet a 15-minute data freshness SLA.
- **Downstream Delivery:** Re-building core executive dashboards, sales trackers, and financial reports in Power BI utilizing Direct Lake mode.

---

> **End of Document**
