import re
from decimal import Decimal

def substation_type_map(*aliases):
    keys = ["primary", "bsp", "gsp"]
    return {alias: key for alias, key in zip(aliases, keys)}

VOLTAGE_LEVELS = [
    "6.6",
    "11.0",
    "25.0",
    "33.0",
    "66.0",
    "132.0",
]

SUBSTRINGS_TO_REMOVE = [
        "kv",
        "kV",
        "Kv",
        "KV",
        "Bsp",
        "S.G.P.",
        "S.G.P",
        "G.S.P",
        "S Stn",
        "Primary Substation",
        "S/S",
        "S/Stn",
        "Power Station",
        "Primary",
        "National Grid Site",
        "S Stn",
        "340038",
        " tn",
        "BSP",
    ]


def normalise_raw_name_entry(name_entry):
    """Normalises a raw substation name string.

    This function applies several cleaning and formatting steps to produce
    a standardised substation name:
        - Converts text to title case.
        - Fixes malformed voltage spacing (e.g., "6 6" → "6.6").
        - Detects numeric voltage values in the name and removes them if they
          match predefined voltage levels.
        - Removes other unwanted substrings.
        - Expands common street abbreviations to full words (e.g., "St." → "Street").
        - Normalises whitespace and trims trailing punctuation/symbols.

    Args:
        name_entry (str): The raw name entry.

    Returns:
        str: A normalized substation name.
    """
    substrings_to_remove = SUBSTRINGS_TO_REMOVE.copy()

    name_entry = name_entry.title()

    if "6 6" in name_entry:
        name_entry = name_entry.replace("6 6", "6.6")

    for number_str in set(re.findall(r"\d+(?:\.\d+)?", name_entry)):
        number_decimal = Decimal(number_str).quantize(Decimal("0.1"))
        number_str_standardised = str(number_decimal)

        if number_str_standardised in VOLTAGE_LEVELS:
            substrings_to_remove.append(number_str)

    for sub_str in substrings_to_remove:
        name_entry = name_entry.replace(sub_str, "")

    name_entry = re.sub(r"\bst\.?\b", "Street", name_entry, flags=re.IGNORECASE)
    name_entry = re.sub(r"\brd\.?\b", "Road", name_entry, flags=re.IGNORECASE)
    name_entry = re.sub(r"\bln\.?\b", "Lane", name_entry, flags=re.IGNORECASE)
    
    name_entry = re.sub(r"\s+", " ", name_entry).strip().rstrip("./& ")

    return name_entry


__all__ = ["substation_type_map", "normalise_raw_name_entry"]