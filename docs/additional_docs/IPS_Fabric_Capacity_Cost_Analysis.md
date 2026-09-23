# Microsoft Fabric Capacity & Cost: FinOps Financial Analysis & Sizing Guide

> **Project:** IPS BI Modernization  
> **Topic:** Capacity Unit (CU) Sizing, Pricing Models, Downscale Risk & FinOps Strategy  
> **Date:** September 8, 2026  

---

## Executive Summary & Operational States

For the **IPS BI Modernization** project, the environment lifecycle is defined across two distinct operational states:

1. **Project Implementation State:**
   - **Non-Production (DEV, SIT, UAT):** Housed together in a single **F128 capacity (128 CUs)**.
   - **Production (PROD):** Dedicated capacity finalized as **F64 (64 CUs)**.
   - **Total Capacity Units:** **192 CUs**

2. **Steady State:**
   - **Non-Production (DEV only):** Scaled down to **F32 (32 CUs)**; SIT and UAT environments decommissioned.
   - **Production (PROD):** Retained as **F64 (64 CUs)**.
   - **Total Capacity Units:** **96 CUs** (50% reduction in total compute footprint).

This report details the Microsoft Fabric compute capacity pricing under **Pay-As-You-Go (PAYG)** and **1-Year Capacity Reservation (Committed)** models, highlights the critical **financial lock-in risks** when scaling down from F128 to F32, and outlines an optimal FinOps procurement strategy.

> **Disclaimer:** All the dollar values quoted in the document are based on certain assumptions and may vary in actual conditions and is therefore indicative to give an idea of the financial commitments involved.

---

## Fabric Capacity Unit (CU) Price Baseline

Microsoft Fabric capacity is billed based on Capacity Units (CUs). In standard Azure regions (e.g., East US / standard commercial regions):
- **Pay-As-You-Go (PAYG) Rate:** **$0.18 per CU / hour** (billed per second, 1-minute minimum).
- **1-Year Capacity Reservation Discount:** **~40.5% discount** against full 24/7 PAYG rates.
- **Billing Baseline:** **730 hours per month** (standard 24/7/365 operational month).

| Fabric SKU | Capacity Units (CUs) | PAYG Hourly Rate | PAYG Monthly (24/7, 730 hrs) | PAYG Annual (8,760 hrs) | 1-Year Reserved Monthly | 1-Year Reserved Annual | 1-Yr Savings (%) |
|---|---|---|---|---|---|---|---|
| **F32** | 32 CUs | $5.76 / hr | $4,204.80 | $50,457.60 | $2,501.00 | $30,012.00 | 40.50% |
| **F64** | 64 CUs | $11.52 / hr | $8,409.60 | $100,915.20 | $5,003.00 | $60,036.00 | 40.50% |
| **F128** | 128 CUs | $23.04 / hr | $16,819.20 | $201,830.40 | $10,005.00 | $120,060.00 | 40.50% |

---

## State 1: Project Implementation Phase (F128 + F64)

During the implementation phase, DEV, SIT, and UAT share a high-throughput F128 capacity to support heavy data backfills, complex transformation testing (Bronze/Silver/Gold ingestion), and user acceptance testing, while PROD F64 is isolated for production cutover prep and go-live.

### Pricing Scenarios for Implementation Phase (192 CUs Total)

| Pricing Strategy | Non-Prod (F128) | Prod (F64) | Total Monthly Cost | Total Annualized Cost | Key Notes |
|---|---|---|---|---|---|
| **Option 1: 100% Pay-As-You-Go (24/7)** | $16,819.20 | $8,409.60 | $25,228.80 | $302,745.60 | Maximum agility; zero lock-in; highest cost if left running 24/7. |
| **Option 2: 100% 1-Year Reserved** | $10,005.00 | $5,003.00 | $15,008.00 | $180,096.00 | Lowest fixed rate BUT locks F128 for 12 months (**cannot scale down reservation**). |
| **Option 3: Hybrid (Prod Reserved + Non-Prod PAYG 24/7)** | $16,819.20 | $5,003.00 | $21,822.20 | $261,866.40 | PROD locked at 40.5% discount; Non-Prod remains completely flexible. |
| **Option 4: Hybrid FinOps (Prod Reserved + Non-Prod Scheduled PAYG)** | $5,990.40<br>*(260 hrs/mo)* | $5,003.00<br>*(24/7 Reserved)* | **$10,993.40** | **$131,920.80** | **Recommended:** Pause F128 nights/weekends (~12h/day on workdays). Saves **$14,235/mo** vs PAYG 24/7. |

---

### The Math Behind Option 4

| Component | Sizing & Rate | Operational Hours | Monthly Calculation | Monthly Cost |
|---|---|---|---|---|
| **Production (PROD)** | F64 (64 CUs)<br>1-Yr Capacity Reservation | 24/7/365<br>(~730 hrs/mo) | Flat 1-year reserved monthly commitment (~40.5% discount) | $5,003.00 |
| **Non-Prod (DEV/SIT/UAT)** | F128 (128 CUs)<br>Pay-As-You-Go ($23.04/hr) | Business Hours Only<br>(~260 hrs/mo) | 12 hrs/day × 5 days/wk × 4.33 wks = 260 hrs<br>260 × $23.04/hr | $5,990.40 |
| **Combined Monthly Total** | **192 CUs** | — | — | **$10,993.40** |
| **Annualized Total** | — | — | $10,993.40 × 12 | **$131,920.80** |

#### How do we achieve this in an automated way?
**Automate Start/Stop for Non-Prod (F128):**
- Fabric capacities are native Azure ARM resources (`Microsoft.Fabric/capacities`).
- When paused (suspended), **all compute billing stops immediately ($0/hr)**. Only persistent OneLake storage is billed ($0.023/GB/month).
- We can automate this via **Azure Logic Apps** (simplest, low-code) or **Azure Automation (PowerShell)**.

---

## State 2: Steady State Phase (F32 + F64)

Once project implementation and go-live are complete, SIT and UAT are decommissioned. Non-production scales down to F32 for maintenance, enhancements, and ongoing DEV, while PROD remains on F64.

### Pricing Scenarios for Steady State Phase (96 CUs Total)

| Pricing Strategy | Non-Prod DEV (F32) | Prod (F64) | Total Monthly Cost | Total Annualized Cost | Key Notes |
|---|---|---|---|---|---|
| **Option 1: 100% Pay-As-You-Go (24/7)** | $4,204.80 | $8,409.60 | $12,614.40 | $151,372.80 | Flexible but no commitment discounts applied. |
| **Option 2: 100% 1-Year Reserved** | $2,501.00 | $5,003.00 | **$7,504.00** | **$90,048.00** | **Recommended:** Maximum steady-state commitment savings (**$76,324/yr lower than PAYG**). |

---

## Critical FinOps Warning: The Reservation Downscale Trap

> [!WARNING]
> **Do NOT purchase a 1-Year Capacity Reservation for F128 if implementation lasts less than 12 months!**

- **How Azure Fabric Reservations Work:** An Azure Capacity Reservation is a 1-year binding financial contract for a fixed CU count. It is **not** tied to the compute resource state.
- **The Problem:** If you reserve an F128 for 1 year ($10,005/month) and complete implementation in 6 months, scaling your Azure resource to F32 in the Azure portal will **NOT lower your reservation bill**. Azure will continue billing you for 128 CUs every month for the remaining 6 months.
- **Azure Reservation Exchange Policy:** Microsoft Azure does **not** allow exchanges that reduce total monetary commitment. You can exchange reservations to scale *up*, but you **cannot** exchange an F128 reservation to a smaller F32 reservation.

---

## Final Recommendation

1. **Lock PROD F64 on a 1-Year Capacity Reservation from Day 1:**
   - PROD runs 24/7 continuously through both Implementation and Steady State.
   - Secures an immediate **$40,880 annual discount** ($5,003/mo vs $8,410/mo PAYG).

2. **Run Non-Prod F128 on Pay-As-You-Go with Automated Start/Stop during Implementation:**
   - Implement an automated schedule (e.g., active 7:00 AM – 7:00 PM Monday through Friday = ~260 hours/month; paused on nights and weekends).
   - Monthly cost is reduced from **$16,819/mo (24/7 PAYG)** down to **~$5,990/mo** — saving more than a reserved instance without incurring any multi-month contract commitment!

3. **Seamless Transition to Steady State:**
   - The moment UAT sign-off and cutover occur for all the modules, instantly scale the Non-Prod resource in the Azure portal from **F128 to F32** via a single click or ARM/Bicep template.
   - **At Steady State:**
     - Purchase a **1-Year F32 Reservation ($2,501/mo)**.
