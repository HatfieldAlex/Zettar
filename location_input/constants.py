VOLTAGE_LEVELS = [
    "6.6",
    "11.0",
    "25.0",
    "33.0",
    "66.0",
    "132.0",
    "275.0",
    "400.0",
]

VOLTAGE_CHOICES = [(v, f"{v} kV") for v in VOLTAGE_LEVELS]

APPLICATION_STATUS_FIELDS = ["pending", "budget", "accepted"]

CLEAN_SUBSTATION_CSV_HEADERS = [
    "name", "type", "geolocation", "dno", "voltages"
    ]

CLEAN_APPLICATION_CSV_HEADERS = [
        "name",
        "type",
        "dno",
        "ss_voltages",
        "proposed_voltage",
        "connection_status",
        "total_demand_number",
        "total_demand_capacity_mw",
        "total_generation_number",
        "total_generation_capacity_mw",
    ]