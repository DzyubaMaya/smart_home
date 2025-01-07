from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Login(BaseModel):
    email    : str
    password :  str   

class LoginSession(BaseModel):
    session_id   : str
    created_time : datetime

class UserCreate(BaseModel):
    email    : str
    name     : str
    password :  str

class UserCreateResponse(BaseModel):
    result : bool
    msg    : str

class SmartDevice(BaseModel):
    name    : str
    type    : str
    token   : str
    ip      : str

class SmartHome(BaseModel):
    temp_folder : str
    devices : List[SmartDevice]

class Temperature(BaseModel):
    temp : float
    time : datetime
