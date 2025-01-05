from fastapi import FastAPI, HTTPException
from typing import List, Optional
from objects import SmartDevice, SmartHome, Temperature
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json
import uvicorn
import os
import re

from miio import ChuangmiPlug
from miio.exceptions import DeviceException

app         = FastAPI()
smart_home  = None
temps       = None

# Настройка SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://smarthome:smarthome@db/smarthome")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Создание таблиц
class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, index=True)
    name = Column(String, index=False)
    password = Column(String, index=False)

Base.metadata.create_all(bind=engine)

def get_temps(directory:str) -> List[Temperature]:
    result = list()
    txt_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                txt_files.append(os.path.join(root, file))

    print(f"# Total files with temp {len(txt_files)}")
    for txt in txt_files:
        with open(txt, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                items = line.split(',')
                number = 0.0
                try:
                    number = float(items[1])
                    match = re.search(r"\d+\.\d+", "0."+items[2])  # Ищет число с точкой
                    if match:
                        number += float(match.group())  # Преобразуем найденное число в float

                    tmp = Temperature( time = datetime.strptime(items[0], "%Y-%m-%d %H:%M:%S"),
                                       temp = number)
                    result.append(tmp)
                except Exception as e:
                    pass

    result = sorted(result, key=lambda x: x.time)
    return result

@app.get("/temps",response_model=List[Temperature])
def get_temperature(first_date:str,last_date:str):
    

    fd = None
    ld = None
    try:
        fd = datetime.strptime(first_date, "%Y-%m-%d")
        fd = fd.replace(hour=0, minute=0, second=0)
        ld = datetime.strptime(last_date, "%Y-%m-%d")
        ld = ld.replace(hour=23, minute=59, second=59)


    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Date should be in format YYYY-MM-DD")

    if ld < fd:
        raise HTTPException(status_code=404, detail="First date should be less then last date")

    temps = get_temps(smart_home.temp_folder)

    min_time = None
    max_time = None
    i           = 0
    min_index   = -1
    max_index   = -1

    for t in temps:
        if t.time<fd:
            min_index = i
        if t.time<ld:
            max_index = i


        if min_time is None or min_time > t.time:
            min_time = t.time
        if max_time is None or max_time < t.time:
            max_time = t.time
        i = i +1

    print(f"# Request min date: {fd}, max date: {ld}")
    print(f"# Data min date: {min_time}, max date: {max_time}")
    print(f"# Get items from {min_index} to {max_index}")

    result = list()
    if ld<min_time or fd>max_time:
        return result

    max_count = 50
    if max_index-min_index <= max_count:
        result = temps[min_index:max_index]
    else:
        step = int((max_index-min_index)/max_count)
        for i in range(max_count):
            val = 0
            start = min_index+i*step
            end   = min_index+(i+1)*step
            if i==max_count-1:
                end = max_index
            for j in range(start,end):
                val += temps[j].temp
            val = val / (end-start+1)
            tmp = Temperature(temp=val,time=temps[start].time)
            result.append(tmp)

    return result

@app.get("/devices", response_model=List[SmartDevice])
def get_devices():
    
    return smart_home.devices

@app.get("/device",response_model=SmartDevice)
def get_device(name:str):
    for d in smart_home.devices:
        if d.name == name:
            return d
    raise HTTPException(status_code=404, detail="Device not found")

@app.post("/plug_on",response_model=SmartDevice)
def plug_on(name:str):
    for d in smart_home.devices:
        if d.name == name:
            try:
                plug = ChuangmiPlug(d.ip, d.token)
                plug.on()
                return d
            except DeviceException as e:
                print(f"Ошибка при подключении к устройству: {e}")
        
    raise HTTPException(status_code=404, detail="Device not found")

@app.post("/plug_off",response_model=SmartDevice)
def plug_off(name:str):
    for d in smart_home.devices:
        if d.name == name:
            try:
                plug = ChuangmiPlug(d.ip, d.token)
                plug.off()
                return d
            except DeviceException as e:
                print(f"Ошибка при подключении к устройству: {e}")
        
    raise HTTPException(status_code=404, detail="Device not found")

@app.get("/plug_status",response_model=bool)
def get_plug_status(name:str):
    for d in smart_home.devices:
        if d.name == name:
            try:
                plug = ChuangmiPlug(d.ip, d.token)
                info = plug.status()
                return info.is_on
            except DeviceException as e:
                print(f"Ошибка при подключении к устройству: {e}")

    raise HTTPException(status_code=404, detail="Device not found")

if __name__ == "__main__":
    with open('devices.json', 'r', encoding='utf-8') as file:
        smart_home = SmartHome.model_validate(json.load(file))

    if smart_home is None:
        print("# No device found")
        exit(-1)

    temps = get_temps(smart_home.temp_folder)

    print(f"# Loaded {len(temps)} temps")
    print(f"# Loaded {len(smart_home.devices)} devices")

    uvicorn.run(app, host="0.0.0.0", port=8080)

