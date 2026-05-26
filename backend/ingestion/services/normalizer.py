from datetime import datetime
from decimal import Decimal, InvalidOperation


def parse_date(value):
    if not value:
        return None

    value = str(value).strip()

    formats = [
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%d-%m-%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


def to_decimal(value):
    if value in [None, ""]:
        return None

    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None


def normalize_unit(unit):
    if not unit:
        return "", None

    unit_clean = str(unit).strip().lower()

    mappings = {
        "ltr": ("litre", Decimal("1")),
        "l": ("litre", Decimal("1")),
        "liter": ("litre", Decimal("1")),
        "litre": ("litre", Decimal("1")),
        "kg": ("kg", Decimal("1")),
        "kwh": ("kWh", Decimal("1")),
        "mwh": ("kWh", Decimal("1000")),
        "km": ("km", Decimal("1")),
        "nights": ("nights", Decimal("1")),
    }

    return mappings.get(unit_clean, (unit, None))


def normalize_quantity(quantity, unit):
    decimal_quantity = to_decimal(quantity)
    normalized_unit, multiplier = normalize_unit(unit)

    if decimal_quantity is None or multiplier is None:
        return decimal_quantity, normalized_unit

    return decimal_quantity * multiplier, normalized_unit