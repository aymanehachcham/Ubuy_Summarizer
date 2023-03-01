
from pydantic import BaseSettings, Field
from dotenv import load_dotenv
from pydantic import BaseModel, validator
from typing import List
from dataclasses import dataclass

load_dotenv(verbose=True)
class UbuySettings(BaseSettings):
    openapi_key:str = Field(..., env="OPENAI_APP_KEY")
    input_file:str = Field(..., env="INPUT_FILE")
    output_file:str = Field(..., env="OUTPUT_FILE")
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


class UbuyProduct(BaseModel):
    name: str
    short_description: str
    description: str
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

class UbuyProductSummary(BaseModel):
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