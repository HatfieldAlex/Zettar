from pydantic import BaseModel, field_validator
from shapely.geometry import Point
from typing import List, Literal

VOLTAGE_LEVELS = [
    "6.6", "11.0", "25.0", "33.0", "66.0", "132.0", "275.0", "400.0"
]

SUBSTATION_TYPE_CHOICES = ["primary", "bsp", "gsp"]
DNO_GROUP_CHOICES = ["nged"]

class CleanSubstationDataRequirements(BaseModel):
    name: str
    type: Literal["primary", "bsp", "gsp"]
    candidate_voltage_levels_kv: List[str]
    geolocation: Point
    dno_group: Literal["nged"]

    @field_validator("candidate_voltage_levels_kv")
    @classmethod
    def validate_voltage_levels(cls, values):
        if not all(v in VOLTAGE_LEVELS for v in values):
            raise ValueError(f"Each voltage must be one of: {', '.join(VOLTAGE_LEVELS)}")
        return values

    model_config = {
        "arbitrary_types_allowed": True 
    }