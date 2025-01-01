from miio import Device, ChuangmiPlug


# Замените на ваши значения
ip_address = "0.0.0.0"
token = "some token"

plug = ChuangmiPlug(ip_address, token)

# Включаем устройство
plug.on()

# Выключаем устройство
# plug.off()

# Получаем статус устройства
status = plug.status()
print(f"Статус устройства: {status}")

# Получаем информацию об устройстве
info = plug.info()
print(f"Информация об устройстве: {info}")

