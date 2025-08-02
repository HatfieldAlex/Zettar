def normalise_name_and_extract_voltage_info(ss_name):

    #remove basic suffiexs
    ss_name = ss_name.strip()
    suffixes_to_remove = [
        ' Bsp',
        ' S.G.P',
        ' S Stn',
        ' Primary Substation',
    ]
    for suffix in suffixes_to_remove:
        if ss_name.endswith(suffix):
            ss_name = ss_name[: -len(suffix)].rstrip()

    voltage_levels = []
    kv_index = ss_name.lower().rfind('kv')
    if kv_index != -1:
        ss_name = ss_name[:kv_index].rstrip()

        #extract voltages
        voltages_str = ss_name[ss_name.rfind(' ') + 1:]
        ss_name = ss_name[:ss_name.rfind(' ')]
        voltage_levels = voltages_str.split('/')
        voltage_levels = [float(v) for v in voltage_levels]

    if ss_name.endswith('Primary Substation'):
            ss_name = ss_name[: -len(suffix)].rstrip()

    return [ss_name, voltage_levels]
