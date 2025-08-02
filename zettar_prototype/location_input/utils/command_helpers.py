import re

VOLTAGE_CHOICES = {
    6.6, 11.0, 33.0, 66.0, 132.0
}

def normalise_name_and_extract_voltage_info(ss_name):

    # Step 1: Trim from the right, stopping at first digit before kv
    kv_index = ss_name.lower().rfind('kv')
    if kv_index != -1:
        ss_name = ss_name[:kv_index].rstrip()

    #extract strings
    voltages_str = ss_name[ss_name.rfind(' ') + 1:]
    ss_name = ss_name[:ss_name.rfind(' ')]
    voltage_levels = voltages_str.split('/')
    voltage_levels = [float(v) for v in voltage_levels]

    return [ss_name, voltage_levels]

print(normalise_name_and_extract_voltage_info('Northampton West 132/33/11kv'))