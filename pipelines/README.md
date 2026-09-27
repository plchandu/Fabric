# Microsoft Fabric Pipelines Catalog

This directory contains the declarative **Microsoft Fabric Data Factory Pipeline definitions** (`pipeline-content.json`) for the **IPS BI Modernization project**.

In accordance with Microsoft Fabric Git integration standards, each pipeline is serialized as a declarative JSON file defining parameters, variables, activity DAGs, dependency conditions, and execution settings.

---

## Pipeline Catalog Summary

| Pipeline Directory | Pipeline Name | Ingestion / Orchestration Mode | Schedule / Trigger | Primary Function |
| :--- | :--- | :--- | :--- | :--- |
| [`pl_master_batch_orchestrator/`](file:///Users/chandu/Documents/Python_practice/Fabric/pipelines/pl_master_batch_orchestrator/pipeline-content.json) | `pl_master_batch_orchestrator` | **Batch Orchestrator** | Twice Daily (`09:00` & `17:00` CET) | Orchestrates **58 AS400 DB2 tables** across Dimensions (full load) and Facts (watermark incremental), followed by Silver DQ and Gold star schema modeling. |
| [`pl_master_nrt_orchestrator/`](file:///Users/chandu/Documents/Python_practice/Fabric/pipelines/pl_master_nrt_orchestrator/pipeline-content.json) | `pl_master_nrt_orchestrator` | **Near Real-Time (NRT)** | Continuous (`Every 5-10 Mins`) | Coordinates micro-batch CDC delta merges for **39 high-frequency tables** from Fivetran into Bronze, Silver, and Gold within a 15-minute SLA. |
| [`pl_ingest_group/`](file:///Users/chandu/Documents/Python_practice/Fabric/pipelines/pl_ingest_group/pipeline-content.json) | `pl_ingest_group` | **Metadata Worker** | Child Pipeline (Invoked by Master) | Queries `sqldb-meta-orch-dev` for datasets matching `group_code`, executes parallel Copy Activities across the On-Premises Data Gateway (OPDG), and logs metrics. |
| [`pl_ingest_bronze_flat_files/`](file:///Users/chandu/Documents/Python_practice/Fabric/pipelines/pl_ingest_bronze_flat_files/pipeline-content.json) | `pl_ingest_bronze_flat_files` | **Event-Driven (EDAI)** | Reactive (`OneLake BlobCreated`) | Invoked dynamically by Data Activator (Reflex) when a user uploads `.csv` files to `Files/FlatFile_Repo/`. Runs `nb_bronze_flat_file_ingestion` and archives processed files. |
| [`pl_sync_metadata_catalog/`](file:///Users/chandu/Documents/Python_practice/Fabric/pipelines/pl_sync_metadata_catalog/pipeline-content.json) | `pl_sync_metadata_catalog` | **Governance / Framework** | On-Demand / File Drop | Ingests `Ingestion_metadata_load_template.xlsx` from OneLake, validates definitions, and populates `meta.*` tables in `sqldb-meta-orch-dev`. |

---

## Directory Layout

```
pipelines/
├── README.md                                             # This catalog guide
├── pl_master_batch_orchestrator/
│   └── pipeline-content.json                            # Master batch orchestrator DAG
├── pl_master_nrt_orchestrator/
│   └── pipeline-content.json                            # Master NRT CDC micro-batch DAG
├── pl_ingest_group/
│   └── pipeline-content.json                            # Dynamic metadata-driven worker DAG
├── pl_ingest_bronze_flat_files/
│   └── pipeline-content.json                            # Event-driven flat file ingestion DAG
└── pl_sync_metadata_catalog/
    └── pipeline-content.json                            # Metadata catalog synchronization DAG
```

---

## Deployment & CI/CD
These pipeline definitions are deployed into Microsoft Fabric shared workspaces via the automated deployment scripts in `deployment/`:
* Pull Request validation: `.github/workflows/ci-validate.yml`
* Continuous Deployment: `.github/workflows/deploy-fabric.yml`
* Manual / Local simulation: `python deployment/deploy_workspace.py --environment PROD --dry-run`
