from fastapi import FastAPI, HTTPException
from typing import List, Optional
from objects import SmartDevice, SmartHome, Temperature
from datetime import datetime
import json
import uvicorn
import os
import re

from miio import ChuangmiPlug
from miio.exceptions import DeviceException

app         = FastAPI()
smart_home  = None
temps       = None

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
def get_temperature():
    return temps

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

