import datetime

from pydantic import BaseConfig, BaseModel as BModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def convert_datetime_to_base_model(dt: datetime.datetime) -> str:
    return dt.replace(tzinfo=datetime.timezone.utc).isoformat().replace("+00:00", "Z")

def convert_field_to_camel_case(string: str) -> str:
    return "".join(
        word if index == 0 else word.capitalize()
        for index, word in enumerate(string.split("_"))
    )

class BaseModel(BModel):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {datetime.datetime: convert_datetime_to_base_model}
        alias_generator = convert_field_to_camel_case