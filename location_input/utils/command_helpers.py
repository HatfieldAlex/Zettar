import re
from decimal import Decimal
from location_input.utils.constants import VOLTAGE_LEVELS


def normalise_name_and_extract_voltage_info(ss_name):
    voltage_levels = VOLTAGE_LEVELS

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

    if "6 6" in ss_name:
        ss_name = ss_name.replace("6 6", "6.6")

    numbers_in_ss_name = set(re.findall(r"\d+(?:\.\d+)?", ss_name))
    voltage_levels_ss = []

    for number_str in numbers_in_ss_name:
        number_decimal = Decimal(number_str).quantize(Decimal("0.1"))
        number_str_standardised = str(number_decimal)

        if number_str_standardised in voltage_levels:
            voltage_levels_ss.append(number_str_standardised)
            substrings_to_remove.append(number_str)

    for sub_str in substrings_to_remove:
        ss_name = ss_name.replace(sub_str, "")

    ss_name = re.sub(r"\bst\.?\b", "Street", ss_name, flags=re.IGNORECASE)
    ss_name = re.sub(r"\brd\.?\b", "Road", ss_name, flags=re.IGNORECASE)
    ss_name = re.sub(r"\bln\.?\b", "Lane", ss_name, flags=re.IGNORECASE)
    ss_name = re.sub(r"\s+", " ", ss_name).strip().rstrip("./& ")

    voltage_levels_ss = sorted(voltage_levels_ss, key=float)

    return [ss_name, voltage_levels_ss]
