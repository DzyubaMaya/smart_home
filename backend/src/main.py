from fastapi import FastAPI, HTTPException
from typing import List, Optional
from objects import SmartDevice, SmartHome
import json
import uvicorn

#from miio import Device, ChuangmiPlug

app     = FastAPI()
devices = None


if __name__ == "__main__":
    with open('devices.json', 'r', encoding='utf-8') as file:
        # Загружаем данные из файла
        devices = SmartHome.model_validate(json.load(file))

    if devices is None:
        print("# No device found")
        exit(-1)

    print(f"# Loaded {len(devices.devices)} devices")

    uvicorn.run(app, host="0.0.0.0", port=8080)


# ip_address = "0.0.0.0"
# token = "some token"
# plug = ChuangmiPlug(ip_address, token)
# plug.on()
# status = plug.status()
# print(f"Статус устройства: {status}")
# info = plug.info()
# print(f"Информация об устройстве: {info}")
