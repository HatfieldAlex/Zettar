from django.core.management.base import BaseCommand, CommandError
from ...utils.core import DataResource

class Command(BaseCommand):
    help = "Import and clean application data"

    def add_arguments(self, parser):
        parser.add_argument(
            'operation',
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
        operation = options["operation"]
        data_category = options["data_category"]
        dno_group_abbr = options['dno_group_abbr']

        self.stdout.write(
            self.style.NOTICE(
                "\n"
                f"Running pipeline:\n"
                f"  Operation      : {operation}\n"
                f"  Data category  : {data_category}\n"
                f"  DNO group abbr : {dno_group_abbr}\n"
            )
        )

        if DataResource.filter(dno_group=dno_group_abbr, data_category=data_category) == []:
            raise CommandError(f"No DataResource instances found for DNO group {dno_group_abbr} and data category {data_category}")
        else:
            self.stdout.write(self.style.NOTICE(f"data resources found for DNO group {dno_group_abbr} and data category {data_category}\n"))


        for data_resource in DataResource.filter(dno_group=dno_group_abbr, data_category=data_category):
            data_resource.ingest(stdout=self.stdout, style=self.style)
            data_resource.prepare()
            data_resource.load()

