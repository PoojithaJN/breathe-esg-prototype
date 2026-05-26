# Breathe ESG Data Ingestion & Analyst Review Prototype

This is a Django REST and React prototype built for the Breathe ESG Tech Intern Assignment.

The system ingests ESG activity data from three source types:

1. SAP fuel and procurement CSV export
2. Utility electricity portal CSV export
3. Corporate travel CSV export

It stores the original raw row, normalizes it into a common ESG activity model, flags suspicious records, and allows analysts to review, approve, reject, and lock rows before audit.

## Core Flow

Upload CSV  
→ Store original row as RawRecord  
→ Normalize into EmissionActivity  
→ Add validation flags  
→ Analyst reviews row  
→ Analyst approves or rejects  
→ Approved row is locked for audit  
→ AuditLog records every action

## Tech Stack

### Backend
- Django
- Django REST Framework
- Token Authentication
- SQLite for local development
- PostgreSQL-ready for deployment

### Frontend
- React
- Vite
- Axios
- React Router

## Source Types Handled

### SAP Fuel & Procurement
Handles SAP-style CSV exports with:
- German column headers
- plant codes
- material codes
- mixed date formats
- inconsistent units
- fuel and procurement rows

### Utility Electricity
Handles utility portal CSV exports with:
- meter number
- service/billing period
- opening and closing readings
- kWh usage
- demand value
- tariff code
- reading type

### Corporate Travel
Handles travel CSV exports with:
- flights
- hotels
- taxi/ground transport
- airport codes
- distances
- nights
- amount and currency

## Demo Login

Username: admin  
Password: Demo@123

## Local Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

Backend runs on:

```text
http://127.0.0.1:8000
```

## Sample Data

Sample CSV files are included in the `sample_data` folder:

- `sap_sample.csv`
- `utility_sample.csv`
- `travel_sample.csv`

These files include both clean and suspicious rows to demonstrate validation and analyst review.

## Important Documentation

- `MODEL.md` explains the data model and audit design
- `DECISIONS.md` explains source-format decisions and assumptions
- `TRADEOFFS.md` explains what was deliberately not built
- `SOURCES.md` explains real-world source research and sample data design

## Deployment

The backend is prepared for Render deployment and the frontend is prepared for Vercel deployment.

For deployed review, use the submitted live frontend URL and demo credentials.