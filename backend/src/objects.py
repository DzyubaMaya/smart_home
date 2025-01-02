from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SmartDevice(BaseModel):
    name    : str
    type    : str
    token   : str
    ip      : str

class SmartHome(BaseModel):
    devices : List[SmartDevice]
