# -*- coding: utf-8 -*-
from pydantic import BaseModel


# properties required during contact email
class ContactEmail(BaseModel):
    firstName: str
    name: str
    email: str
    comments: str
