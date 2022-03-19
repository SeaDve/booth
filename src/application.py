from threading import Thread
from datetime import datetime
from typing import Union

from gi.repository import GLib

from camera import Camera
from person import Person, PersonParseError
from spreadsheet import Spreadsheet
from devices.proximity import ProximitySensor
from devices.temperature import TemperatureSensor
from devices.display import Display
from devices.relay import Relay

DEFAULT_TEMPERATURE = -1
DEFAULT_SPREADSHEET_ID = "1IA6YhAdkvdNkkPPyhCj5JQrB8dcaKZNWzk-4gI0Ea4Y"

# GPIO ports
PROXIMITY_SENSOR_IO = 4
PUMP_IO = 17
BUZZER_IO = 24


class Application:
    _last_code: Union[str, None] = None

    _camera: Camera
    _display: Display
    _pump: Relay
    _buzzer: Relay
    _proximity_sensor: ProximitySensor
    _temperature_sensor: TemperatureSensor

    def __init__(self):
        self._camera = Camera()
        self._code_detected_handler_id = self._camera.connect(
            "code-detected", self._on_code_detected
        )
        self._camera.start()

        self._proximity_sensor = ProximitySensor(PROXIMITY_SENSOR_IO)
        self._detected_handler_id = self._proximity_sensor.connect(
            "detected", self._on_proximity_sensor_detected
        )

        self._temperature_sensor = TemperatureSensor()

        self._display = Display(["   ^   ^   ^    ", "Scan code above "])

        self._pump = Relay(PUMP_IO, True)

        self._buzzer = Relay(BUZZER_IO)

        GLib.timeout_add_seconds(5, self._reset_last_code)

    def run(self):
        loop = GLib.MainLoop()

        try:
            loop.run()
        except KeyboardInterrupt:
            loop.quit()
        finally:
            self._display.clear()

    def _on_proximity_sensor_detected(self, proximity_sensor: ProximitySensor) -> None:
        print(">>> Proximity sensor detected something")

        self._proximity_sensor.handler_block(self._detected_handler_id)

        self._pump.ephemeral_on(1500)
        temperature = self._temperature_sensor.get_object_temperature()
        self._display.ephemeral_write(
            ["  Temperature   ", f"     {temperature:.1f} C     "], 3
        )

        person = Person.from_str(
            f"""
name: Unknown
address: Unknown
contact_number: Unknown
room_id: Unknown
time_detected: {datetime.now().isoformat()}
temperature: {temperature}
"""
        )
        self._try_store_person_to_spreadsheet(person)

        self._proximity_sensor.handler_unblock(self._detected_handler_id)

    def _on_code_detected(self, camera: Camera, code: str) -> None:
        self._camera.handler_block(self._code_detected_handler_id)
        self._proximity_sensor.handler_block(self._detected_handler_id)

        if self._last_code == code:
            print(">>> Same code as last, returning...")
        else:
            self._buzzer.ephemeral_on(500)
            self._handle_new_code_detected(code)

    def _store_person_to_spreadsheet_thread(self, person: Person) -> None:
        Spreadsheet(DEFAULT_SPREADSHEET_ID).append_person(person)

    def _try_store_person_to_spreadsheet(self, person: Person) -> None:
        try:
            thread = Thread(
                target=self._store_person_to_spreadsheet_thread, args=[person]
            )
            thread.run()
        except PersonParseError as error:
            print(f"Error: {error}")

    def _handle_proximity_sensor_wait_for_input(
        self, is_timeout_reached: bool, code: str
    ) -> None:
        temperature = DEFAULT_TEMPERATURE

        if is_timeout_reached:
            self._display.write(["   Received no  ", "  Temperature   "])
            print(
                ">>> Skipped dispensing alcohol and getting temperature: Timeout reached"
            )

        else:
            print(
                ">>> Proximity sensor detected something. Dispensing alcohol and getting temp"
            )

            self._pump.ephemeral_on(1500)
            temperature = self._temperature_sensor.get_object_temperature()
            self._display.write(["  Temperature   ", f"     {temperature:.1f} C     "])

        person = Person.from_str(
            f"{code}\ntime_detected: {datetime.now().isoformat()}\ntemperature: {temperature}"
        )
        self._try_store_person_to_spreadsheet(person)

        self._display.ephemeral_write([f"Hi {person.name}", "  Info logged   "], 3)

        self._camera.handler_unblock(self._code_detected_handler_id)
        self._proximity_sensor.handler_unblock(self._detected_handler_id)

    def _handle_new_code_detected(self, code: str) -> None:
        print(f">>> New detected code `{code}`")

        self._last_code = code

        print(">>> Wait 5 seconds for hand")
        self._display.write([" Code detected! ", "temp&alcohol v v"])
        self._proximity_sensor.wait_for_input(
            5, self._handle_proximity_sensor_wait_for_input, code
        )

    def _reset_last_code(self):
        self._last_code = None
        return True
