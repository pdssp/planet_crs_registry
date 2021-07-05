from ..tortoise import WKT
from tortoise.contrib.pydantic import pydantic_model_creator

Wkt_Pydantic = pydantic_model_creator(WKT, name="WKT")