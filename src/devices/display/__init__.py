from typing import List, Optional

from gi.repository import GLib

from .driver import Lcd

DISPLAY_LENGTH = 16
DISPLAY_HEIGHT = 2


class Display:
    _timeout_id = None

    def __init__(self, default_text: Optional[List[str]]):
        self._inner = Lcd(addr=0x27)
        self._default_text = default_text

        if self._default_text is not None:
            self.write(self._default_text)

    def __del__(self):
        self._inner.lcd_clear()

    def ephemeral_write(self, string_list: List[str], duration_secs: int) -> None:
        self.write(string_list)
        self._timeout_id = GLib.timeout_add_seconds(duration_secs, self.reset)

    def write(self, string_list: List[str]) -> None:
        if self._timeout_id is not None:
            GLib.source_remove(self._timeout_id)
            self._timeout_id = None

        if len(string_list) > DISPLAY_HEIGHT:
            print(
                f"WARNING: Trying to display multiple line of {len(string_list)} that cannot fit"
            )

        for index, string in enumerate(string_list):
            line_number = index + 1

            if len(string) > DISPLAY_LENGTH:
                print(
                    f"WARNING: Trying to display '{string}' of len {len(string)} that cannot fit"
                )

            self._inner.lcd_display_string(string, line_number)

    def reset(self) -> None:
        if self._default_text is not None:
            self.write(self._default_text)
        else:
            self._inner.lcd_clear()
