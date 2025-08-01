import csv 
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point 
import requests
import io
import re
from decimal import Decimal
from datetime import date

from location_input.models.substations import (
    DNOGroup,
    GSPSubstation,
    BSPSubstation,
    PrimarySubstation,
)

from location_input.models.new_connections import (
    ProposedConnectionVoltageLevel,
    ConnectionStatus,
    ReportingPeriod,
    NewConnection,

)

class Command(BaseCommand):
    help = 'Import and process ngid data from ngid website'

    def handle(self, *args, **options):

        self.clear_existing_nged_new_connections_data()

        self.stdout.write(f"Fetching CSV ...")
        CSV_PATH = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'ngid' / 'new_connections_update_may_2025_raw.csv'

        success_substations_gsps = []
        failure_substations_gsps = []

        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                GSP = row.get('Grid Supply Point')
                try:
                    self.process_row(row)           
                    # self.stdout.write(self.style.SUCCESS(f"Successfully processed row of GSP {GSP}: {row}"))
                    success_substations_gsps.append(GSP)
                except Exception as e:
                    print('----------------------------------------')
                    self.stderr.write(self.style.ERROR(str(e)))
                    self.stderr.write(self.style.ERROR(f"Error processing row. Refer to string name above."))
                    
                    names = {
                        'GSP': {row['Grid Supply Point']}, 
                        'BSP': {row['Bulk Supply Point']}, 
                        'Primary': {row['Primary Substation']}
                    }
                    
                    print(names)
                    # self.stderr.write(self.style.ERROR(f"Error processing row of GSP {GSP}: {row}"))
                    # self.stderr.write(self.style.ERROR(str(e)))
                    failure_substations_gsps.append(names)
                    print('----------------------------------------')

        self.stdout.write(self.style.SUCCESS(
            f"CSV import complete: {len(success_substations_gsps)} succeeded, {len(failure_substations_gsps)} failed."
        ))

        if failure_substations_gsps:
            failed_list = ', '.join(failure_substations_gsps)
            self.stderr.write(self.style.ERROR(f"GSPs of rows that failed to process: {failed_list}"))


    def clear_existing_nged_new_connections_data(self):
        self.stdout.write("Clearing existing NGED New Connection data...")
        dno_group = DNOGroup.objects.get(abbr="NGED")
        NewConnection.objects.filter(dno_group=dno_group).delete()
        self.stdout.write("NGED New Connection data cleared")

    def get_connection_status(self, status):
        if status == 'Connection offers not yet accepted':
            return ConnectionStatus.objects.get(status='pending')
        elif status == 'Budget Estimates Provided':
            return ConnectionStatus.objects.get(status='budget')
        elif status == 'Connection offers accepted':
            return ConnectionStatus.objects.get(status='accepted')
            
    def initial_preliminary_clean(self, name):
        for i, c in enumerate(name):
            if c.isdigit():
                name = name[:i-1]
                break
        return name

    def subsequent_clean_gsp(self, name):
        if name.endswith(' S.G.P'):
            name = name.removesuffix(' Sgp')
        if name.endswith(' ('):
            name = name.removesuffix(' (')
        return name

    def subsequent_clean_bsp(self, name):
        if name.endswith(' Bsp'):
                name = name.removesuffix(' Bsp')
        if name.endswith(' ('):
                name = name.removesuffix(' (')
        return name 

    def subsequent_clean_primary(self, name):
        if name.endswith(' Primary Substation'):
            return name.removesuffix(' Primary Substation')
        return name

         
    
    def process_row(self, row):

        #handling the supporting objects 
        dno_group_obj = DNOGroup.objects.get(abbr="NGED")

        start = date(2025, 1, 1)
        end = date(2025, 5, 31)
        reporting_period_obj = ReportingPeriod.objects.get(start_date=start, end_date=end)

        proposed_voltage_str = row['Proposed Connection Voltage (kV)']
        level_kv = Decimal(proposed_voltage_str.strip()) 
        proposed_connection_voltage_obj = ProposedConnectionVoltageLevel.objects.get(level_kv=level_kv)
               
        connection_status = row['Connection Status']
        connection_status_obj = self.get_connection_status(connection_status)
        
        #handling rest
        total_demand_number = row['Total Demand Number']
        total_demand_capacity = row['Total Demand Capacity (MW)']
        total_generation_number = row['Total Generation Number']
        total_generation_capacity = row['Total Generation Capacity (MW)']

        #creating initial connection object
        connection = NewConnection.objects.create(
            connection_status=connection_status_obj,
            voltage_level=proposed_connection_voltage_obj,
            reporting_period=reporting_period_obj,
            dno_group=dno_group_obj,
            demand_count=total_demand_number,
            total_demand_capacity_mw=total_demand_capacity,
            generation_count=total_generation_number,
            total_generation_capacity_mw=total_generation_capacity,
        )

        gsp_substation_name = self.initial_preliminary_clean(row['Grid Supply Point'])
        bsp_substation_name = self.initial_preliminary_clean(row['Bulk Supply Point'])
        primary_substation_name = self.initial_preliminary_clean(row['Primary Substation'])

        #handling GSPs
        if bsp_substation_name == '-':
            gsp_substation_name = self.subsequent_clean_gsp(gsp_substation_name)

            print(f'gsp_substation_name &{gsp_substation_name}&')

            gsp_substation_obj = GSPSubstation.objects.get(name=gsp_substation_name, dno_group=dno_group_obj)
            connection.gsp_substation = gsp_substation_obj

        #handling BSPs
        elif bsp_substation_name and primary_substation_name == '-':
            bsp_substation_name = self.subsequent_clean_bsp(bsp_substation_name)

            print(f'bsp_substation_name: &{bsp_substation_name}&')

            bsp_substation_obj = BSPSubstation.objects.get(name=bsp_substation_name, dno_group=dno_group_obj)
            connection.bsp_substation = bsp_substation_obj
        
        #handling primary stations
        elif primary_substation_name:
            primary_substation_name = self.subsequent_clean_primary(primary_substation_name)

            print(f'primary_substation_name: &{primary_substation_name}&')
            
            primary_substation_obj = PrimarySubstation.objects.get(name=primary_substation_name, dno_group=dno_group_obj)
            connection.primary_substation = primary_substation_obj


            
        connection.save()



