from fastapi import FastAPI, HTTPException
from typing import List, Optional
from objects import SmartDevice, SmartHome
import json
import uvicorn

from miio import ChuangmiPlug
from miio.exceptions import DeviceException

app         = FastAPI()
smart_home  = None

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

    print(f"# Loaded {len(smart_home.devices)} devices")

    uvicorn.run(app, host="0.0.0.0", port=8080)


# ip_address = "0.0.0.0"
# token = "some token"
# plug = ChuangmiPlug(ip_address, token)
# plug.on()
# status = plug.status()
# print(f"Статус устройства: {status}")
# info = plug.info()
# print(f"Информация об устройстве: {info}")
