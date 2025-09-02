from django.core.management.base import BaseCommand, CommandError
from ...resources.data_resource_class import DataResource
from ...resources import data_resource_instances

VALID_ACTIONS = ["orchestrate"]
DEFAULT_ACTION = "orchestrate"

VALID_DNO_GROUP_ABBRS = ["nged", "ukpn", "np"]
DEFAULT_DNO_GROUP_ABBR = "nged"

VALID_CATEGORIES = ["substation"]
DEFAULT_CATEGORY = "substation"

VALID_STAGES = ["ingest", "prepare", "load", "all"]
DEFAULT_STAGE = "all"



class Command(BaseCommand):

    def prompt_user_choice(self, prompt_text, valid_options, default_option):
        """Helper method to prompt user for input with validation."""
        while True:
            user_input = input(f"{prompt_text} ({'/'.join(valid_options)}) [{default_option}]: ").strip().lower()
            choice = user_input or default_option
            if choice in valid_options:
                return choice
            self.stderr.write(f"Invalid choice. Please select from: {', '.join(valid_options)}.\n")

    def handle(self, *args, **options):
        command_choice = self.prompt_user_choice("Choose a pipeline action", VALID_ACTIONS, DEFAULT_ACTION)
        dno_group_abbr_choice = self.prompt_user_choice("Choose a DNO group to handle", VALID_DNO_GROUP_ABBRS, DEFAULT_DNO_GROUP_ABBR)
        category_choice = self.prompt_user_choice("Choose a data category", VALID_CATEGORIES, DEFAULT_CATEGORY)
        stage_choice = self.prompt_user_choice("Choose a pipeline stage", VALID_STAGES, DEFAULT_STAGE)

        action_verb = "orchestrating" if command_choice == "orchestrate" else "inspecting"
        self.stdout.write(
            self.style.NOTICE(
                "\n"
                f"{action_verb} pipeline:\n"
                f"  DNO group abbr : {dno_group_abbr_choice}\n"
                f"  Data category  : {category_choice}\n"
                f"  Pipeline Stage : {stage_choice}\n"
            )
        )

        data_resources = DataResource.filter(dno_group=dno_group_abbr_choice, data_category=category_choice)
        if data_resources == []:
            raise CommandError(
                f"No DataResource instances found for DNO group {dno_group_abbr_choice} and data category {category_choice}"
                )
        else:
            self.stdout.write(
                self.style.NOTICE(f"data resources found for DNO group {dno_group_abbr_choice} and data category {category_choice}\n")
                )

        if command_choice == "orchestrate":
            for data_resource in data_resources:
                if stage_choice == "ingest":
                    data_resource.ingest(stdout=self.stdout, style=self.style)
                elif stage_choice == "prepare":
                    data_resource.prepare(stdout=self.stdout, style=self.style)
                elif stage_choice == "load":
                    data_resource.load(stdout=self.stdout, style=self.style)
                elif stage_choice == "all":
                    data_resource.ingest(stdout=self.stdout, style=self.style)
                    data_resource.prepare(stdout=self.stdout, style=self.style)
                    data_resource.load(stdout=self.stdout, style=self.style)

        elif command_choice == "inspect":
            self.stdout.write(self.style.WARNING(f"Inspection command not complete yet"))

