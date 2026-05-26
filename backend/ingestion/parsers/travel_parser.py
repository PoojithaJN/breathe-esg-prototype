from ingestion.services.normalizer import parse_date, normalize_quantity, to_decimal


def parse_travel_row(row, tenant, facilities):
    category = row.get("category", "").strip().lower()

    if category == "hotel":
        quantity = row.get("nights")
        unit = "nights"
        normalized_quantity = to_decimal(quantity)
        normalized_unit = "nights"
    else:
        quantity = row.get("distance_km")
        normalized_quantity, normalized_unit = normalize_quantity(quantity, "km")

    return {
        "source_type": "TRAVEL",
        "scope": "SCOPE_3",
        "category": category,
        "activity_date": parse_date(row.get("transaction_date")),
        "period_start": None,
        "period_end": None,
        "facility": None,
        "quantity": normalized_quantity,
        "original_unit": "nights" if category == "hotel" else "km",
        "normalized_quantity": normalized_quantity,
        "normalized_unit": normalized_unit,
        "amount": to_decimal(row.get("amount")),
        "currency": row.get("currency", "").strip(),
        "source_reference": row.get("trip_id", ""),
        "origin_airport": row.get("origin_airport", "").strip(),
        "destination_airport": row.get("destination_airport", "").strip(),
        "nights": to_decimal(row.get("nights")),
    }