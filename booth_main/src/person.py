from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import yaml


class PersonParseError(Exception):
    def __init__(self, inner: Exception, parsed: str):
        self._inner = inner
        self._parsed = parsed

    def __str__(self):
        return f"Failed to construct Person from `{self._parsed}`: {repr(self._inner)}"


@dataclass
class Person:
    name: str
    address: str
    contact_number: str
    room_id: str
    temperature: float
    time_detected: datetime

    @staticmethod
    def from_str(string: str) -> Person:
        try:
            data = yaml.safe_load(string)

            time_detected_data = data["time_detected"]
            time_detected = (
                datetime.fromisoformat(time_detected_data)
                if isinstance(time_detected_data, str)
                else time_detected_data
            )

            return Person(
                data["name"],
                data["address"],
                data["contact_number"],
                data["room_id"],
                float(data["temperature"]),
                time_detected,
            )
        except (ValueError, KeyError, yaml.scanner.ScannerError) as error:
            raise PersonParseError(error, string)
