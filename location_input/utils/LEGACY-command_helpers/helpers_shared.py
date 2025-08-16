from pathlib import Path
import csv
import os
from django.core.management.base import CommandError
from .cleaning import extract_identifier_from_row_application_NGED, extract_identifier_from_row_substation_NGED, clean_data_map_application_NGED, clean_data_map_substation_NGED

def open_csv(path, mode):
    return open(path, mode, encoding="utf-8", newline="")

def get_data_csv_path(data_stage, data_type, dno_group_abbr):
    return (
        Path(__file__).resolve().parent.parent.parent.parent 
            / "data"
            / f"{data_stage}"
            / f"{data_type}_{data_stage}_{dno_group_abbr}.csv"
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

def clean_data_map(data_map, data_type, category):
    if category == "NGED" and data_type == "application":
        return clean_data_map_application_NGED(data_map)
    if category == "NGED" and data_type == "substation":
        return clean_data_map_substation_NGED(data_map)


def extract_identifier_from_row(row, data_type, dno_group_abbr):
    if dno_group_abbr == "NGED" and data_type == "application":
        return extract_identifier_from_row_application_NGED(row)
    elif dno_group_abbr == "NGED" and data_type == "substation":
        return extract_identifier_from_row_substation_NGED(row) 

def handle_row(row, writer, dno_group_abbr, data_type, successes, failures, command):
    if dno_group_abbr == "NGED" and data_type == "substation":
        if row["Substation Type"] in {"132kv Switching Station", "Ehv Switching Station"}:
            return

    identifier_name, identifier = extract_identifier_from_row(row, data_type, dno_group_abbr)
    try:
        cleaned_row = clean_data_map(row, data_type, dno_group_abbr)
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
            f"Script complete: {len(successes)} succeeded, {len(failures)} failed."
        )
    )
    if failures:
        command.stderr.write(
            command.style.ERROR(f"Failed identifiers: {failures}")
        )

__all__ = [
    "open_csv",
    "get_data_csv_path",
    "reset_csv",
    "clean_data_map",
    "extract_identifier_from_row",
    "handle_row",
    "report_results",
]
