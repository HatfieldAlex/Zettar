from .models.substations import PrimarySubstation, BSPSubstation, GSPSubstation

substation_type_abbr_to_model = {
    'gsp': GSPSubstation,
    'bsp': BSPSubstation, 
    'primary': PrimarySubstation, 
}

substation_type_model_to_abbr = {
    GSPSubstation: 'gsp',
    BSPSubstation: 'bsp',
    PrimarySubstation: 'primary',
}

substation_type_model_to_display_name = {
    GSPSubstation: 'GSP',
    BSPSubstation: 'BSP',
    PrimarySubstation: 'primary',
}