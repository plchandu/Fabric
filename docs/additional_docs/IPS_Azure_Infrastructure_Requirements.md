# IPS Azure Infrastructure Requirements — Intake Form

> **Azure Landing Zone — IaaS Specifications, Active Directory & Network Topology**
> **Customer:** IPS Corporation

---

## 1. Customer Information

| # | Field | Response |
|---|-------|----------|
| 1.1 | **Customer Name** | IPS Corporation |
| 1.2 | **Address** | — |
| 1.3 | **Contact Name** | Pam Messex / Skyler McGinn / Justin Fransisco |
| 1.4 | **Email** | Email/Teams Only |
| 1.5 | **Phone Number** | — |
| 1.6 | **Customer Abbreviation** | IPS |

---

## 2. Azure Requirements

### 2.1 Azure Subscription

| Question | Response |
|----------|----------|
| Are you an Insight CSP Customer? | **Yes** |
| If Yes, have you completed your Azure onboarding? | **No** |
| If No, do you have an existing Azure Subscription? | **Yes** |

---

### 2.2 Access

Insight requires Azure named account(s) for each delivery engineer. **(These should be cloud only accounts)**

(Ex. `<firstname.lastname>@<myazuretenant>.onmicrosoft.com`)

| Requirement | Status |
|-------------|--------|
| Owner role to Azure subscription | **In Progress** |
| MFA enabled for named account(s) | **In Progress** |

> *If you have questions or issues with setting up MFA, we can assist you with the setup.*

#### Insight Engineers Involved

| Engineer Account | Status |
|-----------------|--------|
| Dylan.Lloyd@tenantname.onmicrosoft.com | **In Progress** |
| Mark.Mazur@tenantname.onmicrosoft.com | **In Progress** |
| Tee.Small@tenantname.onmicrosoft.com | **In Progress** |
| Manish.Jangid@tenantname.onmicrosoft.com | **In Progress** |
| Kiran.Kale@tenantname.onmicrosoft.com | **In Progress** |
| Kory.Mills@tenantname.onmicrosoft.com | **In Progress** |

> *If you are a CSP customer we will get the CSM to setup accounts with your approval.*

---

### 2.3 Virtual Network IP Address Space

For the new Azure virtual network, a unique IP Space needs to be defined by the customer.

- A minimum of a **/20 Private IP Address Space** is needed for the new Azure LZ Virtual Networks (**/16 range is preferred**).

| Field | Response |
|-------|----------|
| IP Address Space | **10.100.0.1 – 10.100.3.254** |

---

### 2.4 Identify the Azure Location/Region for your Azure Build

Insight recommends using an Azure location/region closest to your main datacenter and/or user population.

- Use Azure Latency test to identify closest Azure Datacenter:
  - http://www.azurespeed.com/Azure/Latency
- Graphical map of Azure Datacenter locations/regions:
  - https://azure.microsoft.com/en-us/global-infrastructure/regions/

| Field | Response |
|-------|----------|
| Chosen location | **centralus** |

---

### 2.5 Choose SLA Environment Dev/Prod/QA/Test

| Field | Response |
|-------|----------|
| SLA Environment | **PROD** |

---

### 2.6 Hybrid Implementation

| Question | Response |
|----------|----------|
| Will there be VPN connectivity between Azure and On-premise? | **Yes** |

---

### 2.7 On-Premise VPN Device Information (if connecting to on-premises)

**VPN devices must be supported by Azure to establish a VPN connection.**

Reference: https://docs.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpn-devices#devicetable

#### On-Premise VPN Device Information

| Field | Response |
|-------|----------|
| Vendor | **CATO** |
| Model | **X1700** |
| OS Version | **25.0.22707** |
| Site Name (ex. HQ, DC, Chicago...) | **FNTS_PD** |
| Public IP address for above mentioned on-premise VPN device | **207.218.132.29** |
| On-premise IP Address Space(s)/Range(s) | **Will be attached in 3rd tab — significant number of ranges** |

> *(These are the IP address ranges that currently exist in your on-premise datacenter and offices.)*

---

## 3. Active Directory Domain Requirements

### 3.1 Active Directory

| Question | Response |
|----------|----------|
| Is there an existing active directory implementation? | **Yes** |
| If no, do we need to implement Azure Active Directory Domain services? | **N/A** |

---

### 3.2 Active Directory Access

| Question | Response |
|----------|----------|
| Will Insight be doing DC promotion? | **No** |
| If Yes, please provide Insight with a Domain Admin account to Active Directory | *Please Select* |

---

### 3.3 Active Directory Domain Information

| Question | Response |
|----------|----------|
| Is this a new domain? | **Yes** |
| Forest/Domain name (Ex. mydomain.local) | **ipscorp.local** |
| Forest functional level (2016, 2012R2...) | — |
| Domain functional level (2016, 2012R2...) | — |
| Replication Type (DFSR or FRS) | **DFSR** |
| If FRS, Replication Type will need to be upgraded to DFSR | *Please Select* |
| All On-Premise Active Directory Domain Controller FQDN and IP Address | **TCIPSDC01v – 10.3.x.x** |

---

### 3.4 New Azure Domain Controller VM Information

| Question | Response |
|----------|----------|
| OS Version (2022, 2019)? | *Please Select* |
| Server name (do you have a naming convention to follow) | *Please Select* |

**Naming Convention Example:**
```
[usw1][p][dc][01]
[Azure Region][environment][function][##]
```

---

> **End of Document**
