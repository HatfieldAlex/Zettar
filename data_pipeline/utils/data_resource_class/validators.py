from django.contrib.gis.geos import Point as GEOSPoint
from typing import List, Literal, Optional
from decimal import Decimal
from pydantic import BaseModel, field_validator, condecimal, conint


VOLTAGE_LEVELS = [
    "6.6", "11.0", "25.0", "33.0", "66.0", "132.0", "275.0", "400.0"
]

SUBSTATION_TYPE_CHOICES = ["primary", "bsp", "gsp"]
DNO_GROUP_CHOICES = ["nged"]

class CleanSubstationDataRequirement(BaseModel):
    name: str
    type: Literal["primary", "bsp", "gsp"]
    external_identifier: str
    geolocation: GEOSPoint
    candidate_voltage_levels_kv: List[str]
    dno_group: Literal["nged"]
    reference: str
    

    @field_validator("candidate_voltage_levels_kv")
    @classmethod
    def validate_voltage_levels(cls, values):
        if not all(v in VOLTAGE_LEVELS for v in values):
            raise ValueError(f"Each voltage must be one of: {', '.join(VOLTAGE_LEVELS)}")
        return values

    model_config = {
        "arbitrary_types_allowed": True 
    }



class CleanConnectionApplicationDataRequirement(BaseModel):
    name: str
    substation_type: Literal["primary_substation", "bsp", "gsp"]
    dno_group: Literal["nged"]
    candidate_voltage_levels_kv: List[str]
    geolocation: Optional[GEOSPoint] = None

    proposed_voltage: condecimal(max_digits=4, decimal_places=1) 
    connection_status: Literal["pending", "budget", "accepted"]
    total_demand_number: conint(ge=0)
    total_demand_capacity_mw: condecimal(ge=Decimal("0"), max_digits=10, decimal_places=4)
    total_generation_number: conint(ge=0)
    total_generation_capacity_mw: condecimal(ge=Decimal("0"), max_digits=10, decimal_places=4)
    
    external_identifier: str
    reference: str

    @field_validator("candidate_voltage_levels_kv")
    @classmethod
    def validate_voltage_levels(cls, values):
        if not all(v in VOLTAGE_LEVELS for v in values):
            raise ValueError(f"Each voltage must be one of: {', '.join(VOLTAGE_LEVELS)}")
        return values

    @field_validator("proposed_voltage")
    @classmethod
    def validate_proposed_voltage(cls, value: Decimal) -> Decimal:
        quantised = value.quantize(Decimal("0.0"))
        if str(quantised) not in VOLTAGE_LEVELS:
            raise ValueError(f"proposed_voltage must be one of: {', '.join(VOLTAGE_LEVELS)}")
        return quantised

    model_config = {
        "arbitrary_types_allowed": True 
    }
