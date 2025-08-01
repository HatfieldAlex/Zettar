from location_input.models.substations import DNOGroup

groups = [
    ('UKPN', 'UK Power Networks'),
    ('NGED', 'National Grid Electricity Distribution'),
    ('SPEN', 'SP Energy Networks'),
    ('NP', 'Northern Powergrid'),
    ('ENW', 'Electricity North West'),
    ('SSEN', 'Scottish and Southern Electricity Networks'),
]

for abbr, name in groups:
    DNOGroup.objects.get_or_create(abbr=abbr, defaults={})
