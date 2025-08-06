import re
from decimal import Decimal

from location_input.utils.constants import VOLTAGE_LEVELS

substrings_to_remove = [
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

def normalise_name_and_extract_voltage_info(ss_name):
     """Normalises a substation name and extract voltage level information.

    This function performs the following steps:
        - Replaces certain malformed patterns (e.g., "6 6" -> "6.6").
        - Finds numeric voltage values present in the name and checks
          them against a predefined list of voltage levels.
        - Removes specified unwanted substrings from the name.
        - Expands common street abbreviations to full words.
        - Trims extra spaces and trailing punctuation.

    Args:
        ss_name (str): The original substation name.

    Returns:
        Tuple[str, List[str]]:
            A tuple containing:
                - Normalized substation name (str)
                - Sorted list of voltage levels (List[str])
    """
    voltage_levels = VOLTAGE_LEVELS

    #standardise malformed voltage spacing
    if "6 6" in ss_name:
        ss_name = ss_name.replace("6 6", "6.6")

    #extract numerical values from str name
    voltage_levels_ss = []
    for number_str in set(re.findall(r"\d+(?:\.\d+)?", ss_name)):
        number_decimal = Decimal(number_str).quantize(Decimal("0.1"))
        number_str_standardised = str(number_decimal)

        if number_str_standardised in voltage_levels:
            voltage_levels_ss.append(number_str_standardised)
            substrings_to_remove.append(number_str)

    # Remove unwanted substrings
    for sub_str in substrings_to_remove:
        ss_name = ss_name.replace(sub_str, "")

    # Normalise common abbreviations
    ss_name = re.sub(r"\bst\.?\b", "Street", ss_name, flags=re.IGNORECASE)
    ss_name = re.sub(r"\brd\.?\b", "Road", ss_name, flags=re.IGNORECASE)
    ss_name = re.sub(r"\bln\.?\b", "Lane", ss_name, flags=re.IGNORECASE)
    
    #normalise spacing and remove trailing symbols
    ss_name = re.sub(r"\s+", " ", ss_name).strip().rstrip("./& ")

    #order voltage levels numerically 
    voltage_levels_ss = sorted(voltage_levels_ss, key=float)

    return [ss_name, voltage_levels_ss]
