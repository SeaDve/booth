from datetime import datetime
from typing import Union

from gi.repository import GLib

from camera import Camera
from person import Person, PersonParseError
from spreadsheet import Spreadsheet
from sensors.proximity import ProximitySensor


DEFAULT_SPREADSHEET_ID = "1IA6YhAdkvdNkkPPyhCj5JQrB8dcaKZNWzk-4gI0Ea4Y"

# GPIO ports
PROXIMITY_SENSOR_IO = 4


class Application:
    _last_code: Union[str, None] = None

    _camera: Camera
    _proximity_sensor: ProximitySensor

    def __init__(self):
        self._camera = Camera()
        self._code_detected_handler_id = self._camera.connect(
            "code-detected", self._on_code_detected
        )
        self._camera.start()

        self._proximity_sensor = ProximitySensor(PROXIMITY_SENSOR_IO)
        self._proximity_sensor.connect("detected", self._on_proximity_sensor_detected)

        GLib.timeout_add_seconds(5, self._reset_last_code)

    def run(self):
        loop = GLib.MainLoop()

        try:
            loop.run()
        except KeyboardInterrupt:
            loop.quit()

    def _on_proximity_sensor_detected(self, proximity_sensor: ProximitySensor) -> None:
        print(">>> Proximity sensor detected something")

        # does same thing like in _handle_new_code_detected

    def _on_code_detected(self, camera: Camera, code: str) -> None:
        self._camera.handler_block(self._code_detected_handler_id)

        if self._last_code == code:
            print(">>> Same code as last, returning...")
        else:
            self._handle_new_code_detected(code)

        self._camera.handler_unblock(self._code_detected_handler_id)

    def _handle_new_code_detected(self, code: str) -> None:
        print(f">>> New detected code `{code}`")

        self._last_code = code

        time_detected = datetime.now().isoformat()

        print(">>> Wait 3 seconds for hand")

        temperature = "-1"

        try:
            self._proximity_sensor.wait_for_input(5)
            temperature = "37.1"  # TODO actually get the temperature from sensor
            # Dispense alcohol here
            # Display something here
        except WaitForInputTimeout as error:
            print(f">>> Skipped dispensing alcohol or getting temperature: {error}")

        try:
            Spreadsheet(DEFAULT_SPREADSHEET_ID).append_person(
                Person.from_str(
                    f"{code}\ntime_detected: {time_detected}\ntemperature: {temperature}"
                )
            )
        except PersonParseError as error:
            print(f"Error: {error}")

    def _reset_last_code(self):
        self._last_code = None
        return True
