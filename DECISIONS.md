# DECISIONS.md

This document explains the main choices made for the prototype and the reasoning behind them.

## 1. SAP Ingestion Decision

I chose CSV file upload for SAP fuel and procurement data.

SAP systems can expose data through formats like IDoc, OData services, BAPI calls, and flat-file exports. For this prototype, I chose a flat-file CSV export because enterprise onboarding often starts with exported reports before full API access is approved.

### Subset handled

The prototype handles:

- German column headers
- posting date
- plant code
- material code
- quantity
- unit
- purchase document
- vendor
- cost center
- fuel rows
- procurement rows

### Why this choice

Direct SAP API integration would require client credentials, SAP system access, configuration, and approval from the client’s SAP team. A CSV export is more realistic for a 4-day prototype and still captures SAP data problems such as inconsistent units, plant codes, German headers, and messy date formats.

### Ignored for this prototype

- Live SAP OData integration
- IDoc parsing
- BAPI calls
- Material master synchronization
- Large file streaming

### Questions I would ask the PM

- Which SAP module or report will the client export from?
- Are plant and material master lookup tables available?
- Are fuel records purchase records, consumption records, or both?
- Should procurement rows later use spend-based or material-based emission factors?

## 2. Utility Electricity Ingestion Decision

I chose utility portal CSV upload for electricity data.

Facilities teams may receive electricity data through PDFs, utility portals, manual spreadsheets, or APIs. For this prototype, I chose portal CSV exports.

### Subset handled

The prototype handles:

- site code
- meter number
- service from date
- service to date
- opening reading
- closing reading
- usage kWh
- demand value
- tariff code
- total amount
- reading type

### Why this choice

PDF bills are realistic, but PDF extraction and OCR can become a separate project. CSV still allows the prototype to handle important electricity data issues such as billing periods, meter readings, kWh usage, estimated readings, tariff codes, and usage mismatches.

### Ignored for this prototype

- PDF OCR
- Utility API integration
- Tariff charge calculation
- Calendar-month allocation of bills
- Multiple utility provider templates

### Questions I would ask the PM

- Which utility providers are involved?
- Are bills available as CSV, PDF, or both?
- Should billing periods be split across calendar months?
- Should estimated readings be accepted or always reviewed?

## 3. Corporate Travel Ingestion Decision

I chose Concur-like CSV upload for business travel data.

Travel platforms like Concur or Navan can expose data through APIs, but live API access requires tenant credentials, OAuth setup, and permissions. For this prototype, I modeled a realistic travel export as CSV.

### Subset handled

The prototype handles:

- employee ID
- trip ID
- category
- transaction date
- origin airport
- destination airport
- distance km
- hotel nights
- amount
- currency

### Why this choice

A CSV/API-shaped export is enough to model the ingestion problem without spending time on external authentication. It also allows the prototype to handle realistic travel issues such as missing distance, missing airport codes, unknown categories, and different activity units.

### Ignored for this prototype

- Live Concur/Navan API integration
- OAuth setup
- Automatic airport distance calculation
- Currency conversion
- Duplicate detection across reports

### Questions I would ask the PM

- Which travel platform does the client use?
- Are airport codes always available for flights?
- Should missing distances be estimated automatically or sent to analysts?
- Should hotel stays be normalized by nights or spend?

## 4. Review and Locking Decision

I chose a review-first workflow.

Rows are not directly treated as final after upload. They are stored as `NEEDS_REVIEW` and suspicious flags are shown to the analyst.

### Why this choice

ESG data often goes to auditors, so traceability matters. Analysts should be able to inspect raw rows, understand normalization, approve valid rows, reject wrong rows, and lock approved rows.

## 5. Carbon Calculation Decision

I did not build a carbon calculation engine.

### Why this choice

The assignment says the hard part is not computing carbon, but ingesting and normalizing messy client data. This prototype focuses on preparing clean, reviewed activity data that can later be passed to an emission factor engine.