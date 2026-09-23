# Enterprise Azure Data Platform — Architecture Document

> **Derived from project architecture diagrams (5 images)**
> Generated: 2026-09-22

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Layer 1 — Data Platform Architecture (Microsoft Fabric)](#2-layer-1--data-platform-architecture-microsoft-fabric)
3. [Layer 2 — Network Topology (Connectivity Subscription)](#3-layer-2--network-topology-connectivity-subscription)
4. [Layer 3 — Firewall & Virtual WAN](#4-layer-3--firewall--virtual-wan)
5. [Layer 4 — Production Subscription & Workloads](#5-layer-4--production-subscription--workloads)
6. [Layer 5 — Database & Data Gateway Networks](#6-layer-5--database--data-gateway-networks)
7. [IP Address Plan](#7-ip-address-plan)
8. [Security & Governance Summary](#8-security--governance-summary)

---

## 1. High-Level Overview

This architecture represents an **enterprise-grade Azure landing zone** integrated with **Microsoft Fabric** for data analytics. It follows a **Hub-Spoke network topology** using **Azure Virtual WAN (vWAN)**, with centralized firewall, DNS, and bastion services in the **Connectivity subscription**, and workload VNets in the **Production subscription**.

```mermaid
graph TB
    subgraph "Enterprise Architecture Layers"
        direction TB
        A["🏢 Data Sources<br/>JD Edwards · Salesforce · Legacy DB · Excel · API · Flat Files"]
        B["⚙️ Layer 1: Ingestion<br/>Fabric Data Pipelines · Mirror DB · Shortcuts · Eventhouse"]
        C["💾 Layer 2: Storage & Processing<br/>Medallion Architecture · OneLake · Delta Parquet<br/>Real-Time Analytics · Spark Notebooks · Agentic AI"]
        D["📊 Layer 3: BI & Analytics<br/>Power BI · Data Marketplace · Agentic BI · Data Science Workbench"]
        E["🔒 Layer 4: Data Governance<br/>Microsoft Purview · MDM · Data Quality · Lineage"]
        F["🛡️ Layer 5: Platform Management<br/>Security · Monitoring · IAM · DevOps · FinOps"]
        G["🌐 Layer 6: Azure Networking<br/>vWAN · Firewall · DNS · Bastion · VNet Peering"]
    end

    A --> B --> C --> D
    C --> E
    F -.->|"Underpins all layers"| A
    F -.-> B
    F -.-> C
    F -.-> D
    G -.->|"Connects all layers"| F

    style A fill:#4472C4,color:#fff,stroke:#2F5597
    style B fill:#ED7D31,color:#fff,stroke:#C55A11
    style C fill:#5B9BD5,color:#fff,stroke:#2E75B6
    style D fill:#70AD47,color:#fff,stroke:#548235
    style E fill:#FFC000,color:#000,stroke:#BF9000
    style F fill:#7030A0,color:#fff,stroke:#5B2D8E
    style G fill:#44546A,color:#fff,stroke:#333F50
```

---

## 2. Layer 1 — Data Platform Architecture (Microsoft Fabric)

This layer covers the end-to-end data lifecycle built on **Microsoft Fabric**, from ingestion through consumption.

### 2.1 Data Sources

| Source | Type | Description |
|--------|------|-------------|
| **JD Edwards** | ERP | Enterprise Resource Planning system |
| **Salesforce** | CRM / SaaS | Customer Relationship Management |
| **Legacy DB** | Database | On-premises / legacy databases |
| **Excel** | Files | Spreadsheet-based data |
| **API** | Service | REST / SOAP API endpoints |
| **Flat Files** | Files | CSV, JSON, XML, etc. |

### 2.2 Ingestion (Layer 1)

```mermaid
graph LR
    subgraph Sources
        JDE["JD Edwards"]
        SF["Salesforce"]
        LDB["Legacy DB"]
        XL["Excel"]
        API["API"]
        FF["Flat Files"]
    end

    subgraph "Ingestion Methods"
        BATCH["🔄 Batch<br/>Fabric Data Pipelines"]
        MIRROR["🪞 Fabric Mirror DB"]
        SHORT["🔗 Fabric Shortcuts"]
        EVT["⚡ Fabric Eventhouse<br/>(Real-Time)"]
    end

    JDE --> BATCH
    SF --> MIRROR
    LDB --> BATCH
    XL --> SHORT
    API --> BATCH
    FF --> SHORT
    JDE --> EVT

    style BATCH fill:#2E75B6,color:#fff
    style MIRROR fill:#2E75B6,color:#fff
    style SHORT fill:#2E75B6,color:#fff
    style EVT fill:#C00000,color:#fff
```

| Method | Use Case | Mode |
|--------|----------|------|
| **Fabric Data Pipelines** | Batch ETL/ELT from ERP, DB, APIs | Batch / Scheduled |
| **Fabric Mirror DB** | Near-real-time database replication (e.g., Salesforce) | CDC / Mirror |
| **Fabric Shortcuts** | Zero-copy references to external storage (Excel, flat files) | On-Demand |
| **Fabric Eventhouse** | Streaming / real-time event ingestion | Real-Time |

### 2.3 Storage & Processing (Layer 2) — Medallion Architecture

```mermaid
graph LR
    subgraph "Medallion Architecture on OneLake"
        LZ["🟤 Landing Zone<br/>Lakehouse"]
        BZ["🟠 Bronze Layer<br/>Lakehouse<br/>(Raw)"]
        SL["⚪ Silver Layer<br/>Lakehouse<br/>(Cleansed)"]
        GL["🟡 Gold Layer<br/>Data Warehouse<br/>(Curated)"]
        AL["💎 Analysis Layer<br/>Semantic Model<br/>(Consumption-Ready)"]
    end

    LZ -->|"Ingest"| BZ
    BZ -->|"Cleanse & Conform"| SL
    SL -->|"Aggregate & Enrich"| GL
    GL -->|"Model & Serve"| AL

    DP["Delta Parquet<br/>OneLake Storage"]

    LZ -.-> DP
    BZ -.-> DP
    SL -.-> DP
    GL -.-> DP

    style LZ fill:#8B4513,color:#fff
    style BZ fill:#CD7F32,color:#fff
    style SL fill:#C0C0C0,color:#000
    style GL fill:#FFD700,color:#000
    style AL fill:#4169E1,color:#fff
    style DP fill:#1B5E20,color:#fff
```

| Layer | Store Type | Format | Purpose |
|-------|-----------|--------|---------|
| **Landing Zone** | Lakehouse | Delta Parquet | Raw ingested data as-is |
| **Bronze** | Lakehouse | Delta Parquet | Immutable raw data with metadata |
| **Silver** | Lakehouse | Delta Parquet | Cleansed, conformed, deduplicated |
| **Gold** | Data Warehouse | Delta Parquet | Business-level aggregates & dimensions |
| **Analysis** | Semantic Model | In-memory | Optimized for BI consumption |

> [!NOTE]
> All layers are stored in **OneLake** using **Delta Parquet** format, enabling unified governance and cross-layer access.

### 2.4 Processing Capabilities

| Capability | Technology | Description |
|-----------|-----------|-------------|
| **Real-Time Analytics** | Kusto Query Database | Streaming analytics and time-series queries |
| **Data Transformation** | Fabric Spark Notebooks | PySpark / SQL-based transformations |
| **Orchestration & Scheduling** | Fabric Pipelines | Workflow orchestration and scheduling |

### 2.5 Agentic AI / Gen AI

```mermaid
graph LR
    UD["📄 Unstructured Data<br/>(SoRs / Files)"]
    P["👁️ Perception"]
    E["🔢 Embedding"]
    LLM["🧠 Planning<br/>(LLM)"]
    AO["🤖 Agent Orchestration"]
    TI["Task Info"]
    CO["Collaborate"]
    AC["⚡ Action"]
    MEM["Memory"]
    WF["Workflow"]

    UD --> P --> E --> LLM --> AO
    AO --> TI
    AO --> CO
    AO --> AC
    AC --> MEM
    AC --> WF

    style LLM fill:#7030A0,color:#fff
    style AO fill:#2E75B6,color:#fff
    style AC fill:#C00000,color:#fff
```

### 2.6 Master Data Management (MDM)

| Step | Description |
|------|-------------|
| **Source Data** | SaaS / Other source systems |
| **Cleanse / DQ** | Data quality and cleansing rules |
| **Deploy Rules** | Apply transformation and matching rules |
| **Publish** | Publish golden master records |

### 2.7 Data Governance (Layer 4)

```mermaid
graph LR
    subgraph "Data Governance Stack"
        MP["Microsoft Purview"]
        TDQ["Technical Data Quality"]
        MD["Metadata"]
        LIN["Lineage"]
        BDQ["Business Data Quality"]
        DD["Data Discovery"]
        BG["Business Glossary"]
    end

    MP --> TDQ
    MP --> MD
    MP --> LIN
    TDQ --> BDQ
    MD --> DD
    DD --> BG

    style MP fill:#0078D4,color:#fff
```

### 2.8 Business Intelligence & Analytical Solutions (Layer 3 — Consumption)

| Solution | Technology | Description |
|----------|-----------|-------------|
| **Business Operational Reporting** | Power BI | Operational dashboards and reports |
| **Data Marketplace** | Fabric | Self-service data catalog for consumers |
| **BI Analytical Reporting** | Power BI | Advanced analytical reports |
| **Self-Service Analytics** | Power BI | User-driven ad-hoc analysis |
| **Agentic BI** | Co-Pilot | AI-powered natural language BI |
| **Data Science Workbench** | Azure AI | ML model development and experimentation |
| **Business Rule Engine** | Custom | Automated business logic execution |

### 2.9 Platform Management & Monitoring (Layer 5)

| Domain | Services |
|--------|----------|
| **Security** | Azure Security Center, Azure Key Vault |
| **Monitoring & Observability** | Azure Log Analytics (Insights), Azure Monitor |
| **Identity & Access Management** | Microsoft Entra ID (formerly Azure AD) |
| **DevOps** | Azure DevOps (CI/CD, Repos, Boards) |
| **FinOps** | Cost Optimization Framework & Reporting |
| **Accelerators** | Tech & Process Accelerator |

---

## 3. Layer 2 — Network Topology (Connectivity Subscription)

The network uses a **Hub-Spoke architecture** with **Azure Virtual WAN** as the hub.

### 3.1 Connectivity Subscription Overview

```mermaid
graph TB
    subgraph "connectivity-sub"
        subgraph "hub-sharednetwork-centralus-rg"
            IPG["🛡️ IP Groups<br/>hub-dns-centralus-vnet-ipg<br/>hub-bastion-centralus-vnet-ipg<br/>onprem-dc-centralus-ipg<br/>identity-adds-centralus-vnet-ipg<br/>mgmt-centralus-vnet-ipg<br/>prod-external-centralus-vnet-ipg<br/>prod-internal-centralus-vnet-ipg<br/>prod-db-centralus-vnet-ipg<br/>prod-datagateway-centralus-vnet-ipg<br/>test-datagateway-centralus-vnet-ipg"]
        end

        subgraph "hub-bastionnetwork-centralus-rg"
            subgraph "hub-bastion-centralus-vnet (10.100.2.0/26)"
                BSUB["AzureBastionSubnet<br/>10.100.2.0/26"]
                PIP["Public IP"]
                BAS["hub-centralus-bas<br/>(Azure Bastion)"]
            end
        end

        subgraph "hub-dnsnetwork-centralus-rg"
            subgraph "hub-dns-centralus-vnet (10.100.2.64/26)"
                DNSIN["hub-centralus-dnspr-in-snet<br/>10.100.2.64/28"]
                DNSOUT["hub-centralus-dnspr-out-snet<br/>10.100.2.80/28"]
            end
        end

        subgraph "hub-dns-centralus-rg"
            DNSZ["🌐 DNS Zones"]
            DNSR["hub-centralus-dnspr<br/>DNS Resolver"]
        end

        VWAN["hub-eastus2-vwan<br/>(Virtual WAN)"]
    end

    DFC["🛡️ Defender for Cloud"]

    BSUB --> PIP --> BAS
    DNSIN -->|"Inbound"| DNSZ
    DNSOUT -->|"Outbound"| DNSR
    DNSR -->|"ipscorp.local → 10.3.3.4/5"| DNSZ

    BSUB -.->|"VNet Peering to VHUB"| VWAN
    DNSIN -.->|"VNet Peering to VHUB"| VWAN

    style VWAN fill:#0078D4,color:#fff
    style DFC fill:#C00000,color:#fff
    style DNSZ fill:#2E75B6,color:#fff
```

### 3.2 Resource Groups in Connectivity Subscription

| Resource Group | Purpose | Key Resources |
|---------------|---------|---------------|
| `hub-sharednetwork-centralus-rg` | Shared network IP groups | IP Groups for all VNets |
| `hub-bastionnetwork-centralus-rg` | Bastion host access | Azure Bastion, Public IP |
| `hub-dnsnetwork-centralus-rg` | DNS resolver network | DNS VNet with inbound/outbound subnets |
| `hub-dns-centralus-rg` | DNS zones & resolver | Private DNS Zones, DNS Resolver |
| `hub-vwan-eastus2-rg` | Virtual WAN hub | vWAN, vHUB, Azure Firewall |

### 3.3 DNS Architecture

| Component | Detail |
|-----------|--------|
| **DNS Resolver** | `hub-centralus-dnspr` |
| **Inbound Endpoint** | `10.100.2.64/28` — receives DNS queries from Azure |
| **Outbound Endpoint** | `10.100.2.80/28` — forwards queries to on-prem |
| **Forwarding Rule** | `ipscorp.local` → `10.3.3.4` / `10.3.3.5` (on-prem DCs) |

---

## 4. Layer 3 — Firewall & Virtual WAN

### 4.1 Virtual WAN & Hub Architecture

```mermaid
graph LR
    INET["☁️ Internet"]

    subgraph "hub-vwan-eastus2-rg"
        VWAN["hub-eastus2-vwan<br/>(Azure Virtual WAN)"]

        subgraph "hub-centralus-vhub (10.100.0.0/23)"
            VHUB["Virtual Hub"]
            PIP2["Public IP (x.x.x.x)"]
            AFW["🔥 hub-centralus-afw<br/>Azure Firewall<br/>10.100.0.x"]
            VPN["🔒 Virtual WAN<br/>VPN Gateway"]
        end
    end

    AFWP["📋 hub-centralus-afwp<br/>(Firewall Policy)"]

    INET -->|"Internet Ingress"| PIP2
    PIP2 -->|"Internet Egress"| INET
    PIP2 --> AFW
    AFW --> AFWP
    VHUB --> VPN

    style AFW fill:#C00000,color:#fff
    style VWAN fill:#0078D4,color:#fff
    style VPN fill:#2E75B6,color:#fff
```

### 4.2 Azure Firewall Policy — Network Rules

| # | Action | Source | Destination | Port | Protocol |
|---|--------|--------|-------------|------|----------|
| 1 | **Allow** | Azure Vnets | AzureCloud | Any | Any |
| 2 | **Allow** | All DC's, Azure Vnets | DNS Resolver Vnet | 53 | TCP/UDP |
| 3 | **Allow** | All DC's | All DC's | Any | Any |
| 4 | **Allow** | Azure Vnets, On-prem IPs | All DC's | AD | TCP/UDP |
| 5 | **Allow** | DNS Resolver | ADCS Vnet, On-prem DC's | 53 | TCP/UDP |
| 6 | **Allow** | Azure Prod Vnets | Azure Prod Vnets | Any | Any |
| 7 | **Allow** | Bastion Vnet | Azure Vnets | 3389, 22 | TCP |
| 8 | **Allow** | Prod Data Gateway VNET | TBD Data Sources | TBD | TCP |
| 9 | **Allow** | Test Data Gateway VNET | TBD Data Sources | TBD | TCP |

### 4.3 Azure Firewall Policy — Application Rules

| # | Action | Source | Destination | Protocol |
|---|--------|--------|-------------|----------|
| 1 | **Allow** | Azure Vnets | Business Use | HTTP, HTTPS |
| 2 | **Allow** | Azure Vnets | Office365 FQDN Tags | HTTPS |

### 4.4 DNAT Rules

> [!NOTE]
> No DNAT rules are currently configured.

---

## 5. Layer 4 — Production Subscription & Workloads

### 5.1 Production Subscription Overview

```mermaid
graph TB
    subgraph "production-sub"
        MG["🏛️ production-mg<br/>(Management Group)"]
        POL["📜 Policy"]

        subgraph "prod-externalnetwork-centralus-rg"
            subgraph "prod-external-centralus-vnet (10.100.4.0/23)"
                EXTSNET["prod-external-centralus-snet<br/>10.100.4.0/24"]
            end
        end

        subgraph "prod-backup-centralus-rg"
            BACKUP["☁️ Azure Backup<br/>prod-backup-centralus-rsv"]
        end

        subgraph "prod-internalnetwork-centralus-rg"
            subgraph "prod-internal-centralus-vnet (10.100.6.0/24)"
                INTSNET["prod-internal-centralus-snet<br/>10.100.6.0/24"]
            end
        end

        subgraph "prod-dbnetwork-centralus-rg"
            subgraph "prod-db-centralus-vnet (10.100.7.0/24)"
                DB1["prod-db1-centralus-snet<br/>10.100.7.0/25"]
                DB2["prod-db2-centralus-snet<br/>10.100.7.128/25"]
            end
        end

        subgraph "prod-datagateway-centralus-rg"
            subgraph "prod-datagateway-centralus-vnet (10.100.8.0/24)"
                DGW["prod-datagateway-centralus-snet<br/>10.100.8.0/25"]
            end
        end
    end

    DFC2["🛡️ Defender for Cloud"]

    MG --> POL
    EXTSNET -.->|"VNet Peering"| VHUB["Virtual Hub"]
    INTSNET -.->|"VNet Peering"| VHUB
    DB1 -.->|"VNet Peering"| VHUB
    DGW -.->|"VNet Peering"| VHUB

    style MG fill:#0078D4,color:#fff
    style BACKUP fill:#2E75B6,color:#fff
    style DFC2 fill:#C00000,color:#fff
```

### 5.2 Production Resource Groups

| Resource Group | VNet | CIDR | Purpose |
|---------------|------|------|---------|
| `prod-externalnetwork-centralus-rg` | `prod-external-centralus-vnet` | `10.100.4.0/23` | External-facing workloads |
| `prod-internalnetwork-centralus-rg` | `prod-internal-centralus-vnet` | `10.100.6.0/24` | Internal application workloads |
| `prod-dbnetwork-centralus-rg` | `prod-db-centralus-vnet` | `10.100.7.0/24` | Database tier (2 subnets) |
| `prod-datagateway-centralus-rg` | `prod-datagateway-centralus-vnet` | `10.100.8.0/24` | Data gateway for Fabric connectivity |
| `prod-backup-centralus-rg` | — | — | Azure Backup Recovery Services Vault |

---

## 6. Layer 5 — Database & Data Gateway Networks

### 6.1 Database Network

```mermaid
graph TB
    subgraph "prod-dbnetwork-centralus-rg"
        subgraph "prod-db-centralus-vnet (10.100.7.0/24)"
            DB1S["🗄️ prod-db1-centralus-snet<br/>10.100.7.0/25<br/>(128 IPs)"]
            DB2S["🗄️ prod-db2-centralus-snet<br/>10.100.7.128/25<br/>(128 IPs)"]
        end
    end

    subgraph "prod-datagateway-centralus-rg"
        subgraph "prod-datagateway-centralus-vnet (10.100.8.0/24)"
            DGWS["🔌 prod-datagateway-centralus-snet<br/>10.100.8.0/25<br/>(128 IPs)"]
        end
    end

    DGWS -->|"Connects to on-prem<br/>& cloud data sources"| DB1S
    DGWS --> DB2S

    style DB1S fill:#2E75B6,color:#fff
    style DB2S fill:#2E75B6,color:#fff
    style DGWS fill:#ED7D31,color:#fff
```

> [!IMPORTANT]
> The **Data Gateway VNet** (`10.100.8.0/24`) enables **Microsoft Fabric** to securely connect to on-premises and private network data sources through the Azure Firewall.

---

## 7. IP Address Plan

### 7.1 Complete CIDR Allocation

| VNet | CIDR | Subnet(s) | Subscription | Purpose |
|------|------|-----------|-------------|---------|
| `hub-centralus-vhub` | `10.100.0.0/23` | Virtual Hub | Connectivity | vWAN Hub + Firewall |
| `hub-bastion-centralus-vnet` | `10.100.2.0/26` | `10.100.2.0/26` | Connectivity | Azure Bastion |
| `hub-dns-centralus-vnet` | `10.100.2.64/26` | `10.100.2.64/28`, `10.100.2.80/28` | Connectivity | DNS Resolver |
| `prod-external-centralus-vnet` | `10.100.4.0/23` | `10.100.4.0/24` | Production | External workloads |
| `prod-internal-centralus-vnet` | `10.100.6.0/24` | `10.100.6.0/24` | Production | Internal workloads |
| `prod-db-centralus-vnet` | `10.100.7.0/24` | `10.100.7.0/25`, `10.100.7.128/25` | Production | Database tier |
| `prod-datagateway-centralus-vnet` | `10.100.8.0/24` | `10.100.8.0/25` | Production | Data Gateway |

### 7.2 Address Space Visualization

```
10.100.0.0/16 (Supernet)
├── 10.100.0.0/23   → Virtual Hub (vWAN)
├── 10.100.2.0/26   → Bastion
├── 10.100.2.64/26  → DNS Resolver
├── 10.100.4.0/23   → Prod External
├── 10.100.6.0/24   → Prod Internal
├── 10.100.7.0/24   → Prod Database
└── 10.100.8.0/24   → Prod Data Gateway

On-Premises DNS:
└── 10.3.3.4/5      → On-prem Domain Controllers (ipscorp.local)
```

---

## 8. Security & Governance Summary

### 8.1 Security Controls

```mermaid
graph TB
    subgraph "Security Layers"
        DFC["🛡️ Microsoft Defender for Cloud"]
        AFW["🔥 Azure Firewall<br/>(Centralized inspection)"]
        NSG["🔒 Network Security Groups<br/>(Per subnet)"]
        ENTRA["🔐 Microsoft Entra ID<br/>(Identity & RBAC)"]
        KV["🔑 Azure Key Vault<br/>(Secrets & Certificates)"]
        POL["📜 Azure Policy<br/>(Governance guardrails)"]
        PV["📋 Microsoft Purview<br/>(Data Governance)"]
    end

    DFC --> AFW --> NSG
    ENTRA --> KV
    POL --> PV

    style DFC fill:#C00000,color:#fff
    style AFW fill:#ED7D31,color:#fff
    style ENTRA fill:#0078D4,color:#fff
```

### 8.2 Network Security Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Zero Trust** | All traffic inspected through centralized Azure Firewall |
| **Least Privilege** | IP Groups + firewall rules scope access per VNet |
| **Segmentation** | Separate VNets for external, internal, DB, and gateway workloads |
| **Secure Remote Access** | Azure Bastion (no public RDP/SSH exposure) |
| **Hybrid DNS** | Private DNS resolver with conditional forwarding to on-prem |
| **Centralized Logging** | Azure Monitor + Log Analytics |
| **Backup & DR** | Azure Backup Recovery Services Vault |

### 8.3 Governance Stack

| Domain | Tool | Scope |
|--------|------|-------|
| **Data Governance** | Microsoft Purview | Metadata, lineage, data discovery, business glossary |
| **Data Quality** | Purview + Custom | Technical DQ + business DQ rules |
| **Identity** | Microsoft Entra ID | SSO, RBAC, conditional access |
| **Policy** | Azure Policy | Subscription-level compliance guardrails |
| **Cost Management** | FinOps Framework | Cost optimization & reporting |
| **DevOps** | Azure DevOps | CI/CD pipelines, source control, boards |

---

> [!TIP]
> **Next Steps to Consider:**
> - Define NSG rules for each production subnet
> - Complete the TBD firewall rules for Data Gateway sources
> - Implement Azure Private Endpoints for Fabric ↔ Data Gateway connectivity
> - Set up Azure Monitor workbooks for network flow analytics
> - Define disaster recovery strategy across regions (currently Central US only)
