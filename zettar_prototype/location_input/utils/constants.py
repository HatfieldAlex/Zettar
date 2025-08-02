from decimal import Decimal

VOLTAGE_LEVELS = [
    '6.6', 
    '11', 
    '25', 
    '33', 
    '66', 
    '132', 
    '275', 
    '400', 
    #remember to migrate if adding/changing a voltage level
    ] 

VOLTAGE_CHOICES = [
    (Decimal(v), f"{v} kV") for v in VOLTAGE_LEVELS
] 