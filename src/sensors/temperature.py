from mlx90614 import MLX90614
from smbus2.smbus2 import SMBus


class TemperatureSensor:
    def __init__(self):
        self._bus = SMBus(1)
        self._inner = MLX90614(self._bus)

    def __del__(self):
        self._bus.close()

    def get_object_temperature(self) -> float:
        return self._inner.get_obj_temp()

    def get_ambient_temperature(self) -> float:
        return self._inner.get_amb_temp()
