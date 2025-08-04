VOLTAGE_LEVELS = [
    '6.6', 
    '11.0', 
    '25.0', 
    '33.0', 
    '66.0', 
    '132.0', 
    '275.0', 
    '400.0', 
    #remember to migrate if adding/changing a voltage level
    ] 

VOLTAGE_CHOICES = [
    (v, f"{v} kV") for v in VOLTAGE_LEVELS
] 

APPLICATION_STATUS_FIELDS = ['pending', 'budget', 'accepted']