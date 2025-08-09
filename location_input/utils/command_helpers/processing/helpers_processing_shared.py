from .application import process_row_NGED, handle_row_process_NGED
from location_input.models.substations import Substation, DNOGroup
from location_input.models.new_connections import NewConnection
from .application import handle_row_process_application_NGED

def process_row(row, dno_group_abbr):
    if dno_group_abbr == "NGED":
        process_row_NGED(row)

def handle_row_process_substation(row, successes, failures, command, dno_group_abbr):
    if dno_group_abbr == "NGED":
        handle_row_process_NGED(row, successes, failures, command)

def handle_row_process_application(style, row, dno_group_abbr, successful_identifiers, failed_identifiers, stdout, stderr):
    if dno_group_abbr == "NGED":
        handle_row_process_application_NGED(style, row, successful_identifiers, failed_identifiers, stdout, stderr)

def clear_existing_cleaned_data(stdout, data_type, dno_group_abbr):
    type_map = {
        "substation": Substation,
        "application": NewConnection,
    }
    stdout.write(f"Clearing existing {dno_group_abbr} {data_type} data in project DB")
    dno_group = DNOGroup.objects.get(abbr=dno_group_abbr)
    connection_or_substation_class = type_map.get(data_type)
    connection_or_substation_class.objects.filter(dno_group=dno_group).delete()
    stdout.write(f"{dno_group_abbr} {data_type} data cleared")

__all__ = [
    "process_row",
    "handle_row_process_substation",
    "handle_row_process_application",
    "clear_existing_cleaned_data",
]
