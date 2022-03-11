print(">>> STARTING main.py")

# >>> INFRARED TEMPERATURE SENSOR
# from smbus2.smbus2 import SMBus
# from mlx90614 import MLX90614
# from time import sleep

# bus = SMBus(1)
# sensor = MLX90614(bus, address=0x5A)

# try:
#     while True:
#         print(sensor.get_amb_temp())
#         print(sensor.get_obj_temp())
#         print(sensor.get_object_2())
#         sleep(0.2)
# except KeyboardInterrupt:
#     pass


# bus.close()


# >>> PROXIMITY_SENSOR
# import RPi.GPIO as io
# from time import sleep

# PROXIMITY_SENSOR = 7

# io.setmode(io.BOARD)
# io.setup(PROXIMITY_SENSOR, io.IN)

# try:
#     while True:
#         print(io.input(PROXIMITY_SENSOR))

# except KeyboardInterrupt:
#     io.cleanup()


# >>> ULTRASONIC SENSOR
# import RPi.GPIO as io
# import time

# TRIG_PIN = 23
# ECHO_PIN = 24

# io.setmode(io.BCM)
# io.setup(TRIG_PIN, io.OUT)
# io.setup(ECHO_PIN, io.IN)

# io.output(TRIG_PIN, False)
# time.sleep(2)


# def distance():
#     io.output(TRIG_PIN, True)
#     time.sleep(0.00001)
#     io.output(TRIG_PIN, False)

#     print(io.input(ECHO_PIN))

#     # return 0.1

#     while io.input(ECHO_PIN) == 0:
#         start_time = time.time()

#     while io.input(ECHO_PIN) == 1:
#         end_time = time.time()

#     time_elapsed = end_time - start_time
#     return round(time_elapsed * 17150, 2)


# print(io.input(ECHO_PIN))

# try:
#     while True:
#         # dist = distance()
#         io.output(TRIG_PIN, True)
#         time.sleep(0.00001)
#         io.output(TRIG_PIN, False)
#         print(io.input(ECHO_PIN))
#         # print(f"Measured Distance = {dist:1f} cm")
#         time.sleep(1)
# except KeyboardInterrupt:
#     pass

# io.cleanup()


# from driver import Lcd

# from smbus2.smbus2 import SMBus

# from mlx90614 import MLX90614
# from time import sleep

# bus = SMBus(1)
# sensor = MLX90614(bus, address=0x5A)
# display = Lcd(addr=0x27)

# try:
#     print("Writing to display")
#     while True:
#         display.lcd_display_string(f"Amb temp {sensor.get_amb_temp()}", 1)
#         display.lcd_display_string(f"Obj temp {sensor.get_obj_temp()}", 2)
#         # print()
#         # # print()
#         # # print(sensor.get_object_2())
#         sleep(0.5)
# except KeyboardInterrupt:
#     print("Cleaning up!")
#     # display.lcd_clear()

import RPi.GPIO as io
import time

RELAY = 17

io.setmode(io.BCM)
io.setup(RELAY, io.OUT)

while True:
    io.output(RELAY, Fa
    time.sleep(0.5)
    print("test")
    io.output(RELAY, io.HIGH)
