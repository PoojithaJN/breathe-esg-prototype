from ingestion.services.normalizer import parse_date, normalize_quantity


def parse_sap_row(row, tenant, facilities):
    posting_date = parse_date(row.get("Buchungsdatum"))
    plant_code = row.get("Werk", "").strip()
    material_code = row.get("Material", "").strip()
    quantity = row.get("Menge")
    unit = row.get("MEINS")

    normalized_quantity, normalized_unit = normalize_quantity(quantity, unit)

    facility = facilities.get(plant_code)

    if material_code.upper() in ["DIESEL", "PETROL", "FUEL"]:
        scope = "SCOPE_1"
        category = "Fuel"
    else:
        scope = "SCOPE_3"
        category = "Procurement"

    return {
        "source_type": "SAP",
        "scope": scope,
        "category": category,
        "activity_date": posting_date,
        "period_start": None,
        "period_end": None,
        "facility": facility,
        "quantity": normalized_quantity,
        "original_unit": unit or "",
        "normalized_quantity": normalized_quantity,
        "normalized_unit": normalized_unit or "",
        "amount": None,
        "currency": "",
        "source_reference": row.get("Einkaufsbeleg", ""),
        "material_code": material_code,
    }