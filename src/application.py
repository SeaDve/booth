from datetime import datetime

from gi.repository import GLib

from camera import Camera
from person import Person, PersonParseError
from spreadsheet import Spreadsheet


DEFAULT_SPREADSHEET_ID = "1IA6YhAdkvdNkkPPyhCj5JQrB8dcaKZNWzk-4gI0Ea4Y"


class Application:
    _camera: Camera
    _last_code: str | None = None
    _loop = GLib.MainLoop()

    def __init__(self):
        self._camera = Camera()
        self._code_detected_handler_id = self._camera.connect(
            "code-detected", self._on_code_detected
        )
        self._camera.start()

        GLib.timeout_add_seconds(5, self._reset_last_code)

    def run(self):
        self._loop.run()

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
        temperature = "37.1"  # TODO actually get the temperature from sensor

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
