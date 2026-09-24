# Fabric Connection Setup Guide: Service Principal & Variable Library

A step-by-step engineering implementation guide for configuring headless, resilient database connectivity to a **Microsoft Fabric SQL Database** (`sqldb-meta-orch-dev`) in the `bim-data-dev` workspace using a generic **Microsoft Entra ID Service Principal (SPN)**, and managing dynamic multi-environment configurations (Dev, Test, Prod) via Microsoft Fabric's **Variable Library**.

---

## Table of Contents
1. [Overview & Strategic Motivation](#1-overview--strategic-motivation)
2. [Architectural Relationship Flow](#2-architectural-relationship-flow)
3. [Step 1: Create the Service Principal (SPN) in Microsoft Entra ID](#3-step-1-create-the-service-principal-spn-in-microsoft-entra-id)
4. [Step 2: Grant Permissions to the Service Principal](#4-step-2-grant-permissions-to-the-service-principal)
   - [A. Tenant Admin Consent (Fabric Control Plane)](#a-tenant-admin-consent-fabric-control-plane)
   - [B. Workspace Permissions (Fabric Item Level)](#b-workspace-permissions-fabric-item-level)
   - [C. SQL Database Permissions (Data Plane T-SQL)](#c-sql-database-permissions-data-plane-t-sql)
5. [Step 3: Create the Connection in Microsoft Fabric](#5-step-3-create-the-connection-in-microsoft-fabric)
6. [Step 4: Configure and Use the Variable Library](#6-step-4-configure-and-use-the-variable-library)
   - [A. Create the Variable Library](#a-create-the-variable-library)
   - [B. Define Connection References and Variables](#b-define-connection-references-and-variables)
   - [C. Reference in Fabric Data Pipelines](#c-reference-in-fabric-data-pipelines)
7. [Troubleshooting & Key Enterprise Considerations](#7-troubleshooting--key-enterprise-considerations)

---

## 1. Overview & Strategic Motivation

In standard data pipeline implementations, connections created using individual user accounts (OAuth 2.0) pose major operational risks:
* **Account Deactivation**: When an engineer or contractor leaves the company, pipeline credentials break, resulting in critical production data orchestration failures.
* **Password Expiration & MFA**: Multi-Factor Authentication (MFA) prompts and rolling corporate password policies interrupt automated scheduled pipeline executions.
* **Lack of Least Privilege**: User accounts often have excessive administrative privileges across the tenant.

**The Solution:**
1. Connect via an **Entra ID Service Principal (SPN)** with non-interactive, certificate/secret-based authentication dedicated to automated pipeline workloads.
2. Abstract and decouple connection strings using Fabric's **Variable Library** (`lib-orch-config`), allowing automated CI/CD and multi-environment promotion (Dev $\rightarrow$ Test $\rightarrow$ Prod) without modifying pipeline activity definitions.

---

## 2. Architectural Relationship Flow

The relationship flow spans the **Identity Tier** (Entra ID), **Fabric Control Plane** (Workspace Roles), **Fabric Data Plane** (SQL Database Permissions), and the **Orchestration Tier** (Pipelines & Variable Library):

![Fabric Connection Setup Guide - Part 1](/Users/chandu/Documents/Python_practice/Fabric/images/10_fabric_spn_variable_library_setup_p1.png)

```mermaid
flowchart TD
    subgraph ENTRA["Microsoft Entra ID (Identity Tier)"]
        SPN["Service Principal (SPN)\nspn-fabric-bim-dev"]
    end

    subgraph CONTROL_PLANE["Fabric Control Plane"]
        WS_ROLE["Fabric Workspace Access\nRole: Viewer or Contributor\n(bim-data-dev)"]
    end

    subgraph DATA_PLANE["Fabric Data Plane (Database Engine)"]
        SQL_DB[("Fabric SQL Database\nsqldb-meta-orch-dev\nCREATE USER & db_datareader")]
    end

    subgraph ORCH["Orchestration & Governance Tier"]
        VAR_LIB["Variable Library\nlib-orch-config\n(Connection Reference: Orch_DB_Connection)"]
        PIPE["Fabric Data Pipeline\n(Copy / Lookup / Stored Proc Activities)"]
    end

    SPN -->|Workspace Role Assignment| WS_ROLE
    SPN -->|Provision External Provider User| SQL_DB
    VAR_LIB -->|Dynamic Connection Resolution| PIPE
    PIPE -->|Azure SQL DB Connector with SPN Secret| SQL_DB
```

---

## 3. Step 1: Create the Service Principal (SPN) in Microsoft Entra ID

1. Navigate to the **Microsoft Entra ID Portal** (`https://entra.microsoft.com/` or Azure Portal > Microsoft Entra ID).
2. Under **Manage**, select **App registrations** > **New registration**.
3. Register a new application with the generic enterprise naming convention:
   * **Name**: `spn-fabric-bim-dev`
   * **Supported account types**: Accounts in this organizational directory only (Single tenant).
   * **Redirect URI**: Leave blank.
   * Click **Register**.

4. On the registered application's **Overview** page, record the following core identifiers:
   * **Application (client) ID**: `6f60b84c-cbde-4ded-9027-ce3fc8deb77d`
   * **Directory (tenant) ID**: `2097bb0c-110b-414c-9b7f-293ddc46d353`

5. Under **Manage**, navigate to **Certificates & secrets** > **Client secrets** tab > click **New client secret**.
   * **Description**: `Fabric Pipeline Orchestration Secret`
   * **Expires**: Recommended 180 or 365 days (per organizational security policies).
   * Click **Add**.

6. **Immediately copy the `Value`** of the secret key (it is only displayed once):
   * **Secret Value**: `Apl8Q~toqO15RiAPzstP_NuN-Ef4OcV7sQVNycGx`
   > [!CAUTION]
   > Store this secret value securely in **Azure Key Vault**. If lost, a new secret must be generated and all dependent connections updated.

---

## 4. Step 2: Grant Permissions to the Service Principal

Security must be established across three distinct boundaries: Tenant Control Plane, Workspace Item Level, and SQL Database Data Plane.

### A. Tenant Admin Consent (Fabric Control Plane)
1. An administrator with Fabric Administrator privileges must open the **Fabric Admin Portal** (`app.fabric.microsoft.com`).
2. Navigate to **Tenant settings** > scroll to **Developer settings**.
3. Locate the setting **"Service principals can use Fabric APIs"**.
4. Set the toggle to **Enabled**:
   * Apply to: Either **The entire organization** or a **Specific security group** (e.g., `SG-Fabric-Service-Principals`) containing `spn-fabric-bim-dev`.
5. Click **Apply**.

### B. Workspace Permissions (Fabric Item Level)
1. Open the Microsoft Fabric workspace: `bim-data-dev`.
2. Click **Manage access** in the top-right toolbar.
3. Click **+ Add people or groups**.
4. Search for the Service Principal by name: `spn-fabric-bim-dev` (or paste its Application Client ID).
5. Assign the appropriate workspace role:
   * **Viewer**: Sufficient if the pipeline only reads data and executes read-only stored procedures.
   * **Contributor**: Recommended if pipelines need to write, create, or modify Fabric workspace items, tables, or metadata.
6. Click **Add**.

### C. SQL Database Permissions (Data Plane T-SQL)
1. Connect to the Fabric SQL Database `sqldb-meta-orch-dev` using an administrative Entra ID user account via:
   * **SQL Server Management Studio (SSMS)**
   * **Azure Data Studio**
   * **Fabric Web Query Editor**
2. Execute the following T-SQL script to provision the SPN database user from the external provider and assign role memberships:

```sql
-- 1. Create a database user linked directly to the Entra ID Service Principal
CREATE USER [spn-fabric-bim-dev] FROM EXTERNAL PROVIDER;
GO

-- 2. Grant read permissions across user tables
ALTER ROLE db_datareader ADD MEMBER [spn-fabric-bim-dev];
GO

-- 3. Grant write permissions (Required only if pipeline performs inserts, updates, or creates tables)
ALTER ROLE db_datawriter ADD MEMBER [spn-fabric-bim-dev];
GO

-- 4. (Optional) Grant EXECUTE permissions if orchestrating through stored procedures
GRANT EXECUTE TO [spn-fabric-bim-dev];
GO
```

> [!NOTE]
> When executing `CREATE USER [spn-fabric-bim-dev] FROM EXTERNAL PROVIDER`, the bracketed name must match the exact **Display Name** of the App Registration in Microsoft Entra ID.

---

## 5. Step 3: Create the Connection in Microsoft Fabric

![Fabric Connection Setup Guide - Part 2](/Users/chandu/Documents/Python_practice/Fabric/images/11_fabric_spn_variable_library_setup_p2.png)

> [!IMPORTANT]
> The native **"SQL Database"** connector in Microsoft Fabric currently restricts authentication to interactive **OAuth 2.0**. To authenticate programmatically using a Service Principal and Client Secret, you must select the **Azure SQL Database** connector.

### Connection Configuration Steps
1. Navigate to the Fabric workspace or click the **Settings** (gear icon) in the top-right header > select **Manage connections and gateways**.
2. Under the **Connections** tab, click **+ New** to register a new connection.
3. Select **Azure SQL Database** as the connection type.
4. Populate the connection properties exactly as configured:

| Field Name | Configuration Value | Notes |
| :--- | :--- | :--- |
| **Server** | `bs5zoialcfgedg37fe65yrwtkm-umyi6bvdalrexnstkq5x2tl6sn4.database.fabric.microsoft.com,1433` | Fabric SQL Database connection endpoint with port `,1433` |
| **Database** | `sqldb-meta-orch-dev-cec2b813-3d30-43da-b7f1-813ef67af7a2` | Full GUID-qualified Fabric SQL database name |
| **Authentication kind** | `Service Principal` | Dropdown selection |
| **Tenant ID** | `2097bb0c-110b-414c-9b7f-293ddc46d353` | Entra ID Directory ID from Step 1 |
| **Service principal client ID** | `6f60b84c-cbde-4ded-9027-ce3fc8deb77d` | Application ID from Step 1 |
| **Service principal key** | `Apl8Q~toqO15RiAPzstP_NuN-Ef4OcV7sQVNycGx` | Secret value generated in Step 1 |

5. Click **Create** to test and save the connection.

---

## 6. Step 4: Configure and Use the Variable Library

The **Variable Library** in Microsoft Fabric provides centralized configuration management, allowing pipelines to dynamically resolve database connections and parameters based on the deployment target (Dev, Test, or Prod).

### A. Create the Variable Library
1. In your Fabric workspace (`bim-data-dev`), select **+ New item** > search for and select **Variable library**.
2. Give the library a standardized configuration name: `lib-orch-config`.
3. Click **Create**.

### B. Define Connection References and Variables
1. Within `lib-orch-config`, click **+ Add variable** and define:
   * **Name**: `Orch_DB_Connection`
   * **Data Type**: `Connection reference`
   * **Default / Active Value**: Select the connection created in Step 3 (`sqldb-meta-orch-dev` via `spn-fabric-bim-dev`).
2. *(Optional)* Add companion environment variables for string interpolation:
   * `Database_Server` (Type: `String`)
   * `Database_Name` (Type: `String`)
   * `Environment_Tag` (Type: `String`, e.g., `DEV`)
3. Create **Environment Value Sets** (e.g., `DEV`, `TEST`, `PROD`):
   * Map `Orch_DB_Connection` to the respective environment database connection for each lifecycle stage.
4. Save and publish the Variable Library.

### C. Reference in Fabric Data Pipelines
1. Open your target **Fabric Data Pipeline**.
2. Go to the pipeline **Settings** ribbon > select **Variable Libraries** > add a reference to `lib-orch-config`.
3. In any pipeline activity (**Copy Data**, **Lookup**, **Script**, or **Stored Procedure**):
   * Under the **Settings** or **Connection** tab, switch to dynamic content.
   * Bind the connection dynamically using the pipeline expression syntax:

```json
@variables('Orch_DB_Connection')
```

```mermaid
flowchart LR
    A[Fabric Pipeline Activity] -->|Reads Expression| B["@variables('Orch_DB_Connection')"]
    B -->|Resolves At Runtime| C[Variable Library: lib-orch-config]
    C -->|Points to Active Value Set| D[Azure SQL DB Connector: spn-fabric-bim-dev]
    D -->|Executes Query| E[(sqldb-meta-orch-dev)]
```

---

## 7. Troubleshooting & Key Enterprise Considerations

### 1. Authentication Failures (`Login failed for user '<token-identified principal>'`)
* **Cause**: T-SQL user mapping mismatch or missing external provider link.
* **Resolution**: Ensure the user in the database was created using `CREATE USER [spn-fabric-bim-dev] FROM EXTERNAL PROVIDER`. The username inside brackets must match the **exact Application Display Name** in Microsoft Entra ID, not the Client ID.

### 2. Firewall & Network Rule Violations
* **Cause**: Network security blocking external Fabric compute nodes.
* **Resolution**: In the Fabric SQL Database security settings, ensure **"Allow Azure services and resources to access this server"** is set to `Yes`. If Private Link is enabled, ensure the Self-Hosted Integration Runtime or Managed Virtual Network gateway is properly configured.

### 3. Client Secret Rotation & Expiration Strategy
* **Risk**: Service Principal client secrets have strict maximum lifetimes (typically 6 to 24 months). If a secret expires unmonitored, all scheduled pipeline runs will immediately fail.
* **Best Practice**:
  1. Store the secret expiration date in an **Azure Key Vault** secret tag.
  2. Configure an automated **Azure Event Grid** subscription or Logic App to trigger email notifications 30 days and 7 days prior to secret expiry.
  3. Perform zero-downtime secret rollover: Generate a secondary secret in Entra ID, update the Fabric connection key, verify pipeline runs, and then delete the old expired secret.

### 4. Environment Promotion (CI/CD Deployment Pipelines)
* By utilizing the **Variable Library**, Fabric deployment pipelines automatically switch the connection pointer from `DEV_Connection` to `TEST_Connection` or `PROD_Connection` during stage promotion without requiring git merges or manual activity rewrites.
