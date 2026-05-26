# MODEL.md

The data model is designed around traceability, normalization, analyst review, and audit readiness.

The original uploaded source row is never overwritten. Each row is first stored as a `RawRecord`. A normalized `EmissionActivity` is then created from that raw row. Analysts can review and edit the normalized record, but the original raw row remains available as source-of-truth evidence.

## Main Design Goals

1. Multi-tenancy
2. Scope 1/2/3 categorization
3. Source-of-truth tracking
4. Unit normalization
5. Analyst review
6. Audit trail
7. Locking approved rows for audit

## Tenant

`Tenant` represents a client company.

Every upload, facility, raw record, normalized activity, and audit log is connected to a tenant. This supports multi-tenancy because the system can separate data by client.

## Facility

`Facility` stores plant or site information.

This is needed because SAP plant codes and utility site codes are not meaningful by themselves. For example:

- `BLR01` maps to Bangalore Manufacturing Plant
- `BLR02` maps to Bangalore Office Campus

SAP and utility rows can then be linked to a known facility.

## SourceUpload

`SourceUpload` represents one uploaded file.

It stores:

- tenant
- source type
- original file name
- uploaded user
- upload timestamp
- processing status
- total rows
- successful rows
- failed rows
- suspicious rows

This helps answer which file produced the data and when it entered the system.

## RawRecord

`RawRecord` stores the original row exactly as received from the source file.

For example, a SAP row may contain:

```json
{
  "Buchungsdatum": "31.12.2025",
  "Werk": "BLR01",
  "Material": "DIESEL",
  "Menge": "450",
  "MEINS": "LTR"
}

```

This row is stored without changing the source column names or values.

This is important for auditability because analysts and auditors can compare the normalized row against the original source row.

## EmissionActivity

`EmissionActivity` is the normalized ESG activity row.

It stores:

- tenant
- raw record reference
- source type
- Scope 1/2/3
- category
- activity date or billing period
- facility
- original quantity and unit
- normalized quantity and unit
- amount and currency
- validation status
- suspicious flags
- approval details
- lock status
- source reference

## Scope Mapping

The prototype uses this mapping:

- SAP fuel data → Scope 1
- Utility electricity data → Scope 2
- Corporate travel data → Scope 3
- SAP procurement data → Scope 3

## Unit Normalization

The system normalizes common unit variations.

Examples:

- `LTR`, `L`, `Liter` → `litre`
- `MWh` → `kWh`
- `km` → `km`
- `nights` → `nights`

The normalized value is stored separately from the original value so the analyst can see both.

## Suspicious Flags

Rows are not blindly accepted. Validation rules add flags such as:

- negative quantity
- unknown plant code
- missing meter number
- estimated meter reading
- usage mismatch
- flight distance missing
- unknown travel category

These flags help analysts focus on rows that need review.

## AuditLog

`AuditLog` stores important actions:

- record created from upload
- analyst update
- approval
- rejection
- locking for audit

Each log stores:

- tenant
- activity
- action
- old value
- new value
- performed by
- performed at

## Locking

Approved rows can be locked for audit.

Once locked, the record cannot be edited through the normal analyst flow. This protects the reviewed dataset from accidental changes before audit.

## Why RawRecord and EmissionActivity are separate

`RawRecord` preserves the original source-of-truth. `EmissionActivity` stores the clean business version used for review and audit.

This separation avoids losing original client data when analysts correct or normalize values.