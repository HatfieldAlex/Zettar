
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
            choices=["substations", "connection_applications"],
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

        for data_resource in DataResource.filter(dno=dno_group_abbr, data_category=data_category):
            data_resource.fetch_data_resource()
            data_resource.clean()
            data_resource.process()

        print(f"pipeline_operation: {pipeline_operation}, content_type: {content_type}, dno_group_abbr: {dno_group_abbr}")

