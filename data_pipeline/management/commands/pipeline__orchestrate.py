from django.core.management.base import BaseCommand
from ...utils.core import DataResource

class Command(BaseCommand):
    help = "Import and clean application data"

    def add_arguments(self, parser):
        parser.add_argument(
            'pipeline_operation',
            type=str,
            choices=["ingest", "clean", "process"],
        )
        parser.add_argument(
            'data_category',
            type=str,
            choices=["substation", "connection_application"],
        )
        parser.add_argument(
            'dno_group_abbr',
            type=str,
            choices=["nged"],
            help="Only NGED DNO is currently supported.",
        )
    
    def handle(self, *args, **options):
        pipeline_operation = options["pipeline_operation"]
        data_category = options["data_category"]
        dno_group_abbr = options['dno_group_abbr']

        print(f"pipeline_operation: {pipeline_operation}, data_category: {data_category}, dno_group_abbr: {dno_group_abbr}")

        if DataResource.filter(dno_group=dno_group_abbr, data_category=data_category) == []:
            print("problem! empty filter set")

        for data_resource in DataResource.filter(dno_group=dno_group_abbr, data_category=data_category):
            print("get here?")
            data_resource.ingest()
            data_resource.prepare()
            data_resource.load()

