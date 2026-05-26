def validate_common(quantity, normalized_unit):
    flags = []

    if quantity is None:
        flags.append("Missing or invalid quantity")

    if quantity is not None and quantity < 0:
        flags.append("Negative quantity")

    if not normalized_unit:
        flags.append("Unknown or missing unit")

    return flags


def validate_sap(data):
    flags = validate_common(data.get("quantity"), data.get("normalized_unit"))

    if not data.get("facility"):
        flags.append("Unknown plant code")

    if not data.get("material_code"):
        flags.append("Missing material code")

    if not data.get("activity_date"):
        flags.append("Invalid or missing posting date")

    return flags


def validate_utility(data):
    flags = validate_common(data.get("quantity"), data.get("normalized_unit"))

    if not data.get("meter_no"):
        flags.append("Missing meter number")

    if not data.get("period_start") or not data.get("period_end"):
        flags.append("Invalid billing period")

    if data.get("period_start") and data.get("period_end"):
        if data["period_end"] < data["period_start"]:
            flags.append("Billing period end date is before start date")

    opening = data.get("opening_reading")
    closing = data.get("closing_reading")
    usage = data.get("quantity")

    if opening is not None and closing is not None and usage is not None:
        calculated = closing - opening
        if calculated != usage:
            flags.append("Usage kWh does not match meter reading difference")

    if str(data.get("reading_type", "")).upper() == "ESTIMATED":
        flags.append("Estimated meter reading")

    return flags


def validate_travel(data):
    flags = []

    category = data.get("category")

    allowed_categories = ["flight", "hotel", "taxi", "rail", "car_rental"]

    if category not in allowed_categories:
        flags.append("Unknown travel category")

    if category == "flight":
        if not data.get("origin_airport") or not data.get("destination_airport"):
            flags.append("Flight missing airport code")
        if data.get("quantity") is None:
            flags.append("Flight distance missing")

    if category == "hotel":
        if data.get("nights") is None or data.get("nights") <= 0:
            flags.append("Hotel nights missing or invalid")

    if category in ["taxi", "rail", "car_rental"]:
        if data.get("quantity") is None:
            flags.append("Travel distance missing")

    if not data.get("currency"):
        flags.append("Missing currency")

    return flags