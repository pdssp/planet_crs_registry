# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr


# properties required during contact email
class ContactEmail(BaseModel):
    firstName: str
    name: str
    email: str
    comments: str
