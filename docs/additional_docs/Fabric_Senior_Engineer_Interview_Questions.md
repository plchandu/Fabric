# Senior & Lead Microsoft Fabric Engineer — Technical Interview Guide & Question Bank

> **Role Level:** Senior Data Engineer / Lead Fabric Engineer / Fabric Solutions Architect  
> **Domain Focus:** Enterprise Microsoft Fabric Architecture, OneLake Medallion Engineering, Direct Lake Optimization, Hybrid Ingestion, FinOps Capacity Governance, Entra/Okta Security, and Git-Driven CI/CD.  
> **Reference Context:** Enterprise ERP (IBM AS400 / JDE EnterpriseOne) Modernization to Microsoft Fabric.

---

## Table of Contents
1. [Architecture & OneLake Medallion Design](#1-architecture--onelake-medallion-design)
2. [Hybrid Ingestion, Mainframe/AS400 & Networking](#2-hybrid-ingestion-mainframeas400--networking)
3. [PySpark, Delta Lake & Storage Layer Optimization](#3-pyspark-delta-lake--storage-layer-optimization)
4. [Dimensional Modeling & Ralph Kimball Star Schema](#4-dimensional-modeling--ralph-kimball-star-schema)
5. [Direct Lake Semantic Modeling & Fallback Prevention](#5-direct-lake-semantic-modeling--fallback-prevention)
6. [Enterprise Security, Identity (Okta/Entra) & Governance](#6-enterprise-security-identity-oktaentra--governance)
7. [FinOps, Capacity Unit Sizing & Lifecycle Scheduling](#7-finops-capacity-unit-sizing--lifecycle-scheduling)
8. [DevOps, CI/CD & Fabric Git Integration](#8-devops-cicd--fabric-git-integration)
9. [Real-Time Analytics & Event-Driven Ingestion](#9-real-time-analytics--event-driven-ingestion)
10. [High-Impact Architectural Scenario & Troubleshooting Questions](#10-high-impact-architectural-scenario--troubleshooting-questions)

---

## 1. Architecture & OneLake Medallion Design

### Q1.1: When designing the Gold Layer in Microsoft Fabric, how do you decide between a Fabric Lakehouse (with SQL Analytics Endpoint) and a Fabric Data Warehouse?
* **What Interviewers Look For:** Understanding of read/write compute engines, write throughput, Direct Lake behavior, and governance boundaries.
* **Model Answer:**
  * **Engine & Write Path:** If upstream transformations are performed using PySpark notebooks, a **Fabric Lakehouse** is preferred. Spark writes directly to OneLake Delta Parquet files in native storage without network hops or intermediate SQL translation layers. Writing into a Fabric Warehouse from Spark requires a JDBC connector, introducing an extra network hop and routing data through the SQL transactional boundary.
  * **V-Order Optimization:** In a Lakehouse, Spark sessions can write files directly with Microsoft's proprietary **V-Order** sorting and distribution enabled (`spark.sql.parquet.vorder.enabled=true`), which optimizes the Parquet layout for in-memory VertiPaq execution.
  * **Data Protection & Guardrails:** A Lakehouse SQL Analytics Endpoint is strictly **read-only**. For Gold reporting layers, this prevents ad-hoc T-SQL modifications (`UPDATE`, `DELETE`, `DROP`) by business users or third-party query tools, guaranteeing that all table changes flow exclusively through automated pipelines.
  * **When to choose Data Warehouse:** When the primary transformation skill set is T-SQL (Stored Procedures, `MERGE`, `CTAS`), when cross-database ACID transactional multi-table DML is mandatory, or when downstream applications require direct ODBC/JDBC write capabilities.

---

### Q1.2: Explain the technical implementation of OneLake Shortcuts and how they differ from traditional ETL data replication.
* **What Interviewers Look For:** Zero-copy architecture, performance implications, cross-cloud/cross-workspace data virtualization, and cost benefits.
* **Model Answer:**
  * **Concept:** Shortcuts are embedded symbolic links in OneLake that point to internal storage locations (other Lakehouses/Warehouses) or external cloud storage (Azure Data Lake Storage Gen2, AWS S3, Google Cloud Storage) without copying or moving the underlying physical data.
  * **Eliminating Data Duplication & Latency:** In our ERP modernization, 63 Near-Real-Time (NRT) datasets replicated from IBM AS400 DB2 via CDC into ADLS Gen2 were linked into the Bronze Lakehouse (`lh_bronze`) via OneLake Shortcuts. This eliminated secondary ETL copy pipelines and eliminated disk storage duplication ($0.023/GB/mo savings).
  * **Zero Mainframe Contention:** Reading via shortcuts decoupled Fabric Spark read engines from the production mainframe OLTP core (`IPSRR00`), eliminating ODBC connection saturation and CPU locks on the source database.
  * **Governance:** Shortcuts inherit security and lineage within Fabric, allowing Microsoft Purview to trace lineage back to the underlying target while presenting a unified lake experience to downstream notebooks.

---

### Q1.3: What audit metadata should be stamped at the Bronze ingestion layer, and why is this critical for enterprise reconciliation?
* **What Interviewers Look For:** Data lineage, auditability, backfill capability, and idempotent data pipelines.
* **Model Answer:**
  * Bronze must act as an immutable, high-fidelity replica preserving original cryptic source column names (e.g., JDE's `GLCO`, `GLDGJ`, `GLAA`) without schema manipulation.
  * Every Bronze Delta table must be systematically enriched with technical audit metadata:
    1. `_ingested_dt_pipeline`: UTC timestamp when the record was persisted in Delta Lake.
    2. `_ingested_pipeline`: The unique ID of the Fabric Data Factory pipeline executing the load.
    3. `_freshwr_synced`: Upstream CDC synchronization timestamp.
    4. `_freshwr_deleted`: Soft-delete tombstone flag for upstream CDC deletion reconciliation.
    5. `_source_file`: Absolute URI of the underlying Parquet/CSV file.
    6. `_ingested_at`: A deterministic SHA-256 hash of all non-audit business columns.
  * **Why it matters:** The SHA-256 hash enables sub-second change detection during Silver conformed merges without scanning every individual attribute. The timestamps and pipeline IDs enable deterministic partition replays and audit reconciliation when investigating discrepancies with finance stakeholders.

---

## 2. Hybrid Ingestion, Mainframe/AS400 & Networking

### Q2.1: How do you architect secure, high-throughput hybrid connectivity between Microsoft Fabric (SaaS) and on-premises legacy systems (e.g., IBM AS400 DB2) without exposing inbound firewall ports?
* **What Interviewers Look For:** Network topologies, On-Premises Data Gateway (OPDG) architecture, outbound port requirements, and driver configurations.
* **Model Answer:**
  * **Network Topology:** Deploy an **On-Premises Data Gateway (OPDG)** cluster in **Standard Mode** on dedicated Windows Server 2022 instances (e.g., 16 vCPU, 64 GB RAM) located in the on-premises datacenter network.
  * **Outbound-Only Communication:** The OPDG initiates outbound-only TLS 1.2/1.3 encrypted connections on **Port 443** to Azure Service Bus Relay endpoints (`*.servicebus.windows.net`) and Fabric gateway control endpoints (`*.gateway.core.windows.net`). Inbound firewall ports from the internet into the corporate network are strictly disabled (`Deny All Inbound`).
  * **Local Host Communication:** The gateway communicates internally to the IBM AS400 DB2 host over internal ports: Port 449 (Host Server Map), Port 8471 (Signon Server), and custom database server session ports (e.g., Port 6017).
  * **Driver Stack:** Configure the 64-bit **IBM i Access Client Solutions (ACS)** ODBC driver (`cwbdsede.dll`). Optimize connection string properties with `CommitMode=0` (Autocommit), `BlockSizeSec=512`, `Dynamic=Y`, and `ABrowLargeDataCompression=1` to maximize throughput during large bulk extractions.

---

### Q2.2: How would you design a Metadata-Driven Ingestion Framework (MDF) in Microsoft Fabric, and what problems does it solve compared to static pipelines?
* **What Interviewers Look For:** Reusability, parameterization, metadata architecture, operational maintainability, and scalability.
* **Model Answer:**
  * **The Problem:** In an enterprise migrating 100+ tables (e.g., 121 JDE datasets), building static Data Factory pipelines creates hundreds of brittle, unmaintainable artifacts with hardcoded paths, duplicated code, and high maintenance overhead.
  * **MDF Architecture:**
    1. **Metadata Store:** A centralized SQL database (`sqldb-meta-orch-dev`) storing metadata tables: dataset inventories, source system connection strings, extract queries, watermarks, target Lakehouse locations, schedule groups, and execution states.
    2. **Master Orchestrator Pipeline:** Iterates through active dataset metadata groups (e.g., 6 ingestion tiers: GL Financials, Open Receivables, Payables, Inventory, Master Data).
    3. **Parameterized Worker Pipelines:** Fabric Data Factory pipeline with dynamic parameters (`source_query`, `target_lakehouse`, `watermark_column`, `destination_table`). Executes Copy Activities dynamically over the OPDG or invokes generic PySpark notebooks.
    4. **Dynamic Watermark & State Logging:** Pipeline captures execution telemetry (`RowsRead`, `RowsWritten`, `Duration`, `Status`) and logs execution metrics back to the SQL metadata store, updating watermarks only upon successful completion.

---

## 3. PySpark, Delta Lake & Storage Layer Optimization

### Q3.1: What is the "Small File Problem" in Microsoft Fabric OneLake, and what technical runbooks do you enforce to mitigate it?
* **What Interviewers Look For:** Delta Lake internal mechanics, micro-batch fragmentation, VertiPaq Direct Lake implications, and maintenance commands (`OPTIMIZE`, `VACUUM`).
* **Model Answer:**
  * **Root Cause:** Micro-batch CDC syncs and frequent incremental pipeline runs commit multiple tiny Parquet files (< 1MB) and corresponding JSON commits in the `_delta_log/` directory.
  * **Consequences:** Excessive file system metadata calls degrade Spark read throughput, bloat OneLake storage costs, and directly impair Power BI Direct Lake performance, triggering query timeouts or expensive fallbacks to DirectQuery.
  * **Mitigation Protocol:**
    1. **Automated Compaction (`OPTIMIZE`):** Enforce scheduled weekly Spark table maintenance notebooks to bin-pack small files into 128 MB to 512 MB target files. For Gold tables, target 512 MB to align with VertiPaq segment sizing:
       ```python
       spark.sql("OPTIMIZE lh_gold.Fact_Sales ZORDER BY (TransactionDateKey)")
       ```
    2. **Write-Time Compaction:** Enable `spark.sql.parquet.vorder.enabled = true` and `.option("optimizeWrite", "true")` during batch PySpark writes.
    3. **Dead-File Vacuuming (`VACUUM`):** Run `VACUUM RETAIN 168 HOURS` (7 days) on all Bronze, Silver, and Gold tables. This permanently purges orphaned Parquet files whose log retention has expired while strictly preserving a 7-day Delta Time Travel recovery window for reporting queries and rollback.

---

### Q3.2: Explain Microsoft Fabric's V-Order technology and how it optimizes analytical queries.
* **What Interviewers Look For:** Parquet physical layout, sorting, compression, dictionary encoding, and VertiPaq compatibility.
* **Model Answer:**
  * **Definition:** **V-Order** is a proprietary write-time optimization developed by Microsoft for Delta Parquet files in OneLake.
  * **Mechanism:** Traditional Parquet writes rows into row groups and columnar chunks in standard physical sequence. V-Order applies advanced sorting, distribution, and dictionary encoding algorithms to the columnar data chunks before writing to disk.
  * **Direct Lake Acceleration:** The physical layout of a V-Ordered Delta Parquet file is directly isomorphic to the in-memory columnar format used by the **Power BI VertiPaq engine**. When a Direct Lake query executes, VertiPaq memory-maps the V-Ordered Parquet columns straight into RAM without transcoding, decompression overhead, or data movement, delivering sub-second visual rendering on multi-million-row tables.

---

### Q3.3: How do you handle complex legacy date and decimal data formats in PySpark when ingesting from mainframe ERPs like JD Edwards?
* **What Interviewers Look For:** PySpark DataFrame transformations, performance, User Defined Functions (UDF) antipatterns vs. native Spark SQL expressions.
* **Model Answer:**
  * **Julian Date Conversion (CYYDDD):** Mainframe JDE stores dates in 6-digit Julian format where century $C=1$ represents post-2000 (e.g., $124045$ represents February 14, 2024).
    * *Antipattern:* Using Python UDFs, which forces row-by-row Python-to-JVM serialization.
    * *Native PySpark Solution:* Use native vectorized Spark SQL functions:
      ```python
      from pyspark.sql import functions as F

      def convert_jde_julian(col_name):
          # Extract Year: 1900 + (CYYDDD // 1000)
          # Extract Day of Year: CYYDDD % 1000
          year = F.floor(F.col(col_name) / 1000) + 1900
          day_of_year = F.col(col_name) % 1000
          return F.to_date(F.concat_ws("-", year.cast("string"), day_of_year.cast("string")), "yyyy-D")
      ```
  * **Implied Decimal Shifting:** JDE stores financial amounts as integers without decimal points (e.g., $100000$ represents $\$1,000.00$).
    * *Solution:* Join against system control tables (e.g., `CRPCTL.F0010` currency decimals) in the Silver conformed transformation layer and dynamically divide by $10^{\text{CURR\_DEC}}$ using PySpark arithmetic, casting to `DecimalType(18, 4)`.

---

## 4. Dimensional Modeling & Ralph Kimball Star Schema

### Q4.1: Why is a strict Star Schema mandatory for Power BI Direct Lake models, and why should Snowflake designs be avoided?
* **What Interviewers Look For:** Dimensional modeling best practices, join depth, VertiPaq memory traversal, relationship cardinality, and DAX query generation.
* **Model Answer:**
  * **Minimizing Join Depth:** Power BI's VertiPaq engine evaluates DAX filter context across relationships at run time. In a Star Schema, every dimension table joins directly to the central Fact table with a single hop (1-to-many relationship).
  * **The Snowflake Antipattern:** Normalizing dimensions into sub-dimensions (e.g., `Dim_Product` $\rightarrow$ `Dim_Subcategory` $\rightarrow$ `Dim_Category`) forces the engine to traverse multiple table joins in memory. Under Direct Lake, excessive relationship chains increase memory footprint and can trigger engine query timeouts that force the query to fall back to DirectQuery.
  * **Integer Surrogate Keys:** Natural keys (e.g., alphanumeric customer IDs or composite branch/plant keys) should be mapped to integer surrogate keys (`CustomerKey INT`, `DateKey INT`). Integer keys minimize the cardinality and byte width of relationship columns, resulting in higher compression ratios and faster bit-vector scans in RAM.

---

### Q4.2: How do you design an Enterprise Kimball Bus Matrix across multiple business domains in Microsoft Fabric?
* **What Interviewers Look For:** Architectural vision, conformed dimensions, cross-functional analytics, and consistency across business units.
* **Model Answer:**
  * **Definition:** An Enterprise Kimball Bus Matrix maps business processes (rows) against conformed enterprise dimensions (columns).
  * **Conformed Dimensions:** Build reusable dimensions that share consistent keys, attribute names, and domain definitions across the company (e.g., `Dim_Date`, `Dim_Customer`, `Dim_BranchPlant`, `Dim_GL_Account`).
  * **Business Process Fact Tables:**
    * *General Ledger:* `Fact_GL_Transactions` (periodic and transaction snapshot).
    * *Accounts Receivable:* `Fact_AR_Open` and `Fact_AR_Aging`.
    * *Accounts Payable:* `Fact_AP_Open` and `Fact_AP_History`.
    * *Inventory:* `Fact_Inventory_Balance` (periodic snapshot).
  * **Cross-Process Reporting:** By conforming `Dim_BranchPlant` and `Dim_Customer` across both Sales Orders and Accounts Receivable, executive stakeholders can drill across sales volume and cash collection latency in a single semantic model without data silos or circular relationship paths.

---

## 5. Direct Lake Semantic Modeling & Fallback Prevention

### Q5.1: What is "DirectQuery Fallback" in Power BI Direct Lake mode, what causes it, and how do you prevent it?
* **What Interviewers Look For:** Deep knowledge of Direct Lake architecture, VertiPaq memory boundaries, DAX limitations, and testing methodologies.
* **Model Answer:**
  * **Mechanism:** Direct Lake mode loads Delta Parquet columns directly into the Fabric capacity's VertiPaq RAM. If a query requests data that cannot be served in-memory, the engine silently converts the DAX visual query into a T-SQL query executed against the Lakehouse SQL Analytics Endpoint (**Fallback to DirectQuery**), increasing query latency from sub-800ms to tens of seconds.
  * **Primary Causes & Architectural Mitigations:**
    1. **Capacity RAM Exhaustion:** Semantic models exceed capacity memory limits (e.g., 25 GB limit on F64, 10 GB limit on F32).
       * *Mitigation:* Exclude unused high-cardinality columns, trim string lengths, and convert large decimals to standard precision.
    2. **DAX Calculated Columns & Tables:** Direct Lake does **not** support DAX calculated columns or calculated tables. Adding a DAX calculated column forces that table into DirectQuery mode.
       * *Mitigation:* Push all calculations upstream into PySpark Silver/Gold transformations.
    3. **SQL Endpoint Security Views:** Implementing RLS on the Lakehouse SQL Endpoint causes forced fallback.
       * *Mitigation:* Implement RLS strictly inside the Custom Semantic Model using DAX filters.
    4. **Complex DAX Queries:** Unsupported DAX functions or bi-directional cross-filtering.
  * **Testing Safeguard:** In non-production validation workspaces (SIT/UAT), set the semantic model's **Direct Lake Behavior** property from `Automatic` to **`Direct Lake Only`**. This forces queries that would otherwise fall back to fail immediately, alerting the engineering team to resolve the bottleneck before production release.

---

### Q5.2: Why should enterprise data platforms avoid using the auto-generated "Default Semantic Model" in Microsoft Fabric?
* **What Interviewers Look For:** Governance, schema stability, object-level security, separation of concerns, and enterprise deployment best practices.
* **Model Answer:**
  * **Schema Bloat:** The Default Semantic Model automatically includes **every** table and column created in the Lakehouse (including Bronze staging, Silver conformed, and quarantine tables). Business report authors are exposed to uncurated raw data.
  * **Schema Drift Vulnerability:** If a developer alters an upstream table schema or drops a staging column, the Default Model automatically syncs, instantly breaking existing downstream reports in production.
  * **Lack of Object-Level Security (OLS):** You cannot hide specific columns or tables from business users in the Default Model.
  * **Enterprise Standard:** Architects must mandate **Custom Semantic Models**. Developers curate the model by selecting only certified `Dim_` and `Fact_` tables, defining clean 1-to-many relationships, creating standardized DAX measures, and deploying the model to a separate Tier-2 reporting workspace.

---

### Q5.3: After an upstream PySpark batch pipeline completes its write to the Gold Lakehouse, how do you ensure the Direct Lake semantic model reflects the new data immediately?
* **What Interviewers Look For:** Semantic model synchronization, REST API integration, cache invalidation, and sub-second metadata refreshes.
* **Model Answer:**
  * **The Challenge:** While Direct Lake reads files directly from OneLake, the semantic model caches Delta transaction log checkpoints. To discover new Parquet files written by Spark, the model must perform a metadata sync.
  * **Implementation:** At the conclusion of the Fabric ETL pipeline (immediately after the Gold notebook activity), add a **Web Activity** calling the Power BI REST API endpoint:
    * **Endpoint:** `POST https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes`
    * **Payload:**
      ```json
      {
        "type": "clearCacheAndRehydrate"
      }
      ```
  * **Performance:** Because this operation only refreshes metadata file pointers rather than loading raw data across the network, the API execution completes in **under 1 second**, ensuring executive reports instantly reflect the latest data without capacity spikes.

---

## 6. Enterprise Security, Identity (Okta/Entra) & Governance

### Q6.1: How do you implement an end-to-end security architecture that synchronizes Okta identity management with Microsoft Entra ID and enforces least-privilege governance across Fabric workspaces?
* **What Interviewers Look For:** Identity federation, SCIM group push, Entra ID RBAC, tier-based workspace isolation, and data layer shielding.
* **Model Answer:**
  * **Identity Synchronization (Okta $\rightarrow$ Entra ID):** Configure Okta as the authoritative identity provider. Use **Okta SCIM / Push Groups** to sync 5 standardized role groups into Microsoft Entra ID:
    1. `SG-PBI-FabricAdmins`: Tenant settings and capacity administration (Central IT BI Admins).
    2. `SG-PBI-WorkspaceAdmins`: Workspace lifecycle and deployment pipelines (BI Operations).
    3. `SG-PBI-Developers`: Pipeline development and model authoring (Contributors).
    4. `SG-PBI-ReportConsumers`: Report consumers (App Viewers only).
    5. `SG-PBI-GatewayAdmins`: OPDG gateway configuration (DBA / Infra team).
  * **Two-Tier Workspace Isolation:**
    * **Tier 1 (`bim_data_prod`):** Houses Bronze, Silver, and Gold Lakehouses and pipelines. Only Data Engineers have access.
    * **Tier 2 (`bim_report_prod`):** Houses Custom Semantic Models and Power BI thin reports.
    * **Data Shielding:** Report authors and business users have **zero workspace access** to Tier 1. Instead, the Tier-2 semantic model accesses the Gold Lakehouse via **OneLake Sharing (Read & Build permissions on Gold only)**. Bronze and Silver layers remain completely invisible.

---

### Q6.2: How do you configure Row-Level Security (RLS) in Direct Lake mode without causing DirectQuery fallback?
* **What Interviewers Look For:** DAX-based RLS, dynamic user security, VertiPaq evaluation, and avoiding SQL-level security pitfalls.
* **Model Answer:**
  * **The Rule:** Do **not** create SQL views with security filters or define RLS on the Lakehouse SQL Analytics Endpoint. The VertiPaq Direct Lake engine cannot parse SQL views natively and will force all visual queries into slow DirectQuery mode.
  * **Direct Lake DAX Solution:** Define RLS exclusively within the **Custom Semantic Model** using dynamic DAX filter expressions:
    ```dax
    [Territory_Code] = LOOKUPVALUE(
        UserSecurityMapping[Territory_Code],
        UserSecurityMapping[User_Email],
        USERPRINCIPALNAME()
    )
    ```
  * **Execution:** When an authenticated user opens a Power BI report, VertiPaq evaluates `USERPRINCIPALNAME()` directly in memory, applying the bitmask filter against the compressed in-memory columns while preserving the sub-second Direct Lake query path.

---

### Q6.3: How do you enable secure self-service file uploads to OneLake for business users without granting broad workspace access?
* **What Interviewers Look For:** OneLake Data Access Roles, folder-level ACLs, and least-privilege security design.
* **Model Answer:**
  * **Design Challenge:** Assigning users a Fabric workspace role (*Contributor*, *Member*) grants broad access to all lakehouses, tables, and code artifacts.
  * **Folder-Level Access Implementation:**
    1. Create an Entra ID Security Group: `SG-Fabric-LH-Bronze-Uploader`.
    2. In the `lh_bronze` Lakehouse, configure **OneLake Data Access Roles** (or ADLS Gen2 POSIX ACLs):
       * Define role: `FlatFileRepo_Contributor`.
       * Assign `Read` and `Write` permissions strictly to the subpath: `Files/FlatFile_Repo/`.
       * Leave all other paths (`Files/other_folders/`, `Tables/`) unassigned (implicitly denied).
    3. Grant `SG-Fabric-LH-Bronze-Uploader` only **Viewer** access at the workspace level (or direct Lakehouse Item Sharing with Read-only).
  * **Result:** Business users can log into `app.fabric.microsoft.com`, navigate to `lh_bronze/Files/FlatFile_Repo`, and upload files directly without seeing or modifying any data engineering pipelines or database tables.

---

## 7. FinOps, Capacity Unit Sizing & Lifecycle Scheduling

### Q7.1: What is the "Fabric Reservation Downscale Trap", and how do you design a procurement strategy to prevent it?
* **What Interviewers Look For:** Financial governance, FinOps principles, Azure Reservation terms, capacity lifecycle awareness, and executive cost stewardship.
* **Model Answer:**
  * **The Trap:** An Azure 1-Year Capacity Reservation offers a ~40.5% discount but is a legally binding contract for a fixed Capacity Unit count. Under Microsoft Azure's reservation policies, you cannot exchange a reservation for a lower total monetary value. If an engineering team purchases a 1-year reservation for an **F128 capacity** ($10,005/mo) to absorb heavy data backfills during a 6-month implementation phase, scaling the capacity down to **F32** ($2,501/mo) in the Azure Portal at go-live **will not reduce the Azure bill**. Azure continues billing for the full 128 CUs for the remainder of the 12 months.
  * **Optimal Solution (Hybrid FinOps Model):**
    1. **Production (F64):** Purchase a 1-Year Capacity Reservation ($5,018/mo) for PROD since production runs continuously 24/7/365.
    2. **Non-Production (F128):** Keep DEV/SIT/UAT on **Pay-As-You-Go (PAYG)** compute.
    3. **Automated Lifecycle Scheduling:** Use Azure Logic Apps to automatically pause the Non-Prod F128 capacity outside business hours (~260 hours/month instead of 730 hours).
  * **Impact:** Delivers the necessary 192 CU throughput during implementation while saving over **$170,000 annually** and enabling a risk-free downscale to F32 at steady state.

---

### Q7.2: How does Microsoft Fabric compute smoothing and throttling work, and how do you monitor capacity burn?
* **What Interviewers Look For:** Capacity Unit mechanics, interactive vs. background smoothing windows, throttling phases, and the Fabric Capacity Metrics App.
* **Model Answer:**
  * **Smoothing Algorithm:** Microsoft Fabric aggregates burst compute consumption across capacity units:
    * **Interactive Operations** (Direct Lake queries, report rendering, interactive notebooks): Smoothed over a **5-minute sliding window**.
    * **Background Operations** (Scheduled Data Factory batch pipelines, PySpark Silver/Gold runs): Smoothed over a **24-hour sliding window**.
  * **Throttling Mitigation:** When capacity utilization consistently exceeds 100% of provisioned CUs, Fabric enters progressive throttling:
    1. *Interactive Delay:* Small visual delays introduced.
    2. *Interactive Rejection:* Direct Lake queries are rejected if exhaustion continues.
    3. *Background Rejection:* Batch pipeline executions fail.
  * **Monitoring & Alerting:** Deploy the **Fabric Capacity Metrics App**. Set up automated Azure Monitor alerts triggering when CU utilization exceeds 80% for two consecutive 15-minute intervals. Schedule heavy batch backfills during off-peak hours to spread consumption evenly across the 24-hour smoothing window.

---

### Q7.3: How do you automate the pausing and resuming of Microsoft Fabric capacities using Azure ARM REST APIs?
* **What Interviewers Look For:** Cloud automation, Infrastructure as Code, Logic Apps, and cost optimization execution.
* **Model Answer:**
  * **Architecture:** Fabric capacities are native Azure Resource Manager (ARM) resources under namespace `Microsoft.Fabric/capacities`. When suspended, compute billing stops instantly ($0/hr), and only active OneLake storage ($0.023/GB/mo) is billed.
  * **Logic App Workflow:**
    * Create a scheduled Azure Logic App with a System-Assigned Managed Identity granted *Contributor* permissions on the capacity's Azure Resource Group.
    * **Schedule:** Trigger `resume` at Mon–Fri 07:00 AM UTC and `suspend` at Mon–Fri 19:00 PM UTC.
    * **REST Endpoints:**
      ```
      POST https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/
      providers/Microsoft.Fabric/capacities/{capacityName}/suspend?api-version=2022-07-01-preview
      ```
  * **Developer Ad-Hoc Override:** Create a webhook-triggered Logic App allowing developers to resume compute on weekends or off-hours. Implement an automated **4-hour lease timeout** that automatically re-suspends the capacity after 4 hours if not renewed, preventing accidental weekend billing.

---

## 8. DevOps, CI/CD & Fabric Git Integration

### Q8.1: Why does an enterprise DevOps strategy enforce PySpark code serialization as `.py` files instead of Jupyter Notebook `.ipynb` files in Fabric Git repositories?
* **What Interviewers Look For:** Git diff readability, code review hygiene, merge conflict resolution, and CI/CD automation.
* **Model Answer:**
  * **The `.ipynb` Antipattern:** Jupyter Notebook files store code cells inside large JSON objects alongside execution count metadata, cell IDs, and embedded outputs. When two developers work on the same notebook, merging branches generates complex, unreadable JSON merge conflicts that can easily corrupt the notebook.
  * **The `.py` Solution:** Microsoft Fabric Git Integration supports serializing notebooks as clean Python files (`notebook-content.py`).
  * **Benefits:**
    1. Pull Requests show pure, line-by-line code diffs that make code reviews transparent and fast.
    2. Standard linting and security scanning tools (e.g., Flake8, Black, Bandit, SonarQube) can evaluate the code natively in GitHub Actions.
    3. Merge conflicts can be resolved using standard Git merge tools without JSON syntax errors.

---

### Q8.2: Explain Tabular Model Definition Language (TMDL) and its significance in enterprise Fabric CI/CD workflows.
* **What Interviewers Look For:** Power BI developer tools, Git serialization, concurrent modeling, and merge conflicts.
* **Model Answer:**
  * **Legacy TMSL Antipattern:** Historically, Power BI semantic models were serialized as a single, monolithic JSON document (`model.bim`) spanning tens of thousands of lines. Multiple developers attempting to add measures or modify relationships concurrently frequently encountered irreconcilable merge conflicts.
  * **TMDL Architecture:** TMDL breaks the semantic model into human-readable, folder-based text files:
    * `database.tmdl`: Database-level properties.
    * `tables/`: Individual `.tmdl` files for each dimension and fact table.
    * `relationships.tmdl`: Model relationship definitions.
    * `roles/`: Row-Level Security definitions.
  * **CI/CD Value:** Two developers can build DAX measures on different tables in separate Git feature branches simultaneously. When merged to `dev`, Git seamlessly merges the independent table files with **zero merge conflicts**, establishing true enterprise CI/CD for Power BI.

---

### Q8.3: What is "Repository Pattern A" in Fabric Git Integration, and how does your branch-out workflow operate across environments?
* **What Interviewers Look For:** Workspace-to-Git mapping patterns, environment isolation, feature branching, and release gating.
* **Model Answer:**
  * **Repository Pattern A (Single Workspace per Branch):**
    * The repository `main` branch maps directly to the **Production Workspace**.
    * The `dev` branch maps directly to the shared **Development Workspace**.
  * **Branch-Out Developer Workflow:**
    1. A developer creates a feature branch (`feature/US-1234-gl-aging`) from `dev`.
    2. In Fabric, the developer maps their personal sandbox workspace to this feature branch.
    3. The developer builds pipelines, PySpark transformations, or TMDL measures in isolation.
    4. Changes are committed and pushed to GitHub.
    5. A GitHub Pull Request is opened against `dev`.
    6. **Automated CI Validation (`ci-validate.yml`):** Runs syntax linting, credential leak scanning, and parameter validation.
    7. Upon approval and merge to `dev`, the development workspace automatically syncs.
    8. Releases to higher environments (SIT, UAT, PROD) are promoted via tagged releases triggering GitHub Actions deployment workflows (`deploy-to-prod.yml`) using deployment service principals.

---

## 9. Real-Time Analytics & Event-Driven Ingestion

### Q9.1: How do you architect serverless, automated file ingestion in Microsoft Fabric using Real-Time Hub and Data Activator (Reflex)?
* **What Interviewers Look For:** Event-driven architecture, eliminating scheduled polling latencies, and Data Activator integration.
* **Model Answer:**
  * **The Problem:** Polling a lakehouse folder using scheduled Data Factory pipelines (e.g., every 15 minutes) introduces latency and consumes Capacity Units even when no files have been uploaded.
  * **Event-Driven Architecture:**
    1. **Event Capture (Real-Time Hub):** OneLake natively publishes system events into Fabric's Real-Time Hub whenever files are manipulated.
    2. **Event Filtering (Data Activator / Reflex):** Create a Reflex rule listening for `BlobCreated` events:
       * *Filter Conditions:* Folder path contains `Files/FlatFile_Repo/`, file extension ends in `.csv`, and exclude `/archive/`.
    3. **Action Invocation:** Data Activator triggers a parameterized Fabric Data Pipeline (`pl_ingest_bronze_flat_files`), passing the event payload's absolute file path as a runtime parameter.
    4. **Processing & Archival:** The pipeline ingests the CSV into the target Bronze Delta table and immediately moves the file to `Files/FlatFile_Repo/archive/`.
  * **Result:** Near-zero ingestion latency (under 10 seconds from upload to Bronze landing) with zero polling overhead.

---

## 10. High-Impact Architectural Scenario & Troubleshooting Questions

### Q10.1: [Scenario] On Monday morning, finance executives report that their Power BI executive dashboard is taking 25 seconds to render visuals that usually take 500 milliseconds. How do you troubleshoot and isolate the root cause?
* **What Interviewers Look For:** Systematic diagnostic methodology, Performance Analyzer, Fabric Capacity Metrics App, Direct Lake fallback detection, and memory leak analysis.
* **Model Answer:**
  * **Step 1: Inspect Power BI Performance Analyzer:**
    * Open the report in Power BI Desktop or service, start Performance Analyzer, and refresh visuals.
    * Check if query processing duration is dominated by "DAX Query" or "DirectQuery". If DirectQuery duration is high, the model has fallen back from Direct Lake to DirectQuery.
  * **Step 2: Inspect Fabric Capacity Metrics App:**
    * Check hourly CU utilization. Is the production capacity (F64) experiencing background smoothing throttling or memory paging?
    * Verify if the semantic model exceeded its 25 GB in-memory RAM limit, triggering evictions.
  * **Step 3: Check Upstream Gold Pipeline Commits:**
    * Check the latest PySpark Gold notebook run. Did someone commit a change with `spark.sql.parquet.vorder.enabled` set to `false`? Non-V-Ordered files cause VertiPaq to fail in-memory mapping.
    * Check if an upstream weekend batch load created thousands of tiny Parquet files without running `OPTIMIZE`.
  * **Step 4: Check Semantic Model Metadata Sync:**
    * Check if the post-ETL REST API refresh activity (`clearCacheAndRehydrate`) failed or was skipped, causing VertiPaq to read outdated Delta checkpoints.
  * **Step 5: Immediate Remediation:**
    * Run an ad-hoc table maintenance notebook (`OPTIMIZE Gold_Lakehouse.Fact_GL_Transactions ZORDER BY (DateKey)`).
    * Execute the REST API `clearCacheAndRehydrate` refresh call. Verify query latency drops back below 800ms.

---

### Q10.2: [Scenario] During UAT in Pre-Production, the finance audit team identifies a $50,000 discrepancy between the legacy JDE General Ledger net balance and the Microsoft Fabric Power BI report. How do you conduct reconciliation?
* **What Interviewers Look For:** Audit trail navigation, SHA-256 hash validation, handling Julian dates and implied decimals, and idempotent data reconciliation.
* **Model Answer:**
  * **Step 1: Query Bronze Staging with Delta Time Travel:**
    * Query the Bronze table (`lh_bronze.shr_F0911`) using Delta Time Travel as of the exact ingestion commit timestamp:
      ```sql
      SELECT SUM(GLAA) FROM lh_bronze.shr_F0911 TIMESTAMP AS OF '2026-09-15 08:00:00'
      ```
    * Compare this sum directly against a fresh query on the source AS400 DB2 table (`CRPOTA.F0911`). If Bronze matches AS400, the extraction was 100% complete and the discrepancy occurred downstream.
  * **Step 2: Inspect Quarantine Tables:**
    * Query `lh_silver.th_delta_named_quarantine` for records rejected by data quality rules. Check if records with null document company codes or invalid account numbers were diverted into quarantine.
  * **Step 3: Verify Implied Decimal Logic:**
    * Cross-reference currency codes (`GLCRCD`). Verify whether non-USD transactions required dynamic decimal shifting based on `CRPCTL.F0010` control rules that were missing from the conversion dictionary.
  * **Step 4: Check Soft-Delete Tombstones:**
    * Inspect the `_freshwr_deleted` audit flag to verify whether deleted records in JDE were properly flagged and filtered out of active Gold Star Schema aggregates.

---

### Q10.3: [Scenario] A data engineering team needs to deliver historical backfills spanning 10 years of JDE data across 121 tables within a 2-week sprint. How do you tune the compute and ingestion pipeline to achieve this without blowing the cloud budget?
* **What Interviewers Look For:** Parallelism, partitioning, network throughput, gateway tuning, temporary scaling, and FinOps governance.
* **Model Answer:**
  * **OPDG & Driver Tuning:** Scale the OPDG cluster across multiple nodes. Increase ODBC block fetch sizes (`BlockSizeSec=1024`) and enable compression (`ABrowLargeDataCompression=1`) to maximize throughput from AS400.
  * **Partitioned Ingestion:** Do not pull 10 years in a single monolithic query. Partition queries by Fiscal Year (`RYEAR`) and run concurrent Copy Activities in Fabric Data Factory across parallel pipeline threads.
  * **Compute Sizing & Scheduling:** Spin up an **F128 Pay-As-You-Go** non-prod capacity. Do not buy a reservation.
  * **Temporary Delta Optimizations:**
    * During raw backfill insertion, set `spark.sql.parquet.vorder.enabled = false` and disable write-time compaction to maximize raw bulk write ingestion speed.
    * Once all 10 years have landed in Gold, execute a single batch `OPTIMIZE lh_gold.Fact_Table ZORDER BY (DateKey)` with V-Order enabled during off-peak hours.
  * **FinOps Governance:** Enforce the Logic App scheduler to suspend the F128 capacity outside of sprint testing hours to prevent run-away billing.

---

## Technical Summary Cheatsheet for Quick Revision

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FABRIC LEAD ENGINEER QUICK CHEATSHEET                               │
├───────────────────────────────┬─────────────────────────────────────────────────────────────────────┤
│ Storage Format                │ Delta Parquet in OneLake (Decoupled @ $0.023/GB/mo)                 │
│ Gold Layer Target             │ Fabric Lakehouse (Read-Only SQL Analytics Endpoint + Direct Lake)  │
│ Write Optimization            │ V-Order (Isomorphic to VertiPaq RAM layout)                         │
│ Compaction Cadence            │ Weekly OPTIMIZE (128 MB – 512 MB target file size)                  │
│ Retention & Vacuum            │ VACUUM RETAIN 168 HOURS (Strict 7-day Time Travel disaster window)  │
│ Semantic Model Strategy       │ Custom Semantic Model ONLY (Default Model strictly banned in Prod)  │
│ Direct Lake Fallback Pitfalls │ DAX Calculated Columns/Tables, SQL Views with RLS, RAM > Capacity   │
│ Semantic Cache Refresh        │ REST API: clearCacheAndRehydrate (< 1 sec execution)                │
│ Hybrid Ingestion Security     │ Outbound Port 443 only via On-Premises Data Gateway (OPDG)          │
│ FinOps Implementation State   │ 192 CUs (Prod F64 1-Yr Reserved + Non-Prod F128 Scheduled PAYG)     │
│ FinOps Steady State           │ 96 CUs (Prod F64 1-Yr Reserved + Non-Prod F32 1-Yr Reserved)        │
│ The Downscale Trap            │ Azure Reservations cannot be exchanged to lower total dollar spend  │
│ Git Serialization Standards   │ Notebooks as pure .py scripts; Semantic Models as TMDL text files   │
│ Event-Driven Ingestion        │ OneLake BlobCreated -> Real-Time Hub -> Data Activator -> Pipeline  │
└───────────────────────────────┴─────────────────────────────────────────────────────────────────────┘
```
