# IPS BI Modernization — Comprehensive Multi-Scenario Sample Data

This directory contains comprehensive, referentially consistent test datasets designed specifically for the **IPS BI Modernization Project**. It simulates the upstream on-premises **IBM AS400 DB2** operational databases (JD Edwards EnterpriseOne ERP), flat file uploads for automated ingestion, and the Metadata-Driven Ingestion Framework (MDF) configuration across **11 core enterprise scenarios**.

---

## Directory Structure

```
data/
├── README.md                          # This documentation file
├── generate_sample_data.py            # Reproducible python generator script
│
├── scenarios/                         # Scenario testing documentation & matrix
│   └── test_scenarios_matrix.md       # Detailed matrix of the 11 test scenarios & record IDs
│
├── raw_jde_as400/                     # Raw AS400 tables (CRPOTA & CRPCTL schemas)
│   ├── CRPOTA.F0010_Company_Constants.csv        # Includes Company 00000 fallback
│   ├── CRPOTA.F0101_Address_Book.csv              # Master address book
│   ├── CRPOTA.F0116_Address_By_Date.csv          # SCD Type 2 relocation history
│   ├── CRPOTA.F03012_Customer_Master.csv         # SCD Type 2 credit rating history & multi-co fallback
│   ├── CRPOTA.F03B11_AR_Ledger.csv               # Accounts Receivable aging, partial payments, credit memos
│   ├── CRPOTA.F0401_Supplier_Master.csv          # Supplier master & payment terms
│   ├── CRPOTA.F0411_AP_Ledger.csv                # AP vouchers (open, EFT paid, cash discount taken)
│   ├── CRPOTA.F0901_Account_Master.csv           # Chart of accounts
│   ├── CRPOTA.F0911_GL_Ledger.csv                # GL lines (Julian boundaries, dual-currency, deduplication, DQ)
│   ├── CRPOTA.F1201_Asset_Master.csv             # Fixed Assets Register (CNC, Robotics, Vehicles)
│   ├── CRPOTA.F1202_Asset_Account_Balances.csv   # Historical cost & accumulated depreciation balances
│   ├── CRPCTL.F0005_User_Defined_Codes.csv       # UDC definitions (Doc types RI, PV, JE, RM; Search types C, V)
│   ├── CRPCTL.F0013_Currency_Codes.csv           # Currency decimals (USD=2, EUR=2, JPY=0, KWD=3)
│   ├── CRPCTL.F0014_Payment_Terms.csv            # Payment terms (NET30, NET60, 210NET30)
│   └── CRPCTL.F0015_Currency_Exchange_Rates.csv  # FX rates across multiple periods
│
├── flatfile_repo_uploads/             # For testing Real-Time Hub / Data Activator automated ingestion
│   ├── budget_targets_2026.csv                   # Valid budget target file
│   ├── budget_targets_malformed_test.csv         # Injected errors (string amount, negative period)
│   └── manual_journal_adjustments_2026.csv       # Manual accruals & adjustments
│
└── metadata/                          # For testing Metadata-Driven Framework (MDF)
    ├── meta_dataset_brz_to_silver.csv            # 10 core dataset mapping definitions & primary keys
    └── meta_dataquality_rules.csv                # 10 comprehensive DQ rules (STOP, QUARANTINE, WARNING)
```

---

## The 11 Enterprise Scenarios Covered

See the complete mapping catalog in [test_scenarios_matrix.md](file:///Users/chandu/Documents/Python_practice/Fabric/data/scenarios/test_scenarios_matrix.md).

1. **Julian Date Boundaries & Edge Cases:** Leap Year Day 366 (`124366`), Leap Day Feb 29 (`124060`), Century 1900s boundary (`099365`), zero dates (`000000`), and malformed day 400 (`124400`).
2. **Multi-Currency & Dual Valuation:** Domestic amounts in `GLAA` vs Foreign amounts in `GLACR` (EUR €10,000 and JPY ¥5,000,000 converted to USD via `F0015` exchange rates).
3. **Slowly Changing Dimensions (SCD Type 2):** Customer 10001 credit limit upgrade (B1 $\rightarrow$ A1) and Customer 10002 address relocation (Dallas $\rightarrow$ Austin) with `effective_start_date` and `effective_end_date`.
4. **Multi-Company Hierarchical Fallback:** In JDE, Customer 10008 is defined at corporate parent Company `00000` rather than operating company `00010`. The ingestion engine resolves using `F03B1.RPCO -> Company 00000` fallback without orphan rejection.
5. **Default Member & Orphan Fact Handling:** General ledger row pointing to non-existent Account ID `999999.9999` tests surrogate key resolution to default member `row_id = -1` ('Unknown/Not Applicable').
6. **CDC Deduplication & Windowed Ranking:** Two records with identical composite business keys (`GLKCO`, `GLDCT`, `GLDOC`, `GLDGJ`, `GLJELN`), where the engine keeps only the newest record based on `_ingested_at`.
7. **Data Quality Quarantine Architecture:**
   - `STOP`: Primary key missing (`GLDOC = 0`).
   - `QUARANTINE`: Invalid date, empty company code, or due date before invoice date routed to `silver.{target}_quarantine`.
   - `WARNING`: Zero amount journal line logged to `log.dq_rule_run`.
8. **Fixed Assets & Depreciation:** Fixed asset cost, accumulated depreciation, and net book value tracking.
9. **Accounts Receivable Aging Buckets:** Invoices categorized across Current, 31-60, 61-90, 90+ days past due, partial payments, and Credit Memos (`RM`).
10. **Accounts Payable Vouchers:** Vouchers open, paid via electronic check (`PK`), cash discounts taken (`210NET30`), and overdue liability.
11. **Real-Time Hub Automated Ingestion:** Automated ingestion trigger testing with valid vs malformed CSV uploads.

---

## How to Regenerate or Expand the Data

To regenerate or scale up the records, run:
```bash
python3 data/generate_sample_data.py
```
