

from pydantic import BaseModel, validator
from typing import List


class UbuyProduct(BaseModel):
    name: str
    short_description: str
    description: str
    summary:str
    bullet_points: List[str]

    class Config:
        allow_population_by_field_name = True

    @validator('short_description', 'description', 'name')
    def validate_description(cls, v):
        if v == '':
            raise ValueError(
                'Description cannot be empty'
            )

        if v == '[]':
            raise ValueError(
                'Invalid description'
            )
        return v

class AmazonProduct(BaseModel):
    name: str
    description: str
    summary:str

    class Config:
        allow_population_by_field_name = True

    @validator('description', 'summary', 'name')
    def validate_description(cls, v):
        if v == '':
            raise ValueError(
                'Neither description nor summary can be empty'
            )

        if v == '[]':
            raise ValueError(
                'Invalid description'
            )
        return v