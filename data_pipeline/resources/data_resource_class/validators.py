from decimal import Decimal
from typing import List, Literal, Optional

from django.contrib.gis.geos import Point as GEOSPoint
from pydantic import BaseModel, field_validator, condecimal, conint


class CleanSubstationDataRequirement(BaseModel):
    name: str
    type: Literal["primary", "bsp", "gsp"]
    external_identifier: str
    geolocation: GEOSPoint
    dno_group: Literal["nged", "ukpn", "np"]
    reference: str
    
    model_config = {
        "arbitrary_types_allowed": True 
    }

    @field_validator("name")
    def name_must_not_be_empty_string(cls, v):
        if v == "":
            raise ValueError("name must not be an empty string")
        return v

