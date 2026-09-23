-- ===================================================================================================
-- Microsoft Fabric SQL Analytics Endpoint / Warehouse DDL
-- Database: wh_ips_gold
-- Schemas: staging, dim, fact, rpt
-- Description: Star schema analytical definitions for AS400 DB2 ERP financial mart
-- ===================================================================================================

CREATE SCHEMA IF NOT EXISTS dim;
GO
CREATE SCHEMA IF NOT EXISTS fact;
GO
CREATE SCHEMA IF NOT EXISTS rpt;
GO

-- 1. Dim_Company View
CREATE OR ALTER VIEW dim.Dim_Company AS
SELECT 
    company_code AS CompanyKey,
    company_name AS CompanyName,
    currency_code AS BaseCurrency,
    fiscal_year_start_month AS FiscalYearStartMonth
FROM lh_ips_gold.Dim_Company;
GO

-- 2. Dim_Account View (Handling Unknown Member -1)
CREATE OR ALTER VIEW dim.Dim_Account AS
SELECT 
    account_id AS AccountKey,
    company_code AS CompanyCode,
    business_unit AS BusinessUnit,
    object_account AS ObjectAccount,
    sub_ledger AS SubLedger,
    account_description AS AccountDescription,
    posting_edit_code AS PostingEditCode,
    CASE 
        WHEN object_account BETWEEN '1000' AND '1999' THEN 'Assets'
        WHEN object_account BETWEEN '2000' AND '2999' THEN 'Liabilities'
        WHEN object_account BETWEEN '3000' AND '3999' THEN 'Equity'
        WHEN object_account BETWEEN '5000' AND '5999' THEN 'Revenue'
        WHEN object_account BETWEEN '6000' AND '6999' THEN 'Cost of Goods Sold'
        WHEN object_account BETWEEN '7000' AND '8999' THEN 'Operating Expenses'
        ELSE 'Other'
    END AS AccountFinancialClass
FROM lh_ips_gold.Dim_Account;
GO

-- 3. Fact_GeneralLedger View
CREATE OR ALTER VIEW fact.Fact_GeneralLedger AS
SELECT 
    document_number AS DocumentNumber,
    document_type AS DocumentType,
    line_number AS LineNumber,
    accounting_date AS AccountingDate,
    account_key AS AccountKey,
    company_key AS CompanyKey,
    amount_domestic AS AmountDomestic,
    amount_foreign AS AmountForeign,
    currency_code AS CurrencyCode,
    posted_code AS PostedCode
FROM lh_ips_gold.Fact_GeneralLedger;
GO

-- 4. Executive Summary Reporting View
CREATE OR ALTER VIEW rpt.ExecutiveFinancialSummary AS
SELECT 
    c.CompanyName,
    f.AccountingDate,
    YEAR(f.AccountingDate) AS FiscalYear,
    MONTH(f.AccountingDate) AS FiscalMonth,
    a.AccountFinancialClass,
    SUM(f.AmountDomestic) AS TotalAmountDomestic
FROM fact.Fact_GeneralLedger f
INNER JOIN dim.Dim_Company c ON f.CompanyKey = c.CompanyKey
INNER JOIN dim.Dim_Account a ON f.AccountKey = a.AccountKey
GROUP BY 
    c.CompanyName,
    f.AccountingDate,
    YEAR(f.AccountingDate),
    MONTH(f.AccountingDate),
    a.AccountFinancialClass;
GO
