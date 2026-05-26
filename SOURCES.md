# SOURCES.md

This document explains the real-world formats researched for each source, what was learned, why the sample data looks the way it does, and what could break in a real deployment.

## 1. SAP Fuel and Procurement Data

### Format researched

I researched SAP-style exports for material, fuel, and procurement activity data.

SAP systems can expose data through multiple integration styles, including:

- flat-file exports
- IDocs
- BAPI calls
- OData services
- material document APIs

For this prototype, I chose a flat-file CSV export.

### What I learned

SAP data is often not immediately analyst-friendly. It may include:

- plant codes
- material codes
- purchase document numbers
- vendor references
- cost centers
- inconsistent unit names
- different date formats
- language-specific headers

Some SAP exports can use German-style headers such as:

- `Buchungsdatum` for posting date
- `Werk` for plant
- `Menge` for quantity
- `MEINS` for unit

### Sample data design

The SAP sample file includes:

- German headers
- mixed date formats
- plant codes such as `BLR01` and `BLR02`
- fuel material rows such as `DIESEL` and `PETROL`
- procurement row such as `PROC_STEEL`
- mixed units such as `LTR`, `L`, and `KG`
- one unknown plant
- one negative quantity

This was intentional because real SAP exports are rarely perfectly clean.

### What would break in real deployment

A real deployment would need to handle:

- client-specific SAP column names
- different languages
- missing plant/material master data
- very large files
- SAP API authentication
- IDoc or OData payloads instead of CSV
- duplicate records across exports

## 2. Utility Electricity Data

### Format researched

I researched typical electricity bill and utility portal data structures.

Facilities teams may collect electricity data from:

- utility portal CSV exports
- PDF bills
- manual spreadsheets
- utility APIs if available

For this prototype, I chose utility portal CSV upload.

### What I learned

Electricity data usually contains:

- site or account code
- meter number
- billing/service period
- opening meter reading
- closing meter reading
- usage in kWh
- demand value
- tariff or rate code
- total billed amount
- actual or estimated reading status

Billing periods do not always align with calendar months, which matters for ESG reporting.

### Sample data design

The utility sample file includes:

- site codes
- meter numbers
- service from and service to dates
- opening and closing readings
- usage kWh
- demand values
- tariff code
- actual and estimated readings
- one missing meter number
- one usage mismatch

This tests both normal and suspicious electricity records.

### What would break in real deployment

A real deployment would need to handle:

- PDF-only bills
- scanned bills
- different utility provider templates
- multiple meters per facility
- overlapping billing periods
- bills crossing calendar months
- tariff changes
- missing or estimated readings

## 3. Corporate Travel Data

### Format researched

I researched Concur/Navan-style corporate travel and expense exports.

Travel platforms can expose data through APIs or exports, usually containing trip, expense, category, amount, and employee information.

For this prototype, I chose a Concur-like CSV export.

### What I learned

Business travel data can include:

- employee ID
- trip ID
- expense category
- transaction date
- flight origin and destination airport codes
- distance if available
- hotel nights
- ground transport distance
- amount
- currency

Distances are not always provided. Sometimes only airport codes are available, so the system should not blindly assume distance.

### Sample data design

The travel sample file includes:

- flight row with missing distance
- hotel row with nights
- taxi row with distance
- flight row with missing destination airport
- unknown category row

This shows realistic review cases for corporate travel data.

### What would break in real deployment

A real deployment would need to handle:

- live API authentication
- platform-specific category names
- duplicate trips
- missing airport codes
- automatic airport distance calculation
- currency conversion
- employee privacy controls
- trip amendments and cancellations