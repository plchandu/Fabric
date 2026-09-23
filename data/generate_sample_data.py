#!/usr/bin/env python3
"""
IPS BI Modernization Project — Comprehensive Sample Data Generator
Generates realistic, referentially consistent test datasets covering 11 critical enterprise scenarios:
1. Julian Date Boundaries & Edge Cases (Leap year day 366, leap day Feb 29, 1900s boundary, malformed dates)
2. Multi-Currency & Dual Valuation (USD 2-dec, EUR 2-dec, JPY 0-dec, domestic GLAA vs foreign GLACR)
3. Slowly Changing Dimensions (SCD Type 1 reference vs SCD Type 2 customer credit/address history)
4. Multi-Company Hierarchical Fallback (Operating company 00010 vs Global fallback 00000)
5. Default Member & Referential Integrity Safeguards (Orphan fact rows resolving to row_id = -1)
6. Deduplication & Windowed Ranking (CDC duplicate records with newer _ingested_at timestamps)
7. Data Quality Quarantine Architecture (STOP vs QUARANTINE vs WARNING rule conditions)
8. Fixed Assets Register & Depreciation (F1201 Asset Master & F1202 Asset Balances)
9. Accounts Receivable Aging Buckets (Current, 30-60, 61-90, 90+ days past due, partial payments, credit memos)
10. Accounts Payable Vouchers & Electronic Payments (Open, paid, discounted, voided)
11. Real-Time Hub / Data Activator File Upload Scenarios (Valid budget vs malformed upload)
"""

import os
import csv
import datetime
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_JDE_DIR = os.path.join(BASE_DIR, "raw_jde_as400")
FLATFILE_DIR = os.path.join(BASE_DIR, "flatfile_repo_uploads")
META_DIR = os.path.join(BASE_DIR, "metadata")
SCENARIOS_DIR = os.path.join(BASE_DIR, "scenarios")

for d in [RAW_JDE_DIR, FLATFILE_DIR, META_DIR, SCENARIOS_DIR]:
    os.makedirs(d, exist_ok=True)

def to_jde_julian(dt: datetime.date) -> int:
    """Converts Gregorian date to JDE CYYDDD format."""
    century = 1 if dt.year >= 2000 else 0
    yy = dt.year % 100
    ddd = dt.timetuple().tm_yday
    return int(f"{century}{yy:02d}{ddd:03d}")

print("Generating comprehensive multi-scenario sample data for IPS BI Modernization...")

# -------------------------------------------------------------
# 1. Company Constants: F0010 (CRPOTA)
# Includes Company 00000 (Global Default / Fallback Company)
# -------------------------------------------------------------
f0010_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F0010_Company_Constants.csv")
companies = [
    {"CCCO": "00000", "CCNAME": "IPS Corporation (Global Parent Fallback)", "CCCRCD": "USD", "CCDFP": "R", "CCDSD": 120001},
    {"CCCO": "00001", "CCNAME": "IPS Corporation (Global HQ)", "CCCRCD": "USD", "CCDFP": "R", "CCDSD": 120001},
    {"CCCO": "00010", "CCNAME": "IPS Manufacturing US LLC", "CCCRCD": "USD", "CCDFP": "R", "CCDSD": 120001},
    {"CCCO": "00020", "CCNAME": "IPS Solutions Canada Inc", "CCCRCD": "CAD", "CCDFP": "R", "CCDSD": 120001},
    {"CCCO": "00030", "CCNAME": "IPS Industrial Europe B.V.", "CCCRCD": "EUR", "CCDFP": "R", "CCDSD": 121001},
    {"CCCO": "00040", "CCNAME": "IPS Technology Japan KK", "CCCRCD": "JPY", "CCDFP": "R", "CCDSD": 122001},
    {"CCCO": "00050", "CCNAME": "IPS Do Brasil Ltda", "CCCRCD": "BRL", "CCDFP": "R", "CCDSD": 123001},
]
with open(f0010_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["CCCO", "CCNAME", "CCCRCD", "CCDFP", "CCDSD"])
    writer.writeheader()
    writer.writerows(companies)

# -------------------------------------------------------------
# 2. Currency Codes: F0013 (CRPCTL)
# Covers 2-decimal (USD, EUR), 0-decimal (JPY), and 3-decimal currencies
# -------------------------------------------------------------
f0013_file = os.path.join(RAW_JDE_DIR, "CRPCTL.F0013_Currency_Codes.csv")
currencies = [
    {"CRCD": "USD", "CRDL01": "US Dollar", "CRDEC": 2},
    {"CRCD": "CAD", "CRDL01": "Canadian Dollar", "CRDEC": 2},
    {"CRCD": "EUR", "CRDL01": "Euro", "CRDEC": 2},
    {"CRCD": "GBP", "CRDL01": "British Pound", "CRDEC": 2},
    {"CRCD": "JPY", "CRDL01": "Japanese Yen", "CRDEC": 0},
    {"CRCD": "BRL", "CRDL01": "Brazilian Real", "CRDEC": 2},
    {"CRCD": "KWD", "CRDL01": "Kuwaiti Dinar", "CRDEC": 3},
]
with open(f0013_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["CRCD", "CRDL01", "CRDEC"])
    writer.writeheader()
    writer.writerows(currencies)

# -------------------------------------------------------------
# 3. Currency Exchange Rates: F0015 (CRPCTL)
# Multi-period rates for cross-currency USD corporate consolidation
# -------------------------------------------------------------
f0015_file = os.path.join(RAW_JDE_DIR, "CRPCTL.F0015_Currency_Exchange_Rates.csv")
exchange_rates = [
    {"CRCHCD": "CAD", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 124001, "CRCRR": 0.7450000},
    {"CRCHCD": "CAD", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 125001, "CRCRR": 0.7410000},
    {"CRCHCD": "CAD", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 126001, "CRCRR": 0.7380000},
    {"CRCHCD": "EUR", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 124001, "CRCRR": 1.0920000},
    {"CRCHCD": "EUR", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 125001, "CRCRR": 1.0880000},
    {"CRCHCD": "EUR", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 126001, "CRCRR": 1.0850000},
    {"CRCHCD": "GBP", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 124001, "CRCRR": 1.2850000},
    {"CRCHCD": "GBP", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 126001, "CRCRR": 1.2720000},
    {"CRCHCD": "JPY", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 124001, "CRCRR": 0.0067000},
    {"CRCHCD": "JPY", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 125001, "CRCRR": 0.0066000},
    {"CRCHCD": "JPY", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 126001, "CRCRR": 0.0065000},
    {"CRCHCD": "BRL", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 124001, "CRCRR": 0.2010000},
    {"CRCHCD": "BRL", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 126001, "CRCRR": 0.1980000},
    {"CRCHCD": "USD", "CRCRDC": "USD", "CRCRT1": "M", "CXEFT": 120001, "CRCRR": 1.0000000},
]
with open(f0015_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["CRCHCD", "CRCRDC", "CRCRT1", "CXEFT", "CRCRR"])
    writer.writeheader()
    writer.writerows(exchange_rates)

# -------------------------------------------------------------
# 4. Payment Terms: F0014 (CRPCTL)
# -------------------------------------------------------------
f0014_file = os.path.join(RAW_JDE_DIR, "CRPCTL.F0014_Payment_Terms.csv")
payment_terms = [
    {"PNPTC": "NET30", "PNDL01": "Net 30 Days", "PNNETD": 30, "PNDCP": 0.0, "PNDCD": 0},
    {"PNPTC": "NET60", "PNDL01": "Net 60 Days", "PNNETD": 60, "PNDCP": 0.0, "PNDCD": 0},
    {"PNPTC": "NET90", "PNDL01": "Net 90 Days", "PNNETD": 90, "PNDCP": 0.0, "PNDCD": 0},
    {"PNPTC": "210NET30", "PNDL01": "2% 10 Net 30 Days", "PNNETD": 30, "PNDCP": 2.0, "PNDCD": 10},
    {"PNPTC": "DUEONREC", "PNDL01": "Due Upon Receipt", "PNNETD": 0, "PNDCP": 0.0, "PNDCD": 0},
]
with open(f0014_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["PNPTC", "PNDL01", "PNNETD", "PNDCP", "PNDCD"])
    writer.writeheader()
    writer.writerows(payment_terms)

# -------------------------------------------------------------
# 5. User Defined Codes: F0005 (CRPCTL)
# Covers doc types (RI, PV, JE, RM), search types (C, V, E), ledger types (AA, CA)
# -------------------------------------------------------------
f0005_file = os.path.join(RAW_JDE_DIR, "CRPCTL.F0005_User_Defined_Codes.csv")
udcs = [
    {"DRSY": "00", "DRRT": "DT", "DRKY": "JE", "DRDL01": "General Journal Entry", "DRDL02": "Financial Ledger"},
    {"DRSY": "00", "DRRT": "DT", "DRKY": "RI", "DRDL01": "Standard Invoice", "DRDL02": "Accounts Receivable"},
    {"DRSY": "00", "DRRT": "DT", "DRKY": "RM", "DRDL01": "Credit Memo / Reversal", "DRDL02": "Accounts Receivable"},
    {"DRSY": "00", "DRRT": "DT", "DRKY": "RB", "DRDL01": "Receipt / Cash Application", "DRDL02": "Accounts Receivable"},
    {"DRSY": "00", "DRRT": "DT", "DRKY": "PV", "DRDL01": "Accounts Payable Voucher", "DRDL02": "Accounts Payable"},
    {"DRSY": "00", "DRRT": "DT", "DRKY": "PN", "DRDL01": "Manual Check Payment", "DRDL02": "Accounts Payable"},
    {"DRSY": "00", "DRRT": "DT", "DRKY": "PK", "DRDL01": "Auto Check / Electronic Payment", "DRDL02": "Accounts Payable"},
    {"DRSY": "01", "DRRT": "ST", "DRKY": "C", "DRDL01": "Customer", "DRDL02": "Address Book Search Type"},
    {"DRSY": "01", "DRRT": "ST", "DRKY": "V", "DRDL01": "Supplier / Vendor", "DRDL02": "Address Book Search Type"},
    {"DRSY": "01", "DRRT": "ST", "DRKY": "E", "DRDL01": "Employee", "DRDL02": "Address Book Search Type"},
    {"DRSY": "00", "DRRT": "LT", "DRKY": "AA", "DRDL01": "Actual Amounts Ledger", "DRDL02": "Primary Balance Ledger"},
    {"DRSY": "00", "DRRT": "LT", "DRKY": "CA", "DRDL01": "Foreign Currency Ledger", "DRDL02": "Currency Tracking"},
]
with open(f0005_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["DRSY", "DRRT", "DRKY", "DRDL01", "DRDL02"])
    writer.writeheader()
    writer.writerows(udcs)

# -------------------------------------------------------------
# 6. Address Book Master & Details: F0101 & F0116 (CRPOTA)
# Supports SCD Type 2 historical relocation (e.g. Customer 10002 moving TX address)
# -------------------------------------------------------------
f0101_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F0101_Address_Book.csv")
f0116_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F0116_Address_By_Date.csv")

address_book = [
    # Customers
    {"ABAN8": 10001, "ABALPH": "Acme Industrial Corp", "ABAT1": "C", "ABMCU": "      100010", "ABTAX": "XX-1234567"},
    {"ABAN8": 10002, "ABALPH": "Summit Global Supply LLC", "ABAT1": "C", "ABMCU": "      100010", "ABTAX": "XX-2345678"},
    {"ABAN8": 10003, "ABALPH": "Pinnacle Pipeline Logistics", "ABAT1": "C", "ABMCU": "      100010", "ABTAX": "XX-3456789"},
    {"ABAN8": 10004, "ABALPH": "Maple Leaf Energy Ltd", "ABAT1": "C", "ABMCU": "      100020", "ABTAX": "CA-9988776"},
    {"ABAN8": 10005, "ABALPH": "Bavaria Automotive GmbH", "ABAT1": "C", "ABMCU": "      100030", "ABTAX": "DE-4455667"},
    {"ABAN8": 10006, "ABALPH": "Tokyo Advanced Robotics", "ABAT1": "C", "ABMCU": "      100040", "ABTAX": "JP-1122334"},
    {"ABAN8": 10007, "ABALPH": "Vanguard Manufacturing", "ABAT1": "C", "ABMCU": "      100010", "ABTAX": "XX-5566778"},
    {"ABAN8": 10008, "ABALPH": "Horizon Global Retail (Multi-Co)", "ABAT1": "C", "ABMCU": "      000000", "ABTAX": "XX-6677889"},
    {"ABAN8": 10009, "ABALPH": "Global Marine Systems", "ABAT1": "C", "ABMCU": "      100010", "ABTAX": "XX-7788990"},
    {"ABAN8": 10010, "ABALPH": "Quantum Dynamics Corp", "ABAT1": "C", "ABMCU": "      100010", "ABTAX": "XX-8899001"},
    # Suppliers
    {"ABAN8": 50001, "ABALPH": "Precision Steel Mills Inc", "ABAT1": "V", "ABMCU": "      100010", "ABTAX": "XX-9900112"},
    {"ABAN8": 50002, "ABALPH": "Titan Chemical Reagents", "ABAT1": "V", "ABMCU": "      100010", "ABTAX": "XX-0011223"},
    {"ABAN8": 50003, "ABALPH": "Ontario Heavy Alloy Co", "ABAT1": "V", "ABMCU": "      100020", "ABTAX": "CA-3344556"},
    {"ABAN8": 50004, "ABALPH": "Rheinland Precision Castings", "ABAT1": "V", "ABMCU": "      100030", "ABTAX": "DE-7788990"},
    {"ABAN8": 50005, "ABALPH": "Nippon Sensor Technologies", "ABAT1": "V", "ABMCU": "      100040", "ABTAX": "JP-5566778"},
    {"ABAN8": 50006, "ABALPH": "Apex Freight Logistics", "ABAT1": "V", "ABMCU": "      100010", "ABTAX": "XX-2233445"},
    {"ABAN8": 50007, "ABALPH": "Benchmark Packaging Solutions", "ABAT1": "V", "ABMCU": "      100010", "ABTAX": "XX-4455667"},
    {"ABAN8": 50008, "ABALPH": "Delta Electronics Component", "ABAT1": "V", "ABMCU": "      100010", "ABTAX": "XX-6677889"},
]

# SCD Type 2 Address records: Customer 10002 has 2 versions (historical relocation from Dallas to Austin)
address_details = [
    {"ALAN8": 10001, "ALADD1": "100 Innovation Way", "ALCTY1": "Chicago", "ALADDS": "IL", "ALADDZ": "60601", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    # 10002 Version 1 (Historical)
    {"ALAN8": 10002, "ALADD1": "450 Industrial Parkway", "ALCTY1": "Dallas", "ALADDS": "TX", "ALADDZ": "75201", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 124365},
    # 10002 Version 2 (Current)
    {"ALAN8": 10002, "ALADD1": "900 Silicon Hills Blvd", "ALCTY1": "Austin", "ALADDS": "TX", "ALADDZ": "78701", "ALCTR": "USA", "ALEFTB": 125001, "ALEFTE": 199365},
    {"ALAN8": 10003, "ALADD1": "890 Harbor Blvd", "ALCTY1": "Houston", "ALADDS": "TX", "ALADDZ": "77002", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 10004, "ALADD1": "1200 Bay Street", "ALCTY1": "Toronto", "ALADDS": "ON", "ALADDZ": "M5R 2A5", "ALCTR": "CAN", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 10005, "ALADD1": "Industriestrasse 14", "ALCTY1": "Munich", "ALADDS": "BY", "ALADDZ": "80331", "ALCTR": "DEU", "ALEFTB": 121001, "ALEFTE": 199365},
    {"ALAN8": 10006, "ALADD1": "3-2-1 Marunouchi, Chiyoda-ku", "ALCTY1": "Tokyo", "ALADDS": "13", "ALADDZ": "100-0005", "ALCTR": "JPN", "ALEFTB": 122001, "ALEFTE": 199365},
    {"ALAN8": 10007, "ALADD1": "742 Evergreen Terrace", "ALCTY1": "Springfield", "ALADDS": "IL", "ALADDZ": "62704", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 10008, "ALADD1": "221B Global Way", "ALCTY1": "Atlanta", "ALADDS": "GA", "ALADDZ": "30303", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 10009, "ALADD1": "500 Ocean Avenue", "ALCTY1": "Seattle", "ALADDS": "WA", "ALADDZ": "98101", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 10010, "ALADD1": "1 Silicon Park", "ALCTY1": "San Jose", "ALADDS": "CA", "ALADDZ": "95110", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 50001, "ALADD1": "900 Foundry Road", "ALCTY1": "Pittsburgh", "ALADDS": "PA", "ALADDZ": "15201", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 50002, "ALADD1": "300 Chemical Blvd", "ALCTY1": "Wilmington", "ALADDS": "DE", "ALADDZ": "19801", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 50003, "ALADD1": "55 Queen St West", "ALCTY1": "Hamilton", "ALADDS": "ON", "ALADDZ": "L8P 4Y7", "ALCTR": "CAN", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 50004, "ALADD1": "Rheinufer 88", "ALCTY1": "Cologne", "ALADDS": "NW", "ALADDZ": "50667", "ALCTR": "DEU", "ALEFTB": 121001, "ALEFTE": 199365},
    {"ALAN8": 50005, "ALADD1": "1-1 Shinjuku", "ALCTY1": "Tokyo", "ALADDS": "13", "ALADDZ": "160-0022", "ALCTR": "JPN", "ALEFTB": 122001, "ALEFTE": 199365},
    {"ALAN8": 50006, "ALADD1": "1400 Airport Drive", "ALCTY1": "Memphis", "ALADDS": "TN", "ALADDZ": "38118", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 50007, "ALADD1": "600 Box Factory Way", "ALCTY1": "Charlotte", "ALADDS": "NC", "ALADDZ": "28202", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
    {"ALAN8": 50008, "ALADD1": "700 Circuit Court", "ALCTY1": "Austin", "ALADDS": "TX", "ALADDZ": "78701", "ALCTR": "USA", "ALEFTB": 120001, "ALEFTE": 199365},
]

with open(f0101_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["ABAN8", "ABALPH", "ABAT1", "ABMCU", "ABTAX"])
    writer.writeheader()
    writer.writerows(address_book)

with open(f0116_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["ALAN8", "ALADD1", "ALCTY1", "ALADDS", "ALADDZ", "ALCTR", "ALEFTB", "ALEFTE"])
    writer.writeheader()
    writer.writerows(address_details)

# -------------------------------------------------------------
# 7. Customer Master: F03012 (CRPOTA)
# Covers:
# - SCD Type 2 credit rating change (Customer 10001)
# - Multi-Company Hierarchical Fallback: Customer 10008 defined at Company 00000
# -------------------------------------------------------------
f03012_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F03012_Customer_Master.csv")
customer_master = [
    # Customer 10001 Version 1: Lower credit limit (Historical)
    {"AIAN8": 10001, "AICO": "00010", "AICRCA": "USD", "AICRAL": 25000000, "AICRCD": "B1", "AITRDC": 100, "AITRAP": "NET30", "AIPROV": "COL01", "AIEFTB": 122001, "AIEFTE": 124151},
    # Customer 10001 Version 2: Upgraded credit limit (Current)
    {"AIAN8": 10001, "AICO": "00010", "AICRCA": "USD", "AICRAL": 50000000, "AICRCD": "A1", "AITRDC": 200, "AITRAP": "NET30", "AIPROV": "COL01", "AIEFTB": 124152, "AIEFTE": 199365},
    {"AIAN8": 10002, "AICO": "00010", "AICRCA": "USD", "AICRAL": 35000000, "AICRCD": "A2", "AITRDC": 0, "AITRAP": "NET60", "AIPROV": "COL01", "AIEFTB": 120001, "AIEFTE": 199365},
    {"AIAN8": 10003, "AICO": "00010", "AICRCA": "USD", "AICRAL": 20000000, "AICRCD": "B1", "AITRDC": 150, "AITRAP": "210NET30", "AIPROV": "COL02", "AIEFTB": 120001, "AIEFTE": 199365},
    {"AIAN8": 10004, "AICO": "00020", "AICRCA": "CAD", "AICRAL": 40000000, "AICRCD": "A1", "AITRDC": 0, "AITRAP": "NET30", "AIPROV": "COL03", "AIEFTB": 120001, "AIEFTE": 199365},
    {"AIAN8": 10005, "AICO": "00030", "AICRCA": "EUR", "AICRAL": 60000000, "AICRCD": "A1", "AITRDC": 250, "AITRAP": "NET60", "AIPROV": "COL04", "AIEFTB": 121001, "AIEFTE": 199365},
    {"AIAN8": 10006, "AICO": "00040", "AICRCA": "JPY", "AICRAL": 8000000000, "AICRCD": "A1", "AITRDC": 0, "AITRAP": "NET30", "AIPROV": "COL05", "AIEFTB": 122001, "AIEFTE": 199365},
    {"AIAN8": 10007, "AICO": "00010", "AICRCA": "USD", "AICRAL": 15000000, "AICRCD": "C1", "AITRDC": 0, "AITRAP": "NET30", "AIPROV": "COL02", "AIEFTB": 120001, "AIEFTE": 199365},
    # Multi-Company Fallback: Customer 10008 defined globally under Company 00000
    {"AIAN8": 10008, "AICO": "00000", "AICRCA": "USD", "AICRAL": 25000000, "AICRCD": "B2", "AITRDC": 100, "AITRAP": "NET30", "AIPROV": "COL01", "AIEFTB": 120001, "AIEFTE": 199365},
    {"AIAN8": 10009, "AICO": "00010", "AICRCA": "USD", "AICRAL": 30000000, "AICRCD": "A2", "AITRDC": 0, "AITRAP": "NET60", "AIPROV": "COL02", "AIEFTB": 120001, "AIEFTE": 199365},
    {"AIAN8": 10010, "AICO": "00010", "AICRCA": "USD", "AICRAL": 45000000, "AICRCD": "A1", "AITRDC": 200, "AITRAP": "NET30", "AIPROV": "COL01", "AIEFTB": 120001, "AIEFTE": 199365},
]
with open(f03012_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["AIAN8", "AICO", "AICRCA", "AICRAL", "AICRCD", "AITRDC", "AITRAP", "AIPROV", "AIEFTB", "AIEFTE"])
    writer.writeheader()
    writer.writerows(customer_master)

# -------------------------------------------------------------
# 8. Supplier Master: F0401 (CRPOTA)
# -------------------------------------------------------------
f0401_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F0401_Supplier_Master.csv")
supplier_master = [
    {"A6AN8": 50001, "A6CO": "00010", "A6CRCA": "USD", "A6TRAP": "NET30", "A6TAX": "XX-9900112", "A6AT1": "V"},
    {"A6AN8": 50002, "A6CO": "00010", "A6CRCA": "USD", "A6TRAP": "NET60", "A6TAX": "XX-0011223", "A6AT1": "V"},
    {"A6AN8": 50003, "A6CO": "00020", "A6CRCA": "CAD", "A6TRAP": "NET30", "A6TAX": "CA-3344556", "A6AT1": "V"},
    {"A6AN8": 50004, "A6CO": "00030", "A6CRCA": "EUR", "A6TRAP": "NET60", "A6TAX": "DE-7788990", "A6AT1": "V"},
    {"A6AN8": 50005, "A6CO": "00040", "A6CRCA": "JPY", "A6TRAP": "NET30", "A6TAX": "JP-5566778", "A6AT1": "V"},
    {"A6AN8": 50006, "A6CO": "00010", "A6CRCA": "USD", "A6TRAP": "210NET30", "A6TAX": "XX-2233445", "A6AT1": "V"},
    {"A6AN8": 50007, "A6CO": "00010", "A6CRCA": "USD", "A6TRAP": "NET30", "A6TAX": "XX-4455667", "A6AT1": "V"},
    {"A6AN8": 50008, "A6CO": "00010", "A6CRCA": "USD", "A6TRAP": "NET60", "A6TAX": "XX-6677889", "A6AT1": "V"},
]
with open(f0401_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["A6AN8", "A6CO", "A6CRCA", "A6TRAP", "A6TAX", "A6AT1"])
    writer.writeheader()
    writer.writerows(supplier_master)

# -------------------------------------------------------------
# 9. Account Master: F0901 (CRPOTA)
# -------------------------------------------------------------
f0901_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F0901_Account_Master.csv")
accounts = [
    {"GMAID": "100010.1110", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "1110", "GMSUB": "   ", "GMDL01": "Operating Cash Account", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.1210", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "1210", "GMSUB": "   ", "GMDL01": "Accounts Receivable Trade", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.1410", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "1410", "GMSUB": "   ", "GMDL01": "Finished Goods Inventory", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.1420", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "1420", "GMSUB": "   ", "GMDL01": "Raw Materials Inventory", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.1710", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "1710", "GMSUB": "   ", "GMDL01": "Plant & Machinery Cost", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.1750", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "1750", "GMSUB": "   ", "GMDL01": "Accumulated Depreciation Machinery", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.2110", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "2110", "GMSUB": "   ", "GMDL01": "Accounts Payable Trade", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.2120", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "2120", "GMSUB": "   ", "GMDL01": "Accrued Operating Expenses", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.5010", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "5010", "GMSUB": "   ", "GMDL01": "Gross Revenue Commercial Sales", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.5020", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "5020", "GMSUB": "   ", "GMDL01": "Revenue Discounts & Returns", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.6010", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "6010", "GMSUB": "   ", "GMDL01": "Cost of Goods Sold - Materials", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.6020", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "6020", "GMSUB": "   ", "GMDL01": "Cost of Goods Sold - Freight", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.7010", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "7010", "GMSUB": "   ", "GMDL01": "Salaries & Benefits", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100010.7050", "GMCO": "00010", "GMMCU": "      100010", "GMOBJ": "7050", "GMSUB": "   ", "GMDL01": "Office Rent & Utilities", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100020.1110", "GMCO": "00020", "GMMCU": "      100020", "GMOBJ": "1110", "GMSUB": "   ", "GMDL01": "CAD Operating Cash", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100020.5010", "GMCO": "00020", "GMMCU": "      100020", "GMOBJ": "5010", "GMSUB": "   ", "GMDL01": "Canada Commercial Revenue", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100030.1110", "GMCO": "00030", "GMMCU": "      100030", "GMOBJ": "1110", "GMSUB": "   ", "GMDL01": "EUR Operating Cash", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100030.5010", "GMCO": "00030", "GMMCU": "      100030", "GMOBJ": "5010", "GMSUB": "   ", "GMDL01": "Europe Commercial Revenue", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100040.1110", "GMCO": "00040", "GMMCU": "      100040", "GMOBJ": "1110", "GMSUB": "   ", "GMDL01": "JPY Operating Cash", "GMLDA": "7", "GMPEC": " "},
    {"GMAID": "100040.5010", "GMCO": "00040", "GMMCU": "      100040", "GMOBJ": "5010", "GMSUB": "   ", "GMDL01": "Japan Commercial Revenue", "GMLDA": "7", "GMPEC": " "},
]
with open(f0901_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["GMAID", "GMCO", "GMMCU", "GMOBJ", "GMSUB", "GMDL01", "GMLDA", "GMPEC"])
    writer.writeheader()
    writer.writerows(accounts)

# -------------------------------------------------------------
# 10. Fixed Asset Master & Balances: F1201 & F1202 (CRPOTA)
# Supports Fixed Asset Register & Depreciation Scenarios
# -------------------------------------------------------------
f1201_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F1201_Asset_Master.csv")
f1202_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F1202_Asset_Account_Balances.csv")

assets = [
    {"FA#UMB": 1001, "FAAAID": "100010.1710", "FACO": "00010", "FAMCU": "      100010", "FADL01": "CNC Precision Milling Station", "FACL01": "MACH", "FASERN": "SN-CNC-8899", "FAINSD": 121015, "FADEPN": "SL"},
    {"FA#UMB": 1002, "FAAAID": "100010.1710", "FACO": "00010", "FAMCU": "      100010", "FADL01": "Automated Robotic Arm Unit", "FACL01": "ROBOT", "FASERN": "SN-ROB-4411", "FAINSD": 122090, "FADEPN": "SL"},
    {"FA#UMB": 1003, "FAAAID": "100010.1710", "FACO": "00010", "FAMCU": "      100010", "FADL01": "Logistics Forklift Fleet (3x)", "FACL01": "VEHIC", "FASERN": "SN-FL-9922", "FAINSD": 123045, "FADEPN": "SL"},
    {"FA#UMB": 1004, "FAAAID": "100030.1710", "FACO": "00030", "FAMCU": "      100030", "FADL01": "Rotary Stamping Press", "FACL01": "MACH", "FASERN": "SN-ST-2233", "FAINSD": 122180, "FADEPN": "SL"},
]
asset_balances = [
    {"FA#UMB": 1001, "FACO": "00010", "FAFY": 24, "FALEDG": "AA", "FAHISTCOST": 25000000, "FAACCDEP": 7500000, "FANETBKVAL": 17500000},
    {"FA#UMB": 1001, "FACO": "00010", "FAFY": 25, "FALEDG": "AA", "FAHISTCOST": 25000000, "FAACCDEP": 12500000, "FANETBKVAL": 12500000},
    {"FA#UMB": 1002, "FACO": "00010", "FAFY": 24, "FALEDG": "AA", "FAHISTCOST": 18000000, "FAACCDEP": 3600000, "FANETBKVAL": 14400000},
    {"FA#UMB": 1002, "FACO": "00010", "FAFY": 25, "FALEDG": "AA", "FAHISTCOST": 18000000, "FAACCDEP": 7200000, "FANETBKVAL": 10800000},
    {"FA#UMB": 1003, "FACO": "00010", "FAFY": 25, "FALEDG": "AA", "FAHISTCOST": 9500000, "FAACCDEP": 1900000, "FANETBKVAL": 7600000},
    {"FA#UMB": 1004, "FACO": "00030", "FAFY": 25, "FALEDG": "AA", "FAHISTCOST": 32000000, "FAACCDEP": 8000000, "FANETBKVAL": 24000000},
]
with open(f1201_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["FA#UMB", "FAAAID", "FACO", "FAMCU", "FADL01", "FACL01", "FASERN", "FAINSD", "FADEPN"])
    writer.writeheader()
    writer.writerows(assets)

with open(f1202_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["FA#UMB", "FACO", "FAFY", "FALEDG", "FAHISTCOST", "FAACCDEP", "FANETBKVAL"])
    writer.writeheader()
    writer.writerows(asset_balances)

# -------------------------------------------------------------
# 11. General Ledger Transactions: F0911 (CRPOTA)
# Comprehensive Scenarios:
# 1. Standard sales, purchases, payroll across 2024-2026
# 2. Leap year leap day: 2024-02-29 (Julian 124060)
# 3. Leap year day 366: 2024-12-31 (Julian 124366)
# 4. Century 1900s boundary: 1999-12-31 (Julian 099365)
# 5. Dual-Currency transactions (Domestic GLAA vs Foreign GLACR)
# 6. Deduplication Scenario: duplicate composite keys with newer _ingested_at
# 7. Referential Integrity / Orphan Fact: Unmapped account 999999.9999
# 8. Data Quality Edge Cases:
#    - Malformed Julian day 400 (Julian 124400) -> QUARANTINE
#    - Julian 000000 -> Sentinel/NULL
#    - Missing company code -> QUARANTINE
#    - Missing document number (GLDOC=0) -> STOP
#    - Zero amount -> WARNING
# -------------------------------------------------------------
f0911_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F0911_GL_Ledger.csv")
random.seed(42)

gl_records = []
doc_counter = 100000

# Base dates across 2024-2026
base_dates = [
    datetime.date(2024, 1, 15),
    datetime.date(2024, 2, 29),  # Leap Day 2024
    datetime.date(2024, 3, 31),
    datetime.date(2024, 6, 30),
    datetime.date(2024, 9, 30),
    datetime.date(2024, 12, 31), # Leap Year Day 366
    datetime.date(2025, 1, 15),
    datetime.date(2025, 3, 31),
    datetime.date(2025, 6, 30),
    datetime.date(2025, 9, 30),
    datetime.date(2025, 12, 31), # Non-Leap Year Day 365
    datetime.date(2026, 1, 15),
    datetime.date(2026, 2, 28),
    datetime.date(2026, 3, 10),
    datetime.date(2026, 3, 23),
]

for dt in base_dates:
    julian_date = to_jde_julian(dt)
    
    # 1. Domestic Sales Revenue (RI)
    doc_counter += 1
    cust = random.choice(customer_master)
    sales_amount = random.randint(200000, 3500000)
    
    gl_records.append({
        "GLKCO": cust["AICO"], "GLDCT": "RI", "GLDOC": doc_counter, "GLDGJ": julian_date,
        "GLJELN": 1.0, "GLCO": cust["AICO"], "GLMCU": f"      {cust['AICO']}", "GLAID": f"{cust['AICO']}.1210",
        "GLAA": sales_amount, "GLACR": sales_amount, "GLCRCD": cust["AICRCA"], "GLPOST": "P",
        "GLICUT": "G", "GLICU": 5012, "GLDICJ": julian_date, "GLDSAV": julian_date,
        "_ingested_at": "2026-09-23T06:00:00Z"
    })
    gl_records.append({
        "GLKCO": cust["AICO"], "GLDCT": "RI", "GLDOC": doc_counter, "GLDGJ": julian_date,
        "GLJELN": 2.0, "GLCO": cust["AICO"], "GLMCU": f"      {cust['AICO']}", "GLAID": f"{cust['AICO']}.5010",
        "GLAA": -sales_amount, "GLACR": -sales_amount, "GLCRCD": cust["AICRCA"], "GLPOST": "P",
        "GLICUT": "G", "GLICU": 5012, "GLDICJ": julian_date, "GLDSAV": julian_date,
        "_ingested_at": "2026-09-23T06:00:00Z"
    })
    
    # 2. Purchasing Voucher (PV)
    doc_counter += 1
    supp = random.choice(supplier_master)
    purch_amount = random.randint(150000, 2200000)
    
    gl_records.append({
        "GLKCO": supp["A6CO"], "GLDCT": "PV", "GLDOC": doc_counter, "GLDGJ": julian_date,
        "GLJELN": 1.0, "GLCO": supp["A6CO"], "GLMCU": f"      {supp['A6CO']}", "GLAID": f"{supp['A6CO']}.6010",
        "GLAA": purch_amount, "GLACR": purch_amount, "GLCRCD": supp["A6CRCA"], "GLPOST": "P",
        "GLICUT": "V", "GLICU": 6022, "GLDICJ": julian_date, "GLDSAV": julian_date,
        "_ingested_at": "2026-09-23T06:00:00Z"
    })
    gl_records.append({
        "GLKCO": supp["A6CO"], "GLDCT": "PV", "GLDOC": doc_counter, "GLDGJ": julian_date,
        "GLJELN": 2.0, "GLCO": supp["A6CO"], "GLMCU": f"      {supp['A6CO']}", "GLAID": f"{supp['A6CO']}.2110",
        "GLAA": -purch_amount, "GLACR": -purch_amount, "GLCRCD": supp["A6CRCA"], "GLPOST": "P",
        "GLICUT": "V", "GLICU": 6022, "GLDICJ": julian_date, "GLDSAV": julian_date,
        "_ingested_at": "2026-09-23T06:00:00Z"
    })

# --- SCENARIO 2: Dual-Currency Transactions (Domestic USD vs Foreign EUR / JPY) ---
# Case A: US Company 00010 receives EUR invoice (€10,000.00 @ 1.085 FX = $10,850.00 Domestic)
doc_counter += 1
gl_records.append({
    "GLKCO": "00010", "GLDCT": "PV", "GLDOC": doc_counter, "GLDGJ": 126050,
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.6010",
    "GLAA": 1085000, "GLACR": 1000000, "GLCRCD": "EUR", "GLPOST": "P",
    "GLICUT": "V", "GLICU": 7001, "GLDICJ": 126050, "GLDSAV": 126050,
    "_ingested_at": "2026-09-23T06:00:00Z"
})
gl_records.append({
    "GLKCO": "00010", "GLDCT": "PV", "GLDOC": doc_counter, "GLDGJ": 126050,
    "GLJELN": 2.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.2110",
    "GLAA": -1085000, "GLACR": -1000000, "GLCRCD": "EUR", "GLPOST": "P",
    "GLICUT": "V", "GLICU": 7001, "GLDICJ": 126050, "GLDSAV": 126050,
    "_ingested_at": "2026-09-23T06:00:00Z"
})

# Case B: US Company 00010 buys from Japan (¥5,000,000 @ 0.0065 FX = $32,500.00 Domestic)
doc_counter += 1
gl_records.append({
    "GLKCO": "00010", "GLDCT": "PV", "GLDOC": doc_counter, "GLDGJ": 126060,
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.1420",
    "GLAA": 3250000, "GLACR": 5000000, "GLCRCD": "JPY", "GLPOST": "P",
    "GLICUT": "V", "GLICU": 7002, "GLDICJ": 126060, "GLDSAV": 126060,
    "_ingested_at": "2026-09-23T06:00:00Z"
})
gl_records.append({
    "GLKCO": "00010", "GLDCT": "PV", "GLDOC": doc_counter, "GLDGJ": 126060,
    "GLJELN": 2.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.2110",
    "GLAA": -3250000, "GLACR": -5000000, "GLCRCD": "JPY", "GLPOST": "P",
    "GLICUT": "V", "GLICU": 7002, "GLDICJ": 126060, "GLDSAV": 126060,
    "_ingested_at": "2026-09-23T06:00:00Z"
})

# --- SCENARIO 4: Century 1900s Historical Boundary Date ---
doc_counter += 1
gl_records.append({
    "GLKCO": "00010", "GLDCT": "JE", "GLDOC": doc_counter, "GLDGJ": 99365, # Dec 31, 1999 (C=0, YY=99, DDD=365)
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.1110",
    "GLAA": 100000, "GLACR": 100000, "GLCRCD": "USD", "GLPOST": "P",
    "GLICUT": "G", "GLICU": 1999, "GLDICJ": 99365, "GLDSAV": 99365,
    "_ingested_at": "2026-09-23T06:00:00Z"
})

# --- SCENARIO 5: Default Member / Orphan Fact Handling (Unknown Account) ---
# Fact points to non-existent account 999999.9999 -> Gold engine must map to row_id = -1
doc_counter += 1
gl_records.append({
    "GLKCO": "00010", "GLDCT": "JE", "GLDOC": doc_counter, "GLDGJ": 126070,
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "999999.9999",
    "GLAA": 45000, "GLACR": 45000, "GLCRCD": "USD", "GLPOST": "P",
    "GLICUT": "G", "GLICU": 8001, "GLDICJ": 126070, "GLDSAV": 126070,
    "_ingested_at": "2026-09-23T06:00:00Z"
})

# --- SCENARIO 6: Deduplication & Windowed Ranking (CDC Overlap) ---
# Two records with EXACT SAME composite key (00010, RI, 777001, 126040, 1.0), but different ingested_at
# Older record: Amount $1,000.00
gl_records.append({
    "GLKCO": "00010", "GLDCT": "RI", "GLDOC": 777001, "GLDGJ": 126040,
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.1210",
    "GLAA": 100000, "GLACR": 100000, "GLCRCD": "USD", "GLPOST": "P",
    "GLICUT": "G", "GLICU": 9001, "GLDICJ": 126040, "GLDSAV": 126040,
    "_ingested_at": "2026-09-23T04:00:00Z" # Older
})
# Newer corrected record: Amount $1,250.00 (Must survive deduplication!)
gl_records.append({
    "GLKCO": "00010", "GLDCT": "RI", "GLDOC": 777001, "GLDGJ": 126040,
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.1210",
    "GLAA": 125000, "GLACR": 125000, "GLCRCD": "USD", "GLPOST": "P",
    "GLICUT": "G", "GLICU": 9001, "GLDICJ": 126040, "GLDSAV": 126040,
    "_ingested_at": "2026-09-23T07:30:00Z" # Newer
})

# --- SCENARIO 7: Data Quality Quarantine Test Cases ---
# DQ 1: Malformed Julian date (Day 400 does not exist in calendar!) -> QUARANTINE
gl_records.append({
    "GLKCO": "00010", "GLDCT": "JE", "GLDOC": 999901, "GLDGJ": 124400,
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.1110",
    "GLAA": 50000, "GLACR": 50000, "GLCRCD": "USD", "GLPOST": "P",
    "GLICUT": "G", "GLICU": 9991, "GLDICJ": 124400, "GLDSAV": 124400,
    "_ingested_at": "2026-09-23T06:00:00Z"
})
# DQ 2: Zero date (000000) -> QUARANTINE or Sentinel handling
gl_records.append({
    "GLKCO": "00010", "GLDCT": "JE", "GLDOC": 999902, "GLDGJ": 0,
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.1110",
    "GLAA": 60000, "GLACR": 60000, "GLCRCD": "USD", "GLPOST": "P",
    "GLICUT": "G", "GLICU": 9992, "GLDICJ": 0, "GLDSAV": 0,
    "_ingested_at": "2026-09-23T06:00:00Z"
})
# DQ 3: Untrimmed whitespace in key columns -> Transformation category 5 strips padding
gl_records.append({
    "GLKCO": "00010  ", "GLDCT": "JE  ", "GLDOC": 999903, "GLDGJ": 126080,
    "GLJELN": 1.0, "GLCO": "00010  ", "GLMCU": "100010   ", "GLAID": "100010.1110   ",
    "GLAA": 75000, "GLACR": 75000, "GLCRCD": "USD  ", "GLPOST": "P ",
    "GLICUT": "G ", "GLICU": 9993, "GLDICJ": 126080, "GLDSAV": 126080,
    "_ingested_at": "2026-09-23T06:00:00Z"
})
# DQ 4: Missing / Empty company code -> QUARANTINE
gl_records.append({
    "GLKCO": "", "GLDCT": "JE", "GLDOC": 999904, "GLDGJ": 126080,
    "GLJELN": 1.0, "GLCO": "", "GLMCU": "      100010", "GLAID": "100010.1110",
    "GLAA": 85000, "GLACR": 85000, "GLCRCD": "USD", "GLPOST": "P",
    "GLICUT": "G", "GLICU": 9994, "GLDICJ": 126080, "GLDSAV": 126080,
    "_ingested_at": "2026-09-23T06:00:00Z"
})
# DQ 5: Missing Document Number (GLDOC = 0) -> Severity: STOP
gl_records.append({
    "GLKCO": "00010", "GLDCT": "JE", "GLDOC": 0, "GLDGJ": 126080,
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.1110",
    "GLAA": 90000, "GLACR": 90000, "GLCRCD": "USD", "GLPOST": "P",
    "GLICUT": "G", "GLICU": 9995, "GLDICJ": 126080, "GLDSAV": 126080,
    "_ingested_at": "2026-09-23T06:00:00Z"
})
# DQ 6: Zero Amount -> Severity: WARNING
gl_records.append({
    "GLKCO": "00010", "GLDCT": "JE", "GLDOC": 999906, "GLDGJ": 126080,
    "GLJELN": 1.0, "GLCO": "00010", "GLMCU": "      100010", "GLAID": "100010.1110",
    "GLAA": 0, "GLACR": 0, "GLCRCD": "USD", "GLPOST": "P",
    "GLICUT": "G", "GLICU": 9996, "GLDICJ": 126080, "GLDSAV": 126080,
    "_ingested_at": "2026-09-23T06:00:00Z"
})

with open(f0911_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "GLKCO", "GLDCT", "GLDOC", "GLDGJ", "GLJELN", "GLCO", "GLMCU", "GLAID",
        "GLAA", "GLACR", "GLCRCD", "GLPOST", "GLICUT", "GLICU", "GLDICJ", "GLDSAV", "_ingested_at"
    ])
    writer.writeheader()
    writer.writerows(gl_records)

# -------------------------------------------------------------
# 12. Accounts Receivable Ledger: F03B11 (CRPOTA)
# Scenarios:
# - Current invoices (<30 days)
# - Aging 31-60 days past due
# - Aging 61-90 days past due
# - Aging 90+ days past due
# - Partial payment (Open amount < Gross amount)
# - Fully paid (Open amount = 0)
# - Credit memo (RM, negative amount)
# - Multi-Company fallback customer invoice (Customer 10008)
# -------------------------------------------------------------
f03b11_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F03B11_AR_Ledger.csv")
ar_records = [
    # Current invoice (<30 days)
    {"RPDOC": 300001, "RPDCT": "RI", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 10001, "RPDGJ": 126060, "RPDIVJ": 126090, "RPAG": 1500000, "RPAAP": 1500000, "RPCRCD": "USD", "RPPOST": "P", "AGING_BUCKET": "Current"},
    # Partially paid invoice
    {"RPDOC": 300002, "RPDCT": "RI", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 10002, "RPDGJ": 126040, "RPDIVJ": 126070, "RPAG": 2500000, "RPAAP": 1250000, "RPCRCD": "USD", "RPPOST": "P", "AGING_BUCKET": "Partially_Paid"},
    # Fully paid invoice
    {"RPDOC": 300003, "RPDCT": "RI", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 10003, "RPDGJ": 126010, "RPDIVJ": 126040, "RPAG": 800000, "RPAAP": 0, "RPCRCD": "USD", "RPPOST": "P", "AGING_BUCKET": "Fully_Paid"},
    # 31-60 Days Past Due
    {"RPDOC": 300004, "RPDCT": "RI", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 10007, "RPDGJ": 125330, "RPDIVJ": 125360, "RPAG": 1800000, "RPAAP": 1800000, "RPCRCD": "USD", "RPPOST": "P", "AGING_BUCKET": "31-60_Days"},
    # 61-90 Days Past Due
    {"RPDOC": 300005, "RPDCT": "RI", "RPKCO": "00020", "RPSFX": "001", "RPAN8": 10004, "RPDGJ": 125300, "RPDIVJ": 125330, "RPAG": 3200000, "RPAAP": 3200000, "RPCRCD": "CAD", "RPPOST": "P", "AGING_BUCKET": "61-90_Days"},
    # 90+ Days Severely Past Due
    {"RPDOC": 300006, "RPDCT": "RI", "RPKCO": "00030", "RPSFX": "001", "RPAN8": 10005, "RPDGJ": 125200, "RPDIVJ": 125230, "RPAG": 4500000, "RPAAP": 4500000, "RPCRCD": "EUR", "RPPOST": "P", "AGING_BUCKET": "90+_Days"},
    # Credit Memo / Return (RM)
    {"RPDOC": 300007, "RPDCT": "RM", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 10001, "RPDGJ": 126065, "RPDIVJ": 126065, "RPAG": -250000, "RPAAP": -250000, "RPCRCD": "USD", "RPPOST": "P", "AGING_BUCKET": "Credit_Memo"},
    # Multi-Company Fallback invoice: customer 10008 defined under company 00000
    {"RPDOC": 300008, "RPDCT": "RI", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 10008, "RPDGJ": 126075, "RPDIVJ": 126105, "RPAG": 1950000, "RPAAP": 1950000, "RPCRCD": "USD", "RPPOST": "P", "AGING_BUCKET": "Current"},
    # DQ Error Row: Due date earlier than invoice date -> QUARANTINE
    {"RPDOC": 300099, "RPDCT": "RI", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 10001, "RPDGJ": 126080, "RPDIVJ": 126010, "RPAG": 500000, "RPAAP": 500000, "RPCRCD": "USD", "RPPOST": "P", "AGING_BUCKET": "DQ_Error_Due_Before_Inv"},
]
with open(f03b11_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "RPDOC", "RPDCT", "RPKCO", "RPSFX", "RPAN8", "RPDGJ", "RPDIVJ", "RPAG", "RPAAP", "RPCRCD", "RPPOST", "AGING_BUCKET"
    ])
    writer.writeheader()
    writer.writerows(ar_records)

# -------------------------------------------------------------
# 13. Accounts Payable Ledger: F0411 (CRPOTA)
# Scenarios:
# - Open voucher
# - Paid voucher via electronic check (PK)
# - Discount taken under 210NET30
# - Voided voucher
# -------------------------------------------------------------
f0411_file = os.path.join(RAW_JDE_DIR, "CRPOTA.F0411_AP_Ledger.csv")
ap_records = [
    # Open voucher
    {"RPDOC": 400001, "RPDCT": "PV", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 50001, "RPDIVJ": 126050, "RPDDJ": 126080, "RPAG": 1200000, "RPAAP": 1200000, "RPCRCD": "USD", "STATUS": "OPEN"},
    # Paid voucher via Auto Check (PK)
    {"RPDOC": 400002, "RPDCT": "PV", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 50002, "RPDIVJ": 126020, "RPDDJ": 126080, "RPAG": 2400000, "RPAAP": 0, "RPCRCD": "USD", "STATUS": "PAID_EFT"},
    # Discounted voucher (2% taken under 210NET30)
    {"RPDOC": 400003, "RPDCT": "PV", "RPKCO": "00010", "RPSFX": "001", "RPAN8": 50006, "RPDIVJ": 126070, "RPDDJ": 126100, "RPAG": 1000000, "RPAAP": 0, "RPCRCD": "USD", "STATUS": "DISCOUNT_TAKEN"},
    # Overdue AP voucher
    {"RPDOC": 400004, "RPDCT": "PV", "RPKCO": "00020", "RPSFX": "001", "RPAN8": 50003, "RPDIVJ": 125300, "RPDDJ": 125330, "RPAG": 1750000, "RPAAP": 1750000, "RPCRCD": "CAD", "STATUS": "OVERDUE"},
]
with open(f0411_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "RPDOC", "RPDCT", "RPKCO", "RPSFX", "RPAN8", "RPDIVJ", "RPDDJ", "RPAG", "RPAAP", "RPCRCD", "STATUS"
    ])
    writer.writeheader()
    writer.writerows(ap_records)

# -------------------------------------------------------------
# 14. Real-Time Hub Upload Files (flatfile_repo_uploads/)
# Scenarios:
# 1. budget_targets_2026.csv (Valid upload)
# 2. manual_journal_adjustments_2026.csv (Valid adjustments)
# 3. budget_targets_malformed_test.csv (Missing headers, invalid numeric format to test pipeline exception handling)
# -------------------------------------------------------------
budget_file = os.path.join(FLATFILE_DIR, "budget_targets_2026.csv")
budget_data = [
    {"company_code": "00010", "business_unit": "100010", "object_account": "5010", "fiscal_year": 2026, "fiscal_period": 1, "budget_amount_usd": 450000.00},
    {"company_code": "00010", "business_unit": "100010", "object_account": "5010", "fiscal_year": 2026, "fiscal_period": 2, "budget_amount_usd": 475000.00},
    {"company_code": "00010", "business_unit": "100010", "object_account": "5010", "fiscal_year": 2026, "fiscal_period": 3, "budget_amount_usd": 510000.00},
    {"company_code": "00010", "business_unit": "100010", "object_account": "6010", "fiscal_year": 2026, "fiscal_period": 1, "budget_amount_usd": 280000.00},
    {"company_code": "00010", "business_unit": "100010", "object_account": "6010", "fiscal_year": 2026, "fiscal_period": 2, "budget_amount_usd": 295000.00},
    {"company_code": "00020", "business_unit": "100020", "object_account": "5010", "fiscal_year": 2026, "fiscal_period": 1, "budget_amount_usd": 120000.00},
    {"company_code": "00030", "business_unit": "100030", "object_account": "5010", "fiscal_year": 2026, "fiscal_period": 1, "budget_amount_usd": 185000.00},
]
with open(budget_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["company_code", "business_unit", "object_account", "fiscal_year", "fiscal_period", "budget_amount_usd"])
    writer.writeheader()
    writer.writerows(budget_data)

malformed_file = os.path.join(FLATFILE_DIR, "budget_targets_malformed_test.csv")
with open(malformed_file, "w", encoding="utf-8") as f:
    f.write("company_code,business_unit,object_account,fiscal_year,fiscal_period,budget_amount_usd\n")
    f.write("00010,100010,5010,2026,1,INVALID_AMOUNT\n") # String instead of decimal
    f.write(",100010,5010,2026,2,475000.00\n") # Missing company code
    f.write("00010,100010,5010,2099,99,-5000.00\n") # Invalid period and negative budget

# -------------------------------------------------------------
# 15. Metadata Framework (MDF) Enhanced Configuration & Rules
# -------------------------------------------------------------
meta_dataset_file = os.path.join(META_DIR, "meta_dataset_brz_to_silver.csv")
meta_datasets = [
    {
        "dataset_id": 1, "source_system": "AS400_DB2", "source_schema": "CRPOTA", "source_table": "F0911",
        "target_lakehouse": "lh_silver", "target_table": "General_Ledger",
        "ingestion_mode": "Batch", "primary_business_keys": "GLKCO,GLDCT,GLDOC,GLDGJ,GLJELN",
        "julian_date_columns": "GLDGJ,GLDICJ,GLDSAV", "currency_column": "GLCRCD", "unscaled_amount_columns": "GLAA,GLACR",
        "watermark_column": "GLDSAV", "is_active": 1
    },
    {
        "dataset_id": 2, "source_system": "AS400_DB2", "source_schema": "CRPOTA", "source_table": "F0901",
        "target_lakehouse": "lh_silver", "target_table": "DIM_Account",
        "ingestion_mode": "Batch", "primary_business_keys": "GMAID",
        "julian_date_columns": "", "currency_column": "", "unscaled_amount_columns": "",
        "watermark_column": "", "is_active": 1
    },
    {
        "dataset_id": 3, "source_system": "AS400_DB2", "source_schema": "CRPOTA", "source_table": "F03012",
        "target_lakehouse": "lh_silver", "target_table": "DIM_Customer",
        "ingestion_mode": "Batch", "primary_business_keys": "AIAN8,AICO",
        "julian_date_columns": "AIEFTB,AIEFTE", "currency_column": "AICRCA", "unscaled_amount_columns": "AICRAL",
        "watermark_column": "", "is_active": 1
    },
    {
        "dataset_id": 4, "source_system": "AS400_DB2", "source_schema": "CRPOTA", "source_table": "F03B11",
        "target_lakehouse": "lh_silver", "target_table": "Accounts_Receivable_Ledger",
        "ingestion_mode": "NRT", "primary_business_keys": "RPDOC,RPDCT,RPKCO,RPSFX",
        "julian_date_columns": "RPDGJ,RPDIVJ", "currency_column": "RPCRCD", "unscaled_amount_columns": "RPAG,RPAAP",
        "watermark_column": "RPDGJ", "is_active": 1
    },
    {
        "dataset_id": 5, "source_system": "AS400_DB2", "source_schema": "CRPOTA", "source_table": "F0401",
        "target_lakehouse": "lh_silver", "target_table": "DIM_Supplier",
        "ingestion_mode": "Batch", "primary_business_keys": "A6AN8,A6CO",
        "julian_date_columns": "", "currency_column": "A6CRCA", "unscaled_amount_columns": "",
        "watermark_column": "", "is_active": 1
    },
    {
        "dataset_id": 6, "source_system": "AS400_DB2", "source_schema": "CRPOTA", "source_table": "F0411",
        "target_lakehouse": "lh_silver", "target_table": "Accounts_Payable_Ledger",
        "ingestion_mode": "NRT", "primary_business_keys": "RPDOC,RPDCT,RPKCO,RPSFX",
        "julian_date_columns": "RPDIVJ,RPDDJ", "currency_column": "RPCRCD", "unscaled_amount_columns": "RPAG,RPAAP",
        "watermark_column": "RPDIVJ", "is_active": 1
    },
    {
        "dataset_id": 7, "source_system": "AS400_DB2", "source_schema": "CRPOTA", "source_table": "F0010",
        "target_lakehouse": "lh_silver", "target_table": "DIM_Company",
        "ingestion_mode": "Batch", "primary_business_keys": "CCCO",
        "julian_date_columns": "CCDSD", "currency_column": "CCCRCD", "unscaled_amount_columns": "",
        "watermark_column": "", "is_active": 1
    },
    {
        "dataset_id": 8, "source_system": "AS400_DB2", "source_schema": "CRPCTL", "source_table": "F0005",
        "target_lakehouse": "lh_silver", "target_table": "DIM_User_Defined_Codes",
        "ingestion_mode": "Batch", "primary_business_keys": "DRSY,DRRT,DRKY",
        "julian_date_columns": "", "currency_column": "", "unscaled_amount_columns": "",
        "watermark_column": "", "is_active": 1
    },
    {
        "dataset_id": 9, "source_system": "AS400_DB2", "source_schema": "CRPOTA", "source_table": "F1201",
        "target_lakehouse": "lh_silver", "target_table": "DIM_Asset",
        "ingestion_mode": "Batch", "primary_business_keys": "FA#UMB",
        "julian_date_columns": "FAINSD", "currency_column": "", "unscaled_amount_columns": "",
        "watermark_column": "", "is_active": 1
    },
    {
        "dataset_id": 10, "source_system": "AS400_DB2", "source_schema": "CRPOTA", "source_table": "F1202",
        "target_lakehouse": "lh_silver", "target_table": "DIM_Asset_Account_Balance",
        "ingestion_mode": "Batch", "primary_business_keys": "FA#UMB,FACO,FAFY,FALEDG",
        "julian_date_columns": "", "currency_column": "", "unscaled_amount_columns": "FAHISTCOST,FAACCDEP,FANETBKVAL",
        "watermark_column": "", "is_active": 1
    },
]
with open(meta_dataset_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "dataset_id", "source_system", "source_schema", "source_table", "target_lakehouse", "target_table",
        "ingestion_mode", "primary_business_keys", "julian_date_columns", "currency_column",
        "unscaled_amount_columns", "watermark_column", "is_active"
    ])
    writer.writeheader()
    writer.writerows(meta_datasets)

# Comprehensive Data Quality Rules Table covering 11 Scenarios
meta_dq_file = os.path.join(META_DIR, "meta_dataquality_rules.csv")
meta_dq_rules = [
    # General Ledger Rules
    {"rule_id": 101, "dataset_id": 1, "target_table": "General_Ledger", "column_name": "document_number", "check_type": "MANDATORY_PK", "rule_condition": "document_number IS NOT NULL AND document_number > 0", "severity": "STOP", "description": "Halts execution if primary document number is missing"},
    {"rule_id": 102, "dataset_id": 1, "target_table": "General_Ledger", "column_name": "gl_date", "check_type": "VALID_JULIAN_RANGE", "rule_condition": "gl_date IS NOT NULL AND gl_date BETWEEN 90001 AND 199366", "severity": "QUARANTINE", "description": "Routes malformed Julian dates (<1990 or >2099 or day>366) to quarantine"},
    {"rule_id": 103, "dataset_id": 1, "target_table": "General_Ledger", "column_name": "amount", "check_type": "NON_ZERO_BALANCE", "rule_condition": "amount != 0.00", "severity": "WARNING", "description": "Alerts on zero-dollar GL journal lines"},
    {"rule_id": 104, "dataset_id": 1, "target_table": "General_Ledger", "column_name": "company_code", "check_type": "NOT_BLANK", "rule_condition": "length(trim(company_code)) > 0", "severity": "QUARANTINE", "description": "Routes lines with missing company codes to quarantine"},
    {"rule_id": 105, "dataset_id": 1, "target_table": "General_Ledger", "column_name": "currency_code", "check_type": "VALID_CURRENCY", "rule_condition": "currency_code IN ('USD','CAD','EUR','GBP','JPY','BRL','KWD')", "severity": "QUARANTINE", "description": "Ensures currency code exists in F0013 ISO master"},
    # AR Ledger Rules
    {"rule_id": 201, "dataset_id": 4, "target_table": "Accounts_Receivable_Ledger", "column_name": "invoice_due_date", "check_type": "DATE_CHRONOLOGY", "rule_condition": "invoice_due_date >= invoice_date", "severity": "QUARANTINE", "description": "Invoice due date cannot be earlier than invoice creation date"},
    {"rule_id": 202, "dataset_id": 4, "target_table": "Accounts_Receivable_Ledger", "column_name": "open_amount", "check_type": "AMOUNT_LOGIC", "rule_condition": "abs(open_amount) <= abs(gross_amount)", "severity": "QUARANTINE", "description": "Open amount cannot exceed gross transaction amount"},
    # Customer Master Rules
    {"rule_id": 301, "dataset_id": 3, "target_table": "DIM_Customer", "column_name": "credit_limit", "check_type": "NON_NEGATIVE", "rule_condition": "credit_limit >= 0", "severity": "WARNING", "description": "Flags customers with negative credit limits"},
    {"rule_id": 302, "dataset_id": 3, "target_table": "DIM_Customer", "column_name": "customer_address_number", "check_type": "MANDATORY_PK", "rule_condition": "customer_address_number IS NOT NULL AND customer_address_number > 0", "severity": "STOP", "description": "Customer address number must be positive and non-null"},
    # Fixed Asset Master Rules
    {"rule_id": 401, "dataset_id": 10, "target_table": "DIM_Asset_Account_Balance", "column_name": "accumulated_depreciation", "check_type": "ASSET_BOOK_VALUE", "rule_condition": "accumulated_depreciation <= historical_cost", "severity": "QUARANTINE", "description": "Accumulated depreciation cannot exceed original historical acquisition cost"},
]
with open(meta_dq_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "rule_id", "dataset_id", "target_table", "column_name", "check_type", "rule_condition", "severity", "description"
    ])
    writer.writeheader()
    writer.writerows(meta_dq_rules)

# -------------------------------------------------------------
# 16. Generate Detailed Scenario Catalog: scenarios/test_scenarios_matrix.md
# -------------------------------------------------------------
scenarios_md = os.path.join(SCENARIOS_DIR, "test_scenarios_matrix.md")
with open(scenarios_md, "w", encoding="utf-8") as f:
    f.write("""# IPS BI Modernization — Test Scenarios Matrix & Data Catalog

This catalog outlines the 11 key enterprise testing scenarios covered by the generated datasets in `data/`:

| Scenario ID | Scenario Name | Target Entity / File | Key Test Records / Condition | Expected Engine Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **SC-01** | **Julian Date Boundaries** | `F0911_GL_Ledger.csv` | `GLDGJ = 124060` (Feb 29, 2024)<br/>`GLDGJ = 124366` (Dec 31, 2024 leap)<br/>`GLDGJ = 099365` (Dec 31, 1999) | Correctly parses leap day, 366th day, and C=0 1900s century boundary to Gregorian `YYYY-MM-DD`. |
| **SC-02** | **Multi-Currency & Dual Valuation** | `F0911_GL_Ledger.csv` | Doc 100016: EUR €10,000 (@ 1.085 FX)<br/>Doc 100017: JPY ¥5,000,000 (@ 0.0065 FX) | Preserves domestic `GLAA` ($) and foreign `GLACR` (€/¥). Scales JPY with 0 decimals and converts reporting USD. |
| **SC-03** | **SCD Type 2 Historical Tracking** | `F03012_Customer_Master.csv`<br/>`F0116_Address_By_Date.csv` | Cust 10001 (Credit rating B1 -> A1)<br/>Cust 10002 (Relocation Dallas -> Austin) | Creates distinct historical versions with `effective_start_date`, `effective_end_date`, and `is_current` flags. |
| **SC-04** | **Multi-Company Hierarchical Fallback** | `F03012_Customer_Master.csv`<br/>`F03B11_AR_Ledger.csv` | Customer 10008 linked to Company 00000 | Ingestion applies `F03B1.RPCO -> Company 00000` fallback without orphan lookup errors. |
| **SC-05** | **Default Member / Orphan Fact** | `F0911_GL_Ledger.csv` | Doc 100019: `GLAID = '999999.9999'` | Surrogate key lookups safely resolve to default member `row_id = -1` ('Unknown/Not Applicable'). |
| **SC-06** | **CDC Deduplication & Window Ranking** | `F0911_GL_Ledger.csv` | Doc 777001 (Duplicate row with older `04:00Z` vs newer `07:30Z` timestamp) | `row_number() over (partition by keys order by _ingested_at desc)` discards older record and preserves latest $1,250.00 amount. |
| **SC-07A** | **Data Quality Severity: STOP** | `F0911_GL_Ledger.csv` | Doc 0 (`GLDOC = 0`) | Rule 101 halts the pipeline immediately to prevent corrupt primary keys. |
| **SC-07B** | **Data Quality Severity: QUARANTINE** | `F0911_GL_Ledger.csv`<br/>`F03B11_AR_Ledger.csv` | Doc 999901 (`GLDGJ = 124400` Day 400)<br/>Doc 999904 (`GLCO = ''` Blank Co)<br/>Doc 300099 (Due Date < Inv Date) | Diverts corrupted records into `silver.{target}_quarantine` while valid records continue flowing to Silver Lakehouse. |
| **SC-07C** | **Data Quality Severity: WARNING** | `F0911_GL_Ledger.csv` | Doc 999906 (`GLAA = 0`) | Logs audit warning to `log.dq_rule_run` without halting or quarantining. |
| **SC-08** | **Fixed Assets & Depreciation** | `F1201_Asset_Master.csv`<br/>`F1202_Asset_Balances.csv` | CNC Station (#1001), Robotic Arm (#1002) | Calculates Net Book Value = Historical Cost - Accumulated Depreciation. |
| **SC-09** | **AR Aging Buckets & Credit Memos** | `F03B11_AR_Ledger.csv` | Invoices across Current, 30-60, 61-90, 90+ days, partial pay, and Credit Memo (RM) | Feeds Power BI aging matrix and DSO (Days Sales Outstanding) measures. |
| **SC-10** | **AP Vouchers & Discounts** | `F0411_AP_Ledger.csv` | Vouchers open, paid via EFT (PK), and 2% discount taken under `210NET30` | Validates cash management, discount realization, and AP liability. |
| **SC-11** | **Real-Time Hub Automated Ingestion** | `flatfile_repo_uploads/` | Valid budget vs malformed test file (`budget_targets_malformed_test.csv`) | Tests Data Activator blob triggers and error isolation for manual user uploads. |
""")

print("Successfully generated all multi-scenario datasets and test_scenarios_matrix.md!")
