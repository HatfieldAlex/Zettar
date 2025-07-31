from location_input.models.substations import DNOLicenceArea, DNOGroup

licence_area_mapping = [
    ('north_west_england', 'ENW'),              
    ('north_east_england', 'NP'),              
    ('yorkshire', 'NP'),                  
    ('north_scotland', 'SSEN'),                 
    ('southern_england', 'SSEN'),             
    ('merseyside_cheshire_north_wales', 'SPEN'),
    ('central_southern_scotland', 'SPEN'),     
    ('london', 'UKPN'),                        
    ('eastern_england', 'UKPN'),                
    ('south_east_england', 'UKPN'),        
    ('east_midlands', 'NGED'),                  
    ('west_midlands', 'NGED'),                 
    ('south_west', 'NGED'),         
    ('south_wales', 'NGED'),                    
]

for licence_area, dno_abbr in licence_area_mapping:
    group = DNOGroup.objects.get(abbreviation=dno_abbr)
    DNOLicenceArea.objects.get_or_create(
        licence_area=licence_area,
        defaults={'dno_group': group}
    )
