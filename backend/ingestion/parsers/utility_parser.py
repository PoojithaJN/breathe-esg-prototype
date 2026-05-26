from ingestion.services.normalizer import parse_date, normalize_quantity, to_decimal


def parse_utility_row(row, tenant, facilities):
    site_code = row.get("site_code", "").strip()
    facility = facilities.get(site_code)

    usage = row.get("usage_kwh")
    normalized_quantity, normalized_unit = normalize_quantity(usage, "kWh")

    return {
        "source_type": "UTILITY",
        "scope": "SCOPE_2",
        "category": "Electricity",
        "activity_date": None,
        "period_start": parse_date(row.get("service_from")),
        "period_end": parse_date(row.get("service_to")),
        "facility": facility,
        "quantity": normalized_quantity,
        "original_unit": "kWh",
        "normalized_quantity": normalized_quantity,
        "normalized_unit": normalized_unit or "kWh",
        "amount": to_decimal(row.get("total_amount")),
        "currency": "INR",
        "source_reference": row.get("meter_no", ""),
        "meter_no": row.get("meter_no", "").strip(),
        "opening_reading": to_decimal(row.get("opening_reading")),
        "closing_reading": to_decimal(row.get("closing_reading")),
        "reading_type": row.get("reading_type", ""),
    }