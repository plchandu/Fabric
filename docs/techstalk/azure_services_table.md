|  # | Layer                   | Azure / Microsoft Service                    | Purpose in This Project                                                                                              | Source / Target                        |
| -: | ----------------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
|  1 | **Analytics Platform**  | **Microsoft Fabric**                         | Central analytics platform; hosts Lakehouses, OneLake, notebooks, pipelines, semantic models and analytics workloads | Salesforce, JDE, SQL Server → Fabric   |
|  2 | **Storage**             | **Microsoft OneLake**                        | Centralized enterprise data lake for Bronze, Silver and Gold data                                                    | All source systems → OneLake           |
|  3 | **Data Ingestion**      | **Fabric Data Factory**                      | Orchestrates ingestion, transformation pipelines, scheduling and incremental loads                                   | Salesforce/JDE/SQL Server → OneLake    |
|  4 | **CRM Integration**     | **Salesforce Connectors / APIs**             | Extract Salesforce Accounts, Contacts, Opportunities, Cases, etc.                                                    | Salesforce → Fabric                    |
|  5 | **ERP Integration**     | **On-premises Data Gateway**                 | Secure connectivity from Fabric to on-premises JDE/AS400 DB2 and SQL Server                                          | JDE/SQL Server → Fabric                |
|  6 | **Compute**             | **Azure Virtual Machines**                   | Hosts the On-premises Data Gateway and required IBM i/DB2 connectivity components                                    | Gateway infrastructure                 |
|  7 | **Network**             | **Azure Virtual Network (VNet)**             | Provides private network isolation for gateway and supporting Azure infrastructure                                   | Azure infrastructure                   |
|  8 | **Network**             | **Azure VPN Gateway**                        | Secure site-to-site connectivity between Azure and on-premises data center when required                             | Azure ↔ On-premises                    |
|  9 | **Network**             | **Azure Virtual WAN / vHub**                 | Enterprise hub-and-spoke connectivity and centralized routing for large hybrid environments                          | Azure ↔ On-premises/VNets              |
| 10 | **Network Security**    | **Azure Firewall**                           | Centralized traffic inspection and network security policies                                                         | Azure/VNet traffic                     |
| 11 | **DNS**                 | **Azure Private DNS / Private DNS Resolver** | Private DNS resolution between Azure and on-premises environments                                                    | Azure ↔ On-premises                    |
| 12 | **Administration**      | **Azure Bastion**                            | Secure RDP/SSH access to gateway VMs without exposing public IPs                                                     | Admin → Azure VM                       |
| 13 | **Secrets**             | **Azure Key Vault**                          | Stores database credentials, secrets, certificates and keys                                                          | Applications/Pipelines                 |
| 14 | **Identity**            | **Microsoft Entra ID**                       | Authentication, SSO, MFA, RBAC and identity management                                                               | Users/Services → Fabric/Azure          |
| 15 | **Security**            | **Microsoft Defender for Cloud**             | Security posture management, vulnerability assessment and recommendations                                            | Azure environment                      |
| 16 | **Governance**          | **Azure Policy**                             | Enforces organizational security, compliance and resource standards                                                  | Azure resources                        |
| 17 | **Data Governance**     | **Microsoft Purview**                        | Data catalog, discovery, lineage, classification and business glossary                                               | Sources → Fabric → Power BI            |
| 18 | **Monitoring**          | **Azure Monitor**                            | Infrastructure and application monitoring                                                                            | Azure/Fabric supporting infrastructure |
| 19 | **Logging**             | **Log Analytics**                            | Centralized operational and diagnostic logs                                                                          | Azure services/VMs                     |
| 20 | **Automation**          | **Azure Automation**                         | Runbooks for operational automation, including scheduled capacity operations where appropriate                       | Azure/Fabric operations                |
| 21 | **Workflow Automation** | **Azure Logic Apps**                         | Event-driven notifications and integration workflows                                                                 | Monitoring/Operations                  |
| 22 | **Backup**              | **Azure Backup**                             | Backup/recovery for gateway VMs and supporting Azure infrastructure                                                  | Azure VMs                              |
| 23 | **BI / Reporting**      | **Power BI**                                 | Replaces/modernizes Cognos reporting and provides dashboards and semantic models                                     | Fabric Gold → Power BI                 |
| 24 | **Analytics Compute**   | **Fabric Spark / PySpark**                   | Data cleansing, transformation, enrichment and complex processing                                                    | Bronze → Silver → Gold                 |
| 25 | **Analytics SQL**       | **Fabric SQL / Warehouse**                   | SQL-based transformation and serving layer where appropriate                                                         | Silver/Gold                            |
| 26 | **Data Sharing**        | **OneLake Shortcuts**                        | Provides access to external ADLS Gen2 data without unnecessary data duplication                                      | ADLS Gen2 → OneLake                    |
| 27 | **External Storage**    | **Azure Data Lake Storage Gen2**             | Optional external landing/archive/data lake when organizational requirements require ADLS                            | On-prem/API → ADLS                     |
| 28 | **Capacity Management** | **Microsoft Fabric Capacity**                | Provides compute capacity for Fabric workloads                                                                       | Fabric workloads                       |


| Business Requirement             | Primary Service                                    |
| -------------------------------- | -------------------------------------------------- |
| Extract Salesforce data          | **Fabric Data Factory + Salesforce connector/API** |
| Extract JDE/AS400 data           | **Fabric Data Factory + On-premises Data Gateway** |
| Extract SQL Server data          | **Fabric Data Factory + On-premises Data Gateway** |
| Store raw data                   | **Fabric OneLake**                                 |
| Create Bronze/Silver/Gold layers | **Fabric Lakehouse + OneLake**                     |
| Transform large datasets         | **Fabric Spark / PySpark**                         |
| SQL-based transformations        | **Fabric SQL / Warehouse**                         |
| Implement incremental loads      | **Fabric Data Factory + source CDC/watermarks**    |
| Manage pipeline metadata         | **Fabric/OneLake metadata tables**                 |
| Enterprise data catalog          | **Microsoft Purview**                              |
| Data lineage                     | **Microsoft Purview**                              |
| User authentication              | **Microsoft Entra ID**                             |
| Store secrets                    | **Azure Key Vault**                                |
| Hybrid network connectivity      | **VPN Gateway / ExpressRoute / vWAN**              |
| Network security                 | **Azure Firewall**                                 |
| Gateway VM administration        | **Azure Bastion**                                  |
| Infrastructure monitoring        | **Azure Monitor + Log Analytics**                  |
| VM backup                        | **Azure Backup**                                   |
| Security posture                 | **Defender for Cloud + Azure Policy**              |
| Business reporting               | **Power BI + Fabric Semantic Model**               |
| Replace Cognos                   | **Power BI**                                       |
