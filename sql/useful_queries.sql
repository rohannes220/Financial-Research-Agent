SELECT c.ticker,f.concept,f.end,f.value,f.unit,f.form
FROM financial_facts f JOIN companies c ON c.id=f.company_id
WHERE c.ticker='MSFT' AND f.concept IN ('RevenueFromContractWithCustomerExcludingAssessedTax','Revenues')
ORDER BY f.end DESC LIMIT 20;

SELECT fi.form,fi.filed_at,COUNT(*) chunks
FROM filing_chunks fc JOIN filings fi ON fi.id=fc.filing_id
GROUP BY fi.id,fi.form,fi.filed_at ORDER BY fi.filed_at DESC;
