from pydantic import BaseModel, Field, validator
from shapely.geometry import Point
from typing import Literal, List, Any


class CleanSubstationDataRequirements(BaseModel):
    name: str
    type: Literal["primary", "bsp", "gsp"]
    geolocation: Point
    dno: Literal["nged"]
    voltages: List[float]

    def to_django_model(self) -> "CleanSubstationData":
        from data_pipeline.models import CleanSubstationData
        return CleanSubstationData(**self.dict())
