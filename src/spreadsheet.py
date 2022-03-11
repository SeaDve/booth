import gspread

from person import Person

AUTHORIZED_PATH = "./token_cache.json"
CREDENTIALS_PATH = "./credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class Spreadsheet:
    def __init__(self, id: str):
        client = gspread.oauth(
            scopes=SCOPES,
            credentials_filename=CREDENTIALS_PATH,
            authorized_user_filename=AUTHORIZED_PATH,
        )
        self._inner = client.open_by_key(id)

    def append_person(self, person: Person):
        worksheet = self._inner.get_worksheet(0)
        worksheet.append_row(
            [
                person.name,
                person.address,
                person.contact_number,
                person.room_id,
                str(person.temperature),
                str(person.time_detected),
            ]
        )
        print(f">>> Appended Person {person}")
