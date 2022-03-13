from datetime import datetime
from typing import Union

from gi.repository import GLib

from camera import Camera
from person import Person, PersonParseError
from spreadsheet import Spreadsheet
from sensors.proximity import ProximitySensor
from sensors.temperature import TemperatureSensor

DEFAULT_TEMPERATURE = -1
DEFAULT_SPREADSHEET_ID = "1IA6YhAdkvdNkkPPyhCj5JQrB8dcaKZNWzk-4gI0Ea4Y"

# GPIO ports
PROXIMITY_SENSOR_IO = 4


class Application:
    _last_code: Union[str, None] = None

    _camera: Camera
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

        GLib.timeout_add_seconds(5, self._reset_last_code)

    def run(self):
        loop = GLib.MainLoop()

        try:
            loop.run()
        except KeyboardInterrupt:
            loop.quit()

    def _on_proximity_sensor_detected(self, proximity_sensor: ProximitySensor) -> None:
        print(">>> Proximity sensor detected something")
        print(f"obj: {self._temperature_sensor.get_object_temperature()}")

        # does same thing like in _handle_proximity_sensor_wait_for_input

    def _on_code_detected(self, camera: Camera, code: str) -> None:
        self._camera.handler_block(self._code_detected_handler_id)

        if self._last_code == code:
            print(">>> Same code as last, returning...")
        else:
            self._handle_new_code_detected(code)

    def _try_store_person_to_spreadsheet(self, person: Person) -> None:
        try:
            Spreadsheet(DEFAULT_SPREADSHEET_ID).append_person(person)
        except PersonParseError as error:
            print(f"Error: {error}")

    def _handle_proximity_sensor_wait_for_input(
        self, is_timeout_reached: bool, code: str
    ) -> None:
        time_detected = datetime.now().isoformat()

        if is_timeout_reached:
            print(
                ">>> Skipped dispensing alcohol or getting temperature: Timeout reached"
            )
            self._try_store_person_to_spreadsheet(
                Person.from_str(
                    f"{code}\ntime_detected: {time_detected}\ntemperature: {DEFAULT_TEMPERATURE}"
                )
            )
        else:
            temperature = self._temperature_sensor.get_object_temperature()
            # Dispense alcohol here
            # Display something here
            self._try_store_person_to_spreadsheet(
                Person.from_str(
                    f"{code}\ntime_detected: {time_detected}\ntemperature: {temperature}"
                )
            )

        self._camera.handler_unblock(self._code_detected_handler_id)
        self._proximity_sensor.handler_unblock(self._detected_handler_id)

    def _handle_new_code_detected(self, code: str) -> None:
        print(f">>> New detected code `{code}`")

        self._last_code = code

        self._proximity_sensor.handler_block(self._detected_handler_id)

        print(">>> Wait 5 seconds for hand")
        self._proximity_sensor.wait_for_input(
            5, self._handle_proximity_sensor_wait_for_input, code
        )

    def _reset_last_code(self):
        self._last_code = None
        return True
