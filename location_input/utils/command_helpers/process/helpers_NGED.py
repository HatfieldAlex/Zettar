import ast
from django.contrib.gis.geos import GEOSGeometry

from location_input.models.substations import DNOGroup, Substation
from location_input.models.shared_fields import ConnectionVoltageLevel

def process_row_NGED(row):
    ss_name = row["name"]
    ss_type = row["type"]
    ss_geolocation = GEOSGeometry(row["geolocation"])
    ss_dno = row["dno"]
    ss_voltages = ast.literal_eval(row["voltages"])

    dno_group_obj = DNOGroup.objects.get(abbr=ss_dno)
    connection_voltage_levels_objs = ConnectionVoltageLevel.objects.filter(
        level_kv__in=ss_voltages
    )

    substation = Substation.objects.create(
        name=ss_name,
        geolocation=ss_geolocation,
        type=ss_type,
        dno_group=dno_group_obj,
    )
    substation.voltage_kv.set(connection_voltage_levels_objs)
    substation.save()


def handle_row_process_NGED(row, successes, failures, command):
    identifier_name = row["name"]
    try:
        process_row_NGED(row)
        command.stdout.write(command.style.SUCCESS(f"Successfully processed row with substation name {identifier_name}"))
        successes.append(identifier_name)
    except Exception as e:
        command.stderr.write(command.style.ERROR(f"Error processing row  with substation name: {identifier_name}"))
        command.stderr.write(command.style.ERROR(str(e)))
        failures.append(identifier_name)
