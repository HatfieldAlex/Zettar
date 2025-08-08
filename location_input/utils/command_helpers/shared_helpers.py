from pathlib import Path
import csv
import os
from django.core.management.base import CommandError
from location_input.utils.command_helpers.helpers_NGED import clean_data_map_NGED, extract_identifier_from_row_NGED

def open_csv(path, mode):
    return open(path, mode, encoding="utf-8", newline="")

def get_data_csv_path(data_stage, dno_group_abbr):
    return (
        Path(__file__).resolve().parent.parent.parent.parent 
            / "data"
            / f"{data_stage}"
            / f"connection_applications_{data_stage}_{dno_group_abbr}.csv"
    )


def reset_csv(file_path, csv_headers, stdout):
    """
    Deletes an existing CSV (if it exists) and creates a new blank one 
    with the given headers. Raises CommandError on failure.
    """
    try:
        # Remove existing file if present
        if file_path.exists():
            stdout.write(f"Removing old CSV: {file_path}")
            file_path.unlink()

        # Ensure parent directory exists
        os.makedirs(file_path.parent, exist_ok=True)

        # Create blank CSV with headers
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()

        stdout.write(f"Blank CSV initialised: {file_path.name}")

    except Exception as e:
        raise CommandError(f"Error resetting CSV {file_path}: {e}")

def clean_data_map(data_map, category):
    if category == 'NGED':
        return clean_data_map_NGED(data_map, category)


def extract_identifier_from_row(row, dno_group_abbr):
    if dno_group_abbr == "NGED":
        return extract_identifier_from_row_NGED(row, dno_group_abbr)


def handle_row(row, writer, dno_group_abbr, successes, failures, command):
    identifier_name, identifier = extract_identifier_from_row(row, dno_group_abbr)
    try:
        cleaned_row = clean_data_map(row, dno_group_abbr)
        writer.writerow(cleaned_row)
        command.stdout.write(command.style.SUCCESS(f"Successfully cleaned row of {identifier_name}: {identifier}"))
        successes.append(identifier_name)

    except Exception as e:
        command.stderr.write(command.style.ERROR(f"Error cleaning row of {identifier_name}: {identifier}"))
        command.stderr.write(command.style.ERROR(str(e)))
        failures.append(identifier_name)


def report_results(command, successes, failures):
    command.stdout.write(
        command.style.SUCCESS(
            f"CSV clean complete: {len(successes)} succeeded, {len(failures)} failed."
        )
    )
    if failures:
        command.stderr.write(
            command.style.ERROR(f"Failed identifiers: {failures}")
        )