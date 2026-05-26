# TRADEOFFS.md

This document explains three things I deliberately did not build and why.

## 1. PDF OCR for Utility Bills

I did not build PDF extraction or OCR for electricity bills.

### Why

Utility PDF bills are realistic, but PDF extraction depends on bill layout, scan quality, utility provider format, and OCR accuracy. Building a reliable PDF parser would take significant time and could distract from the main assignment goal.

For this prototype, I chose utility portal CSV uploads so the system can focus on:

- billing periods
- meter readings
- kWh usage
- demand values
- tariff codes
- estimated readings
- analyst review

### Future improvement

A production version could add PDF extraction using provider-specific templates and human review for low-confidence extracted values.

## 2. Live SAP and Travel Platform Integrations

I did not build live SAP, Concur, or Navan API integrations.

### Why

Live enterprise integrations require credentials, OAuth setup, network access, tenant permissions, and client-side approval. These are not available for a 4-day prototype.

Instead, I modeled realistic exported data shapes using CSV uploads. This still demonstrates the core challenge: ingesting messy source data, normalizing it, flagging issues, and preparing it for analyst review.

### Future improvement

A production version could add:

- SAP OData connector
- IDoc ingestion
- Concur/Navan API connector
- scheduled sync jobs
- retry and failure monitoring

## 3. Carbon Emission Calculation Engine

I did not build a full carbon calculation engine.

### Why

The assignment clearly states that the hard part is not computing carbon, but ingesting and normalizing messy client data. So this prototype focuses on activity-data readiness.

The system prepares reviewed and locked activity records that can later be passed to an emission factor engine.

### Future improvement

A production version could add:

- emission factor tables
- region-specific electricity factors
- fuel-specific factors
- travel-category factors
- calculated CO2e values
- auditor-ready calculation reports