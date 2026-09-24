# Fivetran Destination Architecture & Migration Guide for Microsoft Fabric

> **Project:** IPS Corporation BI Modernization  
> **Topic:** Fivetran Destination Architecture Evaluation (ADLS Gen2 vs. Direct Fabric Lakehouse) & End-to-End Migration Runbook  
> **Target Environment:** Microsoft Fabric (`bim_data_dev` / `bim_data_prod`) | Azure Central US  
> **Author:** IPS Data Engineering & Architecture Team  
> **Date:** September 2026  
> **Status:** Production Architecture Standard  

---

## Executive Summary

In Fivetran, **destination types are permanently fixed once created**. When architecting the near real-time ingestion stream from IBM AS400 DB2i into Microsoft Fabric for the **IPS BI Modernization project**, two architectural patterns exist for routing landed change data:
1. **Option A (ADLS Gen2 Landing Storage):** Fivetran writes raw Parquet to an Azure Data Lake Storage Gen2 container, which Microsoft Fabric subsequently accesses via OneLake external shortcuts or secondary copy pipelines.
2. **Option B (Direct Fabric Lakehouse Destination):** Fivetran writes native Delta Lake tables directly into the Bronze Lakehouse (`lh_bronze_dev`) inside the Fabric workspace (`bim_data_dev`) using the native Microsoft Fabric connector.

This guide provides a comprehensive architectural evaluation of both patterns, details the formal recommendation of **Option B**, and presents the complete, step-by-step production runbook to transition from ADLS Gen2 to direct Microsoft Fabric Lakehouse destination.

---

## Table of Contents
1. [Architecture Comparison: Option A vs. Option B](#1-architecture-comparison-option-a-vs-option-b)
2. [Detailed Pros & Cons Analysis](#2-detailed-pros--cons-analysis)
3. [Formal Architectural Recommendation](#3-formal-architectural-recommendation)
4. [Step-by-Step Migration Runbook: Moving from ADLS Gen2 to Fabric Lakehouse](#4-step-by-step-migration-runbook-moving-from-adls-gen2-to-fabric-lakehouse)
   - [Phase 1: Azure Portal Setup (Service Principal & Credentials)](#phase-1-azure-portal-setup-service-principal--credentials)
   - [Phase 2: Microsoft Fabric Configuration (Tenant & Workspace RBAC)](#phase-2-microsoft-fabric-configuration-tenant--workspace-rbac)
   - [Phase 3: Fivetran Dashboard Setup & Connector Re-creation](#phase-3-fivetran-dashboard-setup--connector-re-creation)
   - [Phase 4: Data Validation, Reporting Cutover & Decommissioning](#phase-4-data-validation-reporting-cutover--decommissioning)
5. [Enterprise Infrastructure & Connection Reference](#5-enterprise-infrastructure--connection-reference)

---

## 1. Architecture Comparison: Option A vs. Option B

![Fivetran Destination Architecture Comparison](/Users/chandu/Documents/Python_practice/Fabric/images/34_fivetran_destination_options_adls_vs_fabric_lakehouse_p1.png)

```mermaid
flowchart TD
    subgraph OPTION_A["Option A: Fivetran to ADLS Gen2 Container (Intermediate Hop)"]
        SRC_A["IBM AS400 DB2i\n(Source Data)"] -->|CDC Log Stream| FT_A["Fivetran Engine"]
        FT_A -->|Writes Parquet Files| ADLS["Azure Data Lake Storage Gen2\n(ipsazfdl / fivetran-as400-db2-destination)"]
        ADLS -->|OneLake External Shortcut\nor Copy Pipeline| SC["lh_bronze_dev\n(Files/landing_as400_crpdta)"]
        SC -->|Fabric Notebook Processing| SLV_A["lh_silver_dev"]
        SLV_A -->|Gold Modeling| GLD_A["lh_gold_dev"]
    end

    subgraph OPTION_B["Option B: Direct to Microsoft Fabric Lakehouse (Recommended)"]
        SRC_B["IBM AS400 DB2i\n(Source Data)"] -->|CDC Log Stream| FT_B["Fivetran Engine"]
        FT_B -->|Native Delta Lake Tables| BRZ_B["lh_bronze_dev\n(Fabric Workspace: bim_data_dev)"]
        BRZ_B -->|Instant SQL Endpoint & PySpark| SLV_B["lh_silver_dev"]
        SLV_B -->|Direct Lake Dimensional Modeling| GLD_B["lh_gold_dev"]
    end
```

### Pipeline Flow Topologies:
* **Option A (ADLS Gen2):**
  $$\text{[Source Data]} \longrightarrow \text{[Fivetran]} \longrightarrow \text{[ADLS Gen2 Container]} \longrightarrow \text{(OneLake Shortcut / Pipeline)} \longrightarrow \text{[lh\_bronze\_dev]}$$
* **Option B (Direct Fabric Lakehouse):**
  $$\text{[Source Data]} \longrightarrow \text{[Fivetran]} \longrightarrow \text{[lh\_bronze\_dev in Fabric Workspace 'bim\_data\_dev']}$$

---

## 2. Detailed Pros & Cons Analysis

### Option A: Fivetran $\rightarrow$ ADLS Gen2 Container

In this pattern, Fivetran lands raw files into an ADLS Gen2 storage account (`ipsazfdl`). Microsoft Fabric subsequently accesses this external storage via OneLake Shortcuts or scheduled Fabric Data Factory pipelines.

| Category | Evaluation | Technical Analysis |
| :--- | :--- | :--- |
| **Pros** | **Vendor & Platform Agnostic** | Raw data lands in an independent Azure storage account. Non-Fabric systems (e.g., Azure Synapse, Databricks, custom Python scripts, external machine learning pipelines) can access data without interacting with Microsoft Fabric. |
| | **Independent Storage Lifecycle** | Lifecycle management policies (Hot $\rightarrow$ Cool $\rightarrow$ Archive tiering) can be configured directly on the ADLS Gen2 container without impacting Fabric workspace storage. |
| | **Storage Cost Isolation** | ADLS Gen2 storage billing is kept distinct and separate from Fabric Capacity Unit (CU) consumption. |
| **Cons** | **Extra Architectural Hop & Complexity** | Requires configuring, securing, and maintaining OneLake Shortcuts or secondary copy pipelines to bridge data into `lh_bronze_dev`. |
| | **Higher End-to-End Latency** | Data must fully land and close in ADLS Gen2 before Microsoft Fabric indexes it via shortcuts or ingests it into Bronze Delta tables, threatening the 15-minute SLA. |
| | **Additional Governance Overhead** | Requires managing dual-layer security: SAS tokens, Azure Storage firewalls, Azure Entra ID RBAC on ADLS Gen2 *plus* Fabric workspace permissions. |

---

### Option B: Fivetran $\rightarrow$ Microsoft Fabric Lakehouse (`lh_bronze_dev`) Directly

In this pattern, Fivetran leverages its native **Microsoft Fabric Destination Connector** to write Delta Lake tables directly into the `lh_bronze_dev` Lakehouse within the `bim_data_dev` workspace.

| Category | Evaluation | Technical Analysis |
| :--- | :--- | :--- |
| **Pros** | **Zero-Copy / Native OneLake Ingestion** | Data lands directly into `lh_bronze_dev` as native Delta Lake tables in OneLake without intermediate staging storage. |
| | **Instant Availability for Direct Lake & SQL Endpoint** | The moment Fivetran completes a sync, tables are immediately queryable via Fabric PySpark Notebooks, the Lakehouse SQL Analytics Endpoint, and Power BI Direct Lake mode. |
| | **Simplified Architecture** | Completely eliminates intermediate storage accounts, access keys, secondary pipeline triggers, and shortcut path maintenance. |
| | **Perfect Medallion Architecture Alignment** | `lh_bronze_dev` acts naturally as the raw landing layer. Fabric Notebooks immediately transform `lh_bronze_dev` $\rightarrow$ `lh_silver_dev` $\rightarrow$ `lh_gold_dev`. |
| | **Lower Operational Maintenance** | Fewer moving parts, reducing points of failure, silent sync dropouts, and monitoring surface area. |
| **Cons** | **Fabric Capacity (CU) Consumption** | Heavy Fivetran sync writes and metadata commits consume Microsoft Fabric Capacity Units (CUs) for OneLake writes and transactions. |
| | **Coupled to Fabric Ecosystem** | External tools not integrated with Microsoft Azure or Fabric must query data through Fabric OneLake endpoints rather than raw blob storage APIs. |

---

## 3. Formal Architectural Recommendation

![Recommendation & Migration Phases 1 and 2](/Users/chandu/Documents/Python_practice/Fabric/images/35_fivetran_destination_migration_phases_1_and_2_p2.png)

> [!IMPORTANT]
> **RECOMMENDED: Option B (Direct to `lh_bronze_dev`)**  
> For the IPS Corporation BI Modernization initiative, **Option B is strongly recommended** as the corporate target architecture.

### Architectural Justifications:
1. **Medallion Architecture Purpose**: `lh_bronze_dev` was provisioned specifically to serve as the raw ingestion layer in `bim_data_dev`. Having Fivetran write directly into `lh_bronze_dev` fulfills its exact purpose without needing redundant staging tiers.
2. **Eliminates Unnecessary Pipelines**: Using ADLS Gen2 requires building extra Fabric Pipelines or maintaining OneLake external shortcuts just to expose the data inside `lh_bronze_dev`. Direct ingestion automates the entire Bronze landing lifecycle.
3. **Unlocks Fabric Native Performance**: Fivetran writes native Delta Lake format directly into OneLake, making data instantly available to the Fabric SQL Analytics Endpoint and accelerating downstream Silver/Gold transformations to easily meet the **15-minute end-to-end SLA**.

---

## 4. Step-by-Step Migration Runbook: Moving from ADLS Gen2 to Fabric Lakehouse

Because Fivetran does not permit modifying an existing destination's type, transitioning to Option B requires creating a new Microsoft Fabric destination, configuring Azure and Fabric permissions, re-pointing connectors, and decommissioning the legacy ADLS Gen2 storage.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Cloud Admin
    participant Azure as Azure Entra ID & Portal
    participant Fabric as Microsoft Fabric Admin & Workspace
    participant FT as Fivetran Dashboard
    participant Lakehouse as lh_bronze_dev (OneLake)

    Admin->>Azure: Phase 1: Create App Registration (Fivetran-Fabric-Destination-SP)
    Azure-->>Admin: Returns Client ID, Tenant ID & Secret
    Admin->>Fabric: Phase 2: Enable "Service principals can use Fabric APIs" in Tenant
    Admin->>Fabric: Grant SPN "Member" role on Workspace bim_data_dev
    Admin->>Fabric: Retrieve Workspace ID & Lakehouse ID
    Admin->>FT: Phase 3: Add Destination -> Microsoft Fabric
    Admin->>FT: Enter Workspace ID, Lakehouse ID, Tenant ID, Client ID, Secret
    FT->>Lakehouse: Test Connection & Write Privileges
    Lakehouse-->>FT: Validation Successful
    Admin->>FT: Re-create Connectors (AS400, Salesforce, etc.) & Start Historical Sync
    Admin->>Fabric: Phase 4: Validate Tables via SQL Analytics Endpoint
    Admin->>FT: Pause/Delete legacy ADLS Gen2 destination
```

---

### Phase 1: Azure Portal Setup (Service Principal & Credentials)

Fivetran connects to Microsoft Fabric securely via an Azure Entra ID (formerly Azure Active Directory) Service Principal.

#### 1.1 Create an App Registration (Service Principal):
1. Sign in to the **Azure Portal** (`https://portal.azure.com`).
2. Search for and select **Microsoft Entra ID**.
3. In the left navigation bar, select **App registrations** $\rightarrow$ click **+ New registration**.
4. Configure registration settings:
   * **Name**: `Fivetran-Fabric-Destination-SP`
   * **Supported account types**: Select *Accounts in this organizational directory only (Single tenant)*.
   * **Redirect URI**: Leave blank.
5. Click **Register**.

#### 1.2 Record App IDs & Create Client Secret:
1. On the App Registration **Overview** page, copy and save the GUID values:
   * **Application (client) ID**: `d3ace6c2-c791-4193-94e0-640eb5abf8d9`
   * **Directory (tenant) ID**: `2097bb0c-110b-414c-9b7f-293ddc46d353`
2. In the left navigation menu of the registered app, select **Certificates & secrets**.
3. Under **Client secrets**, click **+ New client secret**.
4. Enter a description (e.g., `Fivetran Secret`), set an expiration period (180 or 730 days per corporate security policy), and click **Add**.
5. **IMPORTANT**: Copy the secret **Value** immediately (this value is permanently masked after leaving the page):
   * **Client Secret Value**: `eY78Q~Tzwb3vYslLcmy5OS8RI~qWK.1_1mkX.cjw`

---

### Phase 2: Microsoft Fabric Configuration (Tenant & Workspace RBAC)

#### 2.1 Enable Service Principal Access at Tenant Level
> [!NOTE]
> Requires Fabric Administrator or Global Administrator credentials.

1. Sign in to **Microsoft Fabric** (`https://app.fabric.microsoft.com`).
2. Click the **Settings (gear icon)** in the top-right corner and select **Admin portal**.
3. Under **Tenant settings**, scroll down to **Developer settings**.
4. Expand **Service principals can use Fabric APIs**:
   * Set toggle to **Enabled**.
   * Choose **The entire organization** OR select **Specific security groups** (and add the security group containing `Fivetran-Fabric-Destination-SP`).
5. Click **Apply**. *(Note: Tenant setting changes may take 10–15 minutes to take global effect).*

#### 2.2 Grant Workspace Access to the Service Principal
1. In Microsoft Fabric, navigate to the target workspace where your Lakehouse resides: **`bim_data_dev`**.
2. Click **Manage access** in the top workspace toolbar.
3. Click **+ Add people or groups**.
4. Search for your Service Principal name (`Fivetran-Fabric-Destination-SP`) or Application (Client) ID.
5. Assign the role: **Member** or **Admin**.
   > [!IMPORTANT]
   > The **Member** role is strictly required. The *Contributor* or *Viewer* role does not grant sufficient write and metadata commit permissions to OneLake Delta tables and delta transaction logs (`_delta_log`).
6. Click **Add**.

#### 2.3 Retrieve Workspace & Lakehouse IDs
1. Open your target Lakehouse: **`lh_bronze_dev`** inside the `bim_data_dev` workspace.
2. Examine the browser URL address bar:
   ```text
   https://app.fabric.microsoft.com/groups/<WORKSPACE_ID>/lakehouses/<LAKEHOUSE_ID>
   ```
3. Extract and record the GUID values:
   * **Workspace ID**: `068f30a3-02a3-4be2-b653-543b7d2fd26f`
   * **Lakehouse ID**: `d262f4a6-c56b-4c86-ae28-7f44ae0c7861`

---

### Phase 3: Fivetran Dashboard Setup & Connector Re-creation

![Fivetran Dashboard Configuration & Phases 3 and 4](/Users/chandu/Documents/Python_practice/Fabric/images/36_fivetran_destination_migration_phases_3_and_4_p3.png)

#### 3.1 Add the New Microsoft Fabric Destination
1. Log in to the **Fivetran Dashboard**.
2. Click **Destinations** in the left sidebar.
3. Click **+ Add Destination** in the top-right corner.
4. Enter a Destination Name (e.g., `Fabric_Lakehouse_Dev` or `Fabric_Lakehouse_Prod`).
5. Click **Add Destination**.
6. Select **Microsoft Fabric** (or **Fabric Lakehouse**) as the destination type.

#### 3.2 Enter Connection Parameters & Save
Enter the connection parameters gathered in previous phases:

| Fivetran Field Name | Source / Description | Verified Production Parameter Value |
| :--- | :--- | :--- |
| **Workspace ID** | Fabric Workspace GUID from browser URL | `068f30a3-02a3-4be2-b653-543b7d2fd26f` |
| **Lakehouse ID** | Fabric Lakehouse GUID from browser URL | `d262f4a6-c56b-4c86-ae28-7f44ae0c7861` |
| **Tenant ID** | Azure Entra Directory (Tenant) GUID | `2097bb0c-110b-414c-9b7f-293ddc46d353` |
| **Client ID** | App Registration Application (Client) GUID | `d3ace6c2-c791-4193-94e0-640eb5abf8d9` |
| **Client Secret** | App Registration Client Secret Value | `eY78Q~Tzwb3vYslLcmy5OS8RI~qWK.1_1mkX.cjw` |

Click **Save & Test**. Ensure that all automated connectivity, OneLake write permission, and schema creation tests pass successfully.

#### 3.3 Re-create & Configure Connectors
1. Under the new Microsoft Fabric destination, navigate to **Connectors**.
2. Click **+ Add Connector** and configure the required data sources:
   * **IBM AS400 DB2i Connector**: Syncing core transactional ledger tables (`F0911`, `F0902`, `F03B11`, `F0011`, `F0411`).
   * **Salesforce, PostgreSQL, and SQL Server Connectors**.
3. Select desired schemas, tables, and set sync frequency (e.g., **5 Minutes** for near real-time AS400 ledgers).
4. Click **Save & Test** and initiate the **Historical Sync**.

---

### Phase 4: Data Validation, Reporting Cutover & Decommissioning

#### 4.1 Data Validation in Fabric Lakehouse
1. Once the initial sync completes in Fivetran, open **`lh_bronze_dev`** in Microsoft Fabric.
2. Verify that tables are created under **Tables** in native **Delta Lake format** (not under Files).
3. Switch to the **SQL Analytics Endpoint** and execute verification queries:
   ```sql
   -- Row count validation query
   SELECT 
       'bronze_f0911' AS table_name, 
       COUNT(1) AS row_cnt, 
       MAX(_fivetran_synced) AS latest_sync
   FROM lh_bronze_dev.dbo.f0911
   UNION ALL
   SELECT 
       'bronze_f03b11' AS table_name, 
       COUNT(1) AS row_cnt, 
       MAX(_fivetran_synced) AS latest_sync
   FROM lh_bronze_dev.dbo.f03b11;
   ```
4. Validate row counts against source systems to verify zero data loss.

#### 4.2 Cutover Downstream Tools
1. **Power BI Semantic Models**: Update Direct Lake models to read directly from the native `lh_bronze_dev` Delta tables rather than through ADLS Gen2 shortcut paths.
2. **Spark / dbt Transformations**: Update PySpark notebook data sources in `nb_silver_generic_engine` to read directly from `lh_bronze_dev` tables.

#### 4.3 Decommission ADLS Gen2 Connection
1. In Fivetran, navigate to the old **ADLS Gen2 Destination**.
2. **Pause or Delete** all legacy connectors associated with ADLS Gen2.
3. Once data retention and audit verification periods expire (typically 30–60 days), archive or delete the old ADLS Gen2 storage container (`fivetran-as400-db2-destination`) to eliminate idle storage costs.

---

## 5. Enterprise Infrastructure & Connection Reference

The table below consolidates the verified cloud infrastructure parameters for IPS Corporation:

| Infrastructure Resource | Parameter / Value | Description |
| :--- | :--- | :--- |
| **Azure Subscription** | `test-sub` | Primary development subscription |
| **Resource Group** | `test-fabric-centralus-rg` | Resource group hosting Fabric & storage |
| **Azure Region** | `CentralUS` | Primary cloud region |
| **Storage Account** | `ipsazfdl` | Legacy ADLS Gen2 account |
| **Storage Container (Legacy)** | `fivetran-as400-db2-destination` | ADLS landing container |
| **Storage Container (Lakehouse Staging)**| `fivetran-as400-lkh-destination` | Staging container for Lakehouse connectivity |
| **Azure RBAC Role** | **Storage Blob Data Owner** | Assigned to `Fivetran-Fabric-Destination-SP` on container `fivetran-as400-lkh-destination` |
| **Fabric Workspace** | `bim_data_dev` (`068f30a3-02a3-4be2-b653-543b7d2fd26f`) | Dev engineering workspace |
| **Fabric Lakehouse** | `lh_bronze_dev` (`d262f4a6-c56b-4c86-ae28-7f44ae0c7861`) | Raw ingestion Lakehouse |
| **Service Principal (SPN)** | `Fivetran-Fabric-Destination-SP` | Non-interactive automation account |
| **SPN Client ID** | `d3ace6c2-c791-4193-94e0-640eb5abf8d9` | Registered App client GUID |
| **SPN Tenant ID** | `2097bb0c-110b-414c-9b7f-293ddc46d353` | Azure Entra Directory GUID |
