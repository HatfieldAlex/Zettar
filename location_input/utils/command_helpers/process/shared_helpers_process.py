from location_input.utils.command_helpers.process.helpers_NGED import process_row_NGED, handle_row_process_NGED

def process_row(row, dno_group_abbr):
    if dno_group_abbr == "NGED":
        process_row_NGED(row)

def handle_row_process(row, successes, failures, command, dno_group_abbr):
    if dno_group_abbr == "NGED":
        handle_row_process_NGED(row, successes, failures, command)