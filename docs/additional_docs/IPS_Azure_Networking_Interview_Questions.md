# IPS Corporation — Azure Networking Technical Interview Guide (Basic to Advanced)

> **Project:** Enterprise Cloud Modernization (IBM AS400 DB2 ERP $\rightarrow$ Microsoft Fabric)  
> **Domain:** Hybrid Cloud Networking, Azure Virtual WAN, Network Security, Gateway Topology & Private Connectivity  
> **Target Audience:** Cloud Engineers, Network Architects, Data Engineers & Azure Infrastructure Specialists  
> **Document Location:** `docs/additional_docs/IPS_Azure_Networking_Interview_Questions.md`  

---

## 📋 Table of Contents
1. [Overview & Networking Architecture Summary](#1-overview--networking-architecture-summary)
2. [Level 1: Foundational & Basic Questions](#2-level-1-foundational--basic-questions)
   - [Q1.1: Why do we need hybrid Azure networking when Microsoft Fabric is a SaaS platform?](#q11-why-do-we-need-hybrid-azure-networking-when-microsoft-fabric-is-a-saas-platform)
   - [Q1.2: What is the IP addressing and CIDR supernet scheme designed for this project?](#q12-what-is-the-ip-addressing-and-cidr-supernet-scheme-designed-for-this-project)
   - [Q1.3: How does the On-Premises Data Gateway (OPDG) connect cloud pipelines to AS400 without inbound firewall ports?](#q13-how-does-the-on-premises-data-gateway-opdg-connect-cloud-pipelines-to-as400-without-inbound-firewall-ports)
   - [Q1.4: What is the difference between an Azure Network Security Group (NSG) and Azure Firewall in this architecture?](#q14-what-is-the-difference-between-an-azure-network-security-group-nsg-and-azure-firewall-in-this-architecture)
   - [Q1.5: What ports are required to establish an ODBC connection from the Gateway VM to IBM AS400 DB2?](#q15-what-ports-are-required-to-establish-an-odbc-connection-from-the-gateway-vm-to-ibm-as400-db2)
3. [Level 2: Intermediate Questions (Architecture, Protocols & Gateway Deep Dive)](#3-level-2-intermediate-questions-architecture-protocols--gateway-deep-dive)
   - [Q2.1: Why was Azure Virtual WAN (vWAN) selected over traditional hub-and-spoke VNet peering?](#q21-why-was-azure-virtual-wan-vwan-selected-over-traditional-hub-and-spoke-vnet-peering)
   - [Q2.2: Explain the technical mechanics of the Azure Service Bus Reverse-Relay used by the Gateway.](#q22-explain-the-technical-mechanics-of-the-azure-service-bus-reverse-relay-used-by-the-gateway)
   - [Q2.3: How does the Azure Private DNS Resolver resolve hybrid hostnames like `ipscorp.local`?](#q23-how-does-the-azure-private-dns-resolver-resolve-hybrid-hostnames-like-ipscorplocal)
   - [Q2.4: How does Azure Bastion provide secure administrative access to the Gateway VM with zero public IPs?](#q24-how-does-azure-bastion-provide-secure-administrative-access-to-the-gateway-vm-with-zero-public-ips)
   - [Q2.5: What are Azure Private Endpoints (Private Link), and how do they secure Azure Key Vault in this project?](#q25-what-are-azure-private-endpoints-private-link-and-how-do-they-secure-azure-key-vault-in-this-project)
   - [Q2.6: What is the On-Premises Data Gateway "Spooling Directory", and how is it tuned to prevent disk saturation?](#q26-what-is-the-on-premises-data-gateway-spooling-directory-and-how-is-it-tuned-to-prevent-disk-saturation)
4. [Level 3: Advanced & Architectural Questions (Routing, High Availability, Security & Sizing)](#4-level-3-advanced--architectural-questions-routing-high-availability-security--sizing)
   - [Q3.1: Trace the complete end-to-end packet flow when a Fabric pipeline extracts 5 million records from AS400 table F0911.](#q31-trace-the-complete-end-to-end-packet-flow-when-a-fabric-pipeline-extracts-5-million-records-from-as400-table-f0911)
   - [Q3.2: How do Virtual Hub Route Tables and UDRs enforce centralized stateful packet inspection through Azure Firewall?](#q32-how-do-virtual-hub-route-tables-and-udrs-enforce-centralized-stateful-packet-inspection-through-azure-firewall)
   - [Q3.3: How do you design high availability (HA) and load balancing for the On-Premises Data Gateway?](#q33-how-do-you-design-high-availability-ha-and-load-balancing-for-the-on-premises-data-gateway)
   - [Q3.4: Fabric Managed VNet Gateway vs. On-Premises Data Gateway: Why did this project choose OPDG?](#q34-fabric-managed-vnet-gateway-vs-on-premises-data-gateway-why-did-this-project-choose-opdg)
   - [Q3.5: How do you mitigate MTU size mismatches and TCP packet fragmentation across the IPsec Site-to-Site VPN tunnel?](#q35-how-do-you-mitigate-mtu-size-mismatches-and-tcp-packet-fragmentation-across-the-ipsec-site-to-site-vpn-tunnel)
   - [Q3.6: How do you detect and troubleshoot network latency spikes and connection drops between the Gateway and AS400?](#q36-how-do-you-detect-and-troubleshoot-network-latency-spikes-and-connection-drops-between-the-gateway-and-as400)
5. [Real-World Scenario-Based Network Troubleshooting](#5-real-world-scenario-based-network-troubleshooting)

---

## 1. Overview & Networking Architecture Summary

```mermaid
graph TB
    subgraph ONPREM["CLIENT ON-PREMISES DATACENTER"]
        AS400["🖥️ IBM AS400 DB2 (10.242.2.25)<br/>Ports: 446 (DRDA), 449, 8471, 9471"]
        DC["🌐 Active Directory DCs (10.3.3.4, 10.3.3.5)<br/>ipscorp.local"]
        ROUTER["🔒 Edge VPN Router"]
        AS400 <--> DC
        AS400 <--> ROUTER
    end

    subgraph TRANSIT["HYBRID ENCRYPTED TRANSIT"]
        VPN["🔐 IPsec Site-to-Site VPN / ExpressRoute"]
        RELAY["⚡ Azure Service Bus Relay<br/>(Outbound TLS 443)"]
    end

    subgraph HUB["AZURE CONNECTIVITY HUB (South India / Central India)"]
        VWAN["🌐 Azure Virtual WAN (hub-centralindia-vwan)"]
        VHUB["🏢 Virtual Hub (10.100.0.0/23)"]
        AFW["🔥 Azure Firewall Standard (hub-southindia-afw)"]
        BASTION["🛡️ Azure Bastion (hub-southindia-bas: 10.100.2.0/26)"]
        DNS_PR["📡 Private DNS Resolver (10.100.2.64/28)"]
        
        VWAN --- VHUB
        VHUB <--> AFW
        VHUB <--> BASTION
        VHUB <--> DNS_PR
    end

    subgraph SPOKE["SPOKE WORKLOADS VNET (10.100.8.0/24)"]
        GW_VM["🖥️ Gateway VM: genie-fabric-prod-01 (10.100.8.10)<br/>Windows Server 2022 · 64-bit IBM ACS ODBC"]
        NSG["🔒 Gateway NSG<br/>Allow Inbound 3389 from Bastion | Deny Internet"]
        KV["🔑 Azure Key Vault (ipskv-prod-chennai-01)"]
        GW_VM --- NSG
    end

    subgraph FABRIC["MICROSOFT FABRIC SAAS PLANE"]
        FDF["Data Factory Pipelines"]
        ONELAKE["OneLake (Bronze -> Silver -> Gold)"]
        PBI["Power BI Direct Lake"]
        FDF --> ONELAKE --> PBI
    end

    ROUTER <==> VPN <==> VHUB
    GW_VM ==>"Outbound TLS 443"==> RELAY ==>"Control Link"==> FDF
    GW_VM -->|"ODBC 446/8471 via Firewall"| AFW -->|"Route to On-Prem"| AS400
    GW_VM -->|"Resolve ipscorp.local"| DNS_PR -->|"DNS Port 53"| DC
    BASTION -->|"Private RDP 3389"| GW_VM
    FDF -.->|"Fetch DB Secrets"| KV
```

---

## 2. Level 1: Foundational & Basic Questions

### Q1.1: Why do we need hybrid Azure networking when Microsoft Fabric is a SaaS platform?
* **What Interviewers Look For:** Understanding of SaaS multi-tenancy vs. private enterprise boundaries.
* **Model Answer:**
  * Microsoft Fabric is a multi-tenant Software-as-a-Service (SaaS) cloud platform hosted within Microsoft's managed cloud infrastructure.
  * Our transactional ERP core—**IBM AS400 DB2**—resides inside a private, on-premises enterprise datacenter behind strict corporate firewalls with no public internet routing.
  * Without a secure hybrid networking bridge (Azure Virtual WAN, Azure Firewall, and an On-Premises Data Gateway), Fabric cannot reach private on-premises IP addresses (`10.242.2.25`) to extract batch datasets. The networking architecture provides a secure, encrypted, authenticated, and isolated transit backbone between on-premises and Fabric OneLake.

---

### Q1.2: What is the IP addressing and CIDR supernet scheme designed for this project?
* **What Interviewers Look For:** Subnetting fundamentals, CIDR allocation, avoidance of IP collisions.
* **Model Answer:**
  * To avoid IP overlap between on-premises (`10.242.0.0/16` and `10.3.0.0/16`) and Azure, a dedicated **Azure Supernet** was allocated: `10.100.0.0/16` (65,536 addresses).
  * **Subnet Allocations:**
    * `10.100.0.0/23` (512 IPs): Azure Virtual WAN Hub (`hub-southindia-vhub`).
    * `10.100.1.0/26` (64 IPs): Azure Firewall Subnet (`AzureFirewallSubnet`).
    * `10.100.2.0/26` (64 IPs): Azure Bastion Host Subnet (`AzureBastionSubnet`).
    * `10.100.2.64/28` (16 IPs): Private DNS Resolver Inbound Subnet.
    * `10.100.2.80/28` (16 IPs): Private DNS Resolver Outbound Subnet.
    * `10.100.8.0/24` (256 IPs): Spoke Gateway VNet (`genie-fabric-prod-01` VM assigned static private IP `10.100.8.10`).
    * `10.100.7.0/24` (256 IPs): Reserved for Database Workloads.

---

### Q1.3: How does the On-Premises Data Gateway (OPDG) connect cloud pipelines to AS400 without inbound firewall ports?
* **What Interviewers Look For:** Reverse-relay architecture, outbound WebSocket mechanics, and perimeter security.
* **Model Answer:**
  * Opening inbound firewall ports into a corporate datacenter violates enterprise security standards because it exposes internal networks to port scanning and denial-of-service attacks.
  * The **On-Premises Data Gateway** resolves this using an **Outbound Reverse-Relay Architecture**:
    1. During boot, the Gateway service (`PBIEgwService`) on VM `10.100.8.10` opens an outbound persistent WebSocket/HTTPS connection over **TCP 443** to the Azure Service Bus relay in the cloud.
    2. When a Fabric Data Factory pipeline initiates a Copy Activity, it places the request onto the Azure Relay channel.
    3. The Gateway pulls the request down over its existing outbound channel, issues the query internally to the AS400 DB2 host over local ODBC ports, compresses and encrypts the extracted payload, and streams the data outbound back to OneLake over TLS 443.
    4. **Result:** Zero public IPs and zero inbound firewall ports are opened into the on-premises environment.

---

### Q1.4: What is the difference between an Azure Network Security Group (NSG) and Azure Firewall in this architecture?
* **What Interviewers Look For:** Layer 4 packet filtering vs. Layer 7 stateful inspection and centralized governance.
* **Model Answer:**
  * **Network Security Group (NSG):**
    * Operates at **Layer 4 (Transport Layer)**.
    * Applies basic stateless/stateful 5-tuple filtering rules (Source IP, Source Port, Destination IP, Destination Port, Protocol) directly at the Virtual Machine Network Interface Card (NIC) or subnet level.
    * In our project, `nsg-gateway` is used locally to permit RDP traffic exclusively from the Bastion subnet (`10.100.2.0/26`) and block all inbound internet.
  * **Azure Firewall Standard (`hub-southindia-afw`):**
    * A fully managed, cloud-native **Layer 3 to Layer 7 stateful firewall**.
    * Provides centralized network routing, Threat Intelligence filtering, FQDN application rules, and deep packet inspection.
    * All hybrid traffic between the Gateway Spoke (`10.100.8.0/24`) and on-premises AS400 (`10.242.2.25`) is routed through Azure Firewall to log connection attempts and prevent lateral threat movement.

---

### Q1.5: What ports are required to establish an ODBC connection from the Gateway VM to IBM AS400 DB2?
* **What Interviewers Look For:** Knowledge of IBM iSeries / AS400 DB2 communication daemons.
* **Model Answer:**
  * The Gateway VM uses the official **64-bit IBM i Access Client Solutions (ACS) ODBC Driver**.
  * To connect to AS400 DB2 (`10.242.2.25`), the following internal TCP ports must be allowed through the corporate firewall:
    * **Port 449:** As-Host Server Port Mapper daemon (resolves database services).
    * **Port 8471 / 9471:** IBM i Database Server (8471 unencrypted / 9471 SSL/TLS).
    * **Port 446:** Distributed Relational Database Architecture (DRDA) service.
    * **Port 6017:** IBM DB2 UDB relational database connection daemon.
  * *Security standard:* These ports are restricted strictly between Gateway VM `10.100.8.10` and AS400 host `10.242.2.25`. They are never exposed outside the internal corporate network.

---

## 3. Level 2: Intermediate Questions (Architecture, Protocols & Gateway Deep Dive)

### Q2.1: Why was Azure Virtual WAN (vWAN) selected over traditional hub-and-spoke VNet peering?
* **What Interviewers Look For:** Scalability, automated transit routing, operational complexity trade-offs.
* **Model Answer:**
  * **Traditional VNet Peering Limitations:** In standard hub-and-spoke architectures, spoke VNets cannot transitively communicate through each other or to on-premises without manual User-Defined Routes (UDRs) and complex Network Virtual Appliances (NVAs). Maintaining route tables across dozens of subnets becomes error-prone and brittle.
  * **Why Azure Virtual WAN:**
    1. **Automated Transit Routing:** vWAN automatically configures branch-to-VNet and VNet-to-VNet routing through the managed Virtual Hub (`hub-southindia-vhub`).
    2. **Built-in Scale & Gateway Integration:** Provides built-in VPN/ExpressRoute gateways with up to 20 Gbps throughput without provisioning separate GatewaySubnets.
    3. **Single Pane of Glass:** Integrates Azure Firewall, VPN connections, and spoke attachments into a unified management interface.

---

### Q2.2: Explain the technical mechanics of the Azure Service Bus Reverse-Relay used by the Gateway.
* **What Interviewers Look For:** WebSocket handshakes, Azure Relay endpoints, and proxy communication.
* **Model Answer:**
  * The On-Premises Data Gateway uses the **Azure Relay** infrastructure:
    1. Upon startup, the gateway performs DNS discovery against Azure endpoints (`*.servicebus.windows.net`, `*.frontend.clouddatahub.net`).
    2. It initiates an outbound TLS handshake over port 443. The firewall approves the connection as standard outbound web traffic.
    3. The connection upgrades to a persistent **WebSocket control channel**.
    4. When a pipeline triggers, Fabric dispatches a job packet to the Relay.
    5. The gateway receives the query via the open WebSocket, authenticates via encrypted credentials passed in the payload, executes the query against AS400, and streams chunks back across the WebSocket connection into OneLake.

---

### Q2.3: How does the Azure Private DNS Resolver resolve hybrid hostnames like `ipscorp.local`?
* **What Interviewers Look For:** Split-brain DNS resolution, conditional forwarding rulesets, and DNS proxying.
* **Model Answer:**
  * The Gateway VM in Azure needs to communicate with on-premises resources using fully qualified domain names (e.g., `as400.ipscorp.local`) rather than hardcoded IP addresses.
  * Azure default DNS (`168.63.129.16`) cannot resolve private on-premises Active Directory domains (`ipscorp.local`).
  * **Azure Private DNS Resolver Architecture (`hub-southindia-dnspr`):**
    * **Inbound Endpoint (`10.100.2.64/28`):** Allows on-premises clients to query Azure Private DNS Zones.
    * **Outbound Endpoint (`10.100.2.80/28`):** Configured with a **DNS Forwarding Ruleset**:
      * Domain rule: Any query for `*.ipscorp.local` is conditionally forwarded across the vWAN/VPN tunnel to on-premises Domain Controllers (`10.3.3.4` and `10.3.3.5`) on port 53.
    * **Advantage:** Eliminates the overhead of deploying and patching legacy IaaS Windows DNS forwarder VMs.

---

### Q2.4: How does Azure Bastion provide secure administrative access to the Gateway VM with zero public IPs?
* **What Interviewers Look For:** Protecting management planes (RDP/SSH), eliminating jump-box exposure.
* **Model Answer:**
  * Exposing RDP port 3389 to the public internet attracts brute-force attacks and port scans.
  * **Azure Bastion Standard (`hub-southindia-bas`)** is deployed in a dedicated subnet (`10.100.2.0/26`):
    1. An administrator connects to the Azure Portal over browser HTTPS (TLS 443).
    2. Azure Bastion establishes a secure HTML5 browser-based RDP session directly into the private IP of the Gateway VM (`10.100.8.10`).
    3. The Gateway VM requires **no public IP address**.
    4. The Gateway NSG permits inbound port 3389 **exclusively** from the Bastion subnet (`10.100.2.0/26`), rejecting all other connection attempts.

---

### Q2.5: What are Azure Private Endpoints (Private Link), and how do they secure Azure Key Vault in this project?
* **What Interviewers Look For:** Securing PaaS services, disabling public endpoints, DNS integration.
* **Model Answer:**
  * By default, PaaS services like Azure Key Vault have public DNS names resolving to public IP addresses (protected by firewalls).
  * In our enterprise architecture, **Azure Private Endpoint** projects a private Network Interface Card (NIC) with a private IP inside the Spoke VNet (`10.100.8.x`) directly to **Azure Key Vault (`ipskv-prod-chennai-01`)**.
  * **Security Benefits:**
    1. The Key Vault's public network access is set to **Disabled**.
    2. Private DNS Zone `privatelink.vaultcore.azure.net` resolves the Key Vault URI directly to the internal private IP.
    3. Credentials and ODBC connection strings fetched by pipelines traverse the private Azure backbone and never touch the public internet.

---

### Q2.6: What is the On-Premises Data Gateway "Spooling Directory", and how is it tuned to prevent disk saturation?
* **What Interviewers Look For:** Gateway performance tuning, local buffer management, disk I/O bottlenecks.
* **Model Answer:**
  * When extracting massive datasets (e.g., 20GB extraction from General Ledger `F0911`), the OPDG buffers data locally before streaming it to OneLake. This buffer location is the **Spooling Directory**.
  * **Default Risk:** The default path is on the OS system drive (`C:\Windows\ServiceProfiles\...`). Large extractions can fill the `C:\` drive, crashing the Windows Server OS.
  * **Production Configuration in our Project:**
    1. In `Microsoft.PowerBI.DataMovement.Pipeline.GatewayCore.dll.config`, relocate the spooling path to a dedicated high-speed NVMe data disk:
       ```xml
       <setting name="SpoolingDirectory" serializeAs="String">
           <value>D:\GatewaySpooling</value>
       </setting>
       ```
    2. Configure **StreamBeforeRequestCompletes** to `True` so the gateway streams data chunks in real time rather than waiting for the entire query to complete.
    3. Restrict NTFS permissions on `D:\GatewaySpooling` exclusively to the `NT SERVICE\PBIEgwService` account.

---

## 4. Level 3: Advanced & Architectural Questions (Routing, High Availability, Security & Sizing)

### Q3.1: Trace the complete end-to-end packet flow when a Fabric pipeline extracts 5 million records from AS400 table F0911.
* **What Interviewers Look For:** Deep understanding of the end-to-end lifecycle across SaaS, IaaS, firewall, routing, and on-premises layers.
* **Model Answer:**
  ```
  [1. Fabric Data Factory Pipeline]
         │ (Dispatches batch Copy Activity via Azure Relay control channel)
         ▼
  [2. Azure Relay (WebSocket over TLS 443)]
         │ (Gateway VM dequeues extraction command)
         ▼
  [3. Gateway VM (genie-fabric-prod-01: 10.100.8.10)]
         │ (Fetches AS400 password from Azure Key Vault via Private Endpoint)
         │ (Resolves as400.ipscorp.local via Private DNS Resolver -> on-prem DC 10.3.3.4)
         │ (Initiates ODBC TCP 446/8471 connection)
         ▼
  [4. Gateway Spoke Route Table / vWAN Hub]
         │ (Next-hop UDR forces packet through Azure Firewall)
         ▼
  [5. Azure Firewall Standard (hub-southindia-afw: 10.100.1.4)]
         │ (Inspects packet, validates firewall rule: Allow 10.100.8.10 -> 10.242.2.25 on port 446/8471)
         ▼
  [6. IPsec VPN Tunnel / ExpressRoute]
         │ (Encrypted packet travels across private WAN)
         ▼
  [7. On-Premises Edge Router]
         │ (Routes packet onto internal corporate VLAN)
         ▼
  [8. IBM AS400 DB2 Host (10.242.2.25)]
         │ (Executes SQL SELECT * FROM CRPOTA.F0911 WHERE GLUPMJ >= Watermark)
         │ (Streams record batches back over ODBC connection to Gateway VM)
         ▼
  [9. Gateway VM (Buffers in D:\GatewaySpooling, compresses & encrypts)]
         │ (Streams outbound HTTPS/TLS 443 via Service Bus Relay)
         ▼
  [10. Bronze Lakehouse (lh_ips_bronze in OneLake)]
         │ (Commits raw Parquet chunks & appends to Delta transaction log)
  ```

---

### Q3.2: How do Virtual Hub Route Tables and UDRs enforce centralized stateful packet inspection through Azure Firewall?
* **What Interviewers Look For:** Asymmetric routing prevention, default route injection, and Virtual Hub routing intents.
* **Model Answer:**
  * By default, VNets connected to a vWAN hub can communicate directly without traversing the firewall.
  * To enforce compliance and stateful packet inspection:
    1. **Routing Intent / Default Route Propagation:** In the Virtual Hub Route Table, a default route `0.0.0.0/0` and private supernet route `10.0.0.0/8` are configured with **Next Hop = Azure Firewall Private IP (`10.100.1.4`)**.
    2. **Preventing Asymmetric Routing:** If a packet leaves the Gateway VM through the firewall but returns directly across the VPN without hitting the firewall, the TCP handshake is dropped (state violation). vWAN routing ensures both forward and return paths are forced through the firewall's virtual network connection.
    3. **Application & Network Rules:** Azure Firewall enforces explicit allow rules:
       * *Source:* `10.100.8.10/32` (Gateway VM only)
       * *Destination:* `10.242.2.25/32` (AS400 DB2 only)
       * *Ports:* `446, 449, 8471, 9471, 6017`
       * *Action:* Allow with full diagnostic logging to `ips-law-southindia-01`.

---

### Q3.3: How do you design high availability (HA) and load balancing for the On-Premises Data Gateway?
* **What Interviewers Look For:** Gateway clustering, failover mechanisms, active-active scaling.
* **Model Answer:**
  * A single gateway VM represents a single point of failure (SPOF) and a throughput bottleneck during heavy month-end financial loads.
  * **Our High Availability Architecture:**
    1. **Gateway Cluster:** Deploy a secondary gateway VM (`genie-fabric-prod-02: 10.100.8.11`) within the same Spoke VNet in an alternate Azure Availability Zone.
    2. **Cluster Mode:** Join Node 2 to the primary cluster (`gwcluster-ips-prod-01`).
    3. **Load Distribution:** In Fabric Gateway Settings, enable **"Distribute requests across all active gateways in this cluster"**. Incoming batch pipeline queries are automatically distributed across Node 1 and Node 2.
    4. **Automatic Failover:** If Node 1 undergoes Windows OS patching or hardware degradation, the Azure Service Bus relay detects heartbeat loss within 30 seconds and routes 100% of pipeline requests to Node 2.

---

### Q3.4: Fabric Managed VNet Gateway vs. On-Premises Data Gateway: Why did this project choose OPDG?
* **What Interviewers Look For:** Knowledge of cutting-edge Fabric features vs. real-world legacy mainframe constraints.
* **Model Answer:**
  * Microsoft Fabric introduced **Managed VNet Data Gateways**, which allow Fabric to connect into an Azure VNet without hosting an IaaS VM.
  * **Why We Implemented OPDG on Windows Server 2022:**
    1. **Proprietary Legacy ODBC Drivers:** IBM AS400 DB2 requires the specialized **64-bit IBM i Access Client Solutions (ACS) ODBC Driver**. Managed VNet Gateways run on hardened Linux containers where installing proprietary licensed IBM ACS Windows drivers is not supported.
    2. **Custom Kerberos & IBM Host Daemons:** Connecting to AS400 requires custom CCSID character translations, port mapping daemons, and connection string tuning (`SystemNaming=1;CMT=0;`) that can only be configured via Windows ODBC Data Source Administrator (`odbcad32.exe`).
    3. **Direct Local Disk Spooling:** The OPDG allows dedicated NVMe SSD buffering (`D:\GatewaySpooling`) for multi-gigabyte financial table extractions.

---

### Q3.5: How do you mitigate MTU size mismatches and TCP packet fragmentation across the IPsec Site-to-Site VPN tunnel?
* **What Interviewers Look For:** Low-level packet inspection, MSS clamping, and VPN performance tuning.
* **Model Answer:**
  * **The Problem:** Standard Ethernet Maximum Transmission Unit (MTU) is 1500 bytes. When packets traverse an IPsec VPN tunnel, IPsec headers (ESP, AH) add 50–70 bytes of overhead. If the packet size exceeds the tunnel MTU (typically 1400–1420 bytes) and the "Don't Fragment" (DF) bit is set, the router drops the packet, causing silent TCP connection timeouts and stalled pipeline loads.
  * **Mitigation Standards in our Architecture:**
    1. **TCP MSS Clamping:** Configured on the Azure Virtual WAN VPN Gateway and on-premises edge router to clamp the Maximum Segment Size (MSS) to **1350 bytes**.
    2. **OS TCP Window Tuning:** On the Gateway VM (`genie-fabric-prod-01`), execute:
       ```powershell
       netsh interface ipv4 set subinterface "Ethernet" mtu=1400 store=persistent
       ```
    3. **Result:** Eliminates packet fragmentation, ensuring consistent high-speed throughput for large Parquet extractions.

---

### Q3.6: How do you detect and troubleshoot network latency spikes and connection drops between the Gateway and AS400?
* **What Interviewers Look For:** Diagnostic commands, metrics, and log analysis tools.
* **Model Answer:**
  * When batch extraction times jump from 10 minutes to 60 minutes, we execute a structured network diagnostic sequence:
    1. **Test-NetConnection & Port Diagnostics:** Run PowerShell TCP ping against AS400 ports:
       ```powershell
       Test-NetConnection -ComputerName 10.242.2.25 -Port 446
       Test-NetConnection -ComputerName 10.242.2.25 -Port 8471
       ```
    2. **Azure Network Watcher Connection Monitor:** Inspect the continuous probe between the Gateway VM and the on-premises VPN endpoint to verify round-trip time (RTT) and packet drop percentage (baseline RTT is < 15ms).
    3. **Azure Firewall Log Analytics Query:** In `ips-law-southindia-01`, query for dropped packets or port resets:
       ```kusto
       AzureDiagnostics
       | where Category == "AzureFirewallNetworkRule"
       | where msg_s contains "10.242.2.25" and msg_s contains "Deny"
       ```
    4. **Gateway Network Trace:** In the Gateway app, enable **Additional Logging $\rightarrow$ Network tracing**, which exports an `.etl` packet trace analyzing socket resets (`WSAECONNRESET`).

---

## 5. Real-World Scenario-Based Network Troubleshooting

### Scenario 1: Intermittent Pipeline Timeout during 02:00 AM Batch
* **Question:** *"During the nightly 02:00 AM batch extraction, the Fabric Copy Activity for table F0911 occasionally fails with 'ODBC: ERROR [08S01] Communication link failure / Socket closed'. How do you isolate whether the root cause is Azure Firewall, VPN drops, or AS400 CPU saturation?"*
* **Response Framework:**
  1. Check **Azure Firewall logs** in `ips-law-southindia-01` at 02:00 AM. If the firewall dropped the connection due to an idle timeout (default TCP idle timeout is 4 minutes), tune the ODBC connection string to add `KeepAlive=True` or `KeepAliveTimeout=60`.
  2. Inspect the **VPN Gateway metrics** in the Azure Portal. Look for tunnel bandwidth saturation or re-keying renegotiation drops at 02:00 AM.
  3. Contact the AS400 Systems Administrator to review the **WRKACTJOB** (Work with Active Jobs) CPU usage on `IPSPROD`. Often, nightly backup jobs (`SAVLIB`) execute at 02:00 AM, exhausting AS400 disk I/O and closing client sockets.
  4. If AS400 contention is confirmed, shift the Fabric batch ingestion schedule from 02:00 AM to 03:30 AM via `meta.schedule` in the metadata database.

---

### Scenario 2: Gateway VM Disk Exhaustion During Full History Backfill
* **Question:** *"You are executing a 10-year historical backfill of General Ledger transactions. After 45 minutes, the Gateway VM crashes and the pipeline terminates with 'Disk full'. What happened, and how do you re-architect the solution?"*
* **Response Framework:**
  1. **Root Cause:** The query returned 40GB of data. Because `StreamBeforeRequestCompletes` was set to `False`, the gateway attempted to buffer all 40GB in the default `C:\` drive spooling directory, filling the OS disk to 100%.
  2. **Immediate Remediation:** Expand the VM data disk, relocate `SpoolingDirectory` to `D:\GatewaySpooling` in `GatewayCore.dll.config`, and enable `StreamBeforeRequestCompletes = True`.
  3. **Architectural Mitigation:** In `meta.dataset_src_to_brnz`, partition the historical extraction by fiscal year (`WHERE GLFY = 2016`, `WHERE GLFY = 2017`) rather than extracting all 10 years in a single monolithic query, limiting each batch to < 5GB.

---

### Scenario 3: On-Premises Hostname Fails to Resolve After Domain Controller Patching
* **Question:** *"Following weekend infrastructure patching, all Fabric pipelines fail with 'Unable to resolve server host as400.ipscorp.local'. Pinging 10.242.2.25 works fine. What broke in the network architecture?"*
* **Response Framework:**
  1. Identify that the **Azure Private DNS Resolver** (`hub-southindia-dnspr`) is failing to resolve `ipscorp.local`.
  2. Inspect the DNS Forwarding Ruleset attached to the Outbound Endpoint (`10.100.2.80/28`).
  3. Verify whether the on-premises Domain Controller IPs (`10.3.3.4` and `10.3.3.5`) are online and accepting UDP/TCP port 53 queries.
  4. If the primary DC is offline due to patching, verify that the secondary DC IP is configured in the DNS forwarding ruleset.
  5. As a temporary workaround while DC patching completes, add an entry to the Windows Gateway VM `hosts` file (`C:\Windows\System32\drivers\etc\hosts`) mapping `10.242.2.25 as400.ipscorp.local` to immediately restore pipeline operations.

---

### Key Documentation References in the Repo:
* **Networking Concepts & Architecture:** [techstalk/networking_concepts.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/techstalk/networking_concepts.md)
* **Azure Infrastructure Requirements:** [IPS_Azure_Infrastructure_Requirements.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_Azure_Infrastructure_Requirements.md)
* **On-Premises Data Gateway Guide:** [IPS_On_Premises_Data_Gateway_Installation_and_Configuration_Guide.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_On_Premises_Data_Gateway_Installation_and_Configuration_Guide.md)
* **Azure CLI Network Commands:** [techstalk/azure_commands.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/techstalk/azure_commands.md)
* **Enterprise Security Architecture:** [IPS_Enterprise_Security_Architecture_and_Compliance_Guide.md](file:///Users/chandu/Documents/Python_practice/Fabric/docs/additional_docs/IPS_Enterprise_Security_Architecture_and_Compliance_Guide.md)
