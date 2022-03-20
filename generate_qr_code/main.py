import csv
import errno
import os
import sys
from argparse import Namespace
from pathlib import Path
from typing import List

import qrcode
import pandas

BOLD = "\033[1m"
RED = "\033[31m"
BLUE = "\033[34m"
ENDC = "\033[0m"


class InvalidHeader(Exception):
    def __init__(
        self, missing_column_no: int, missing_column_name: str, found_instead: str
    ):
        self._missing_column_no = missing_column_no
        self._missing_column_name = missing_column_name
        self._found_instead = found_instead

    def __str__(self):
        return (
            f"Missing `{self._missing_column_name}` at column `{self._missing_column_no}`. "
            f"Found `{self._found_instead}` instead."
        )


def log_error(text: str) -> None:
    print(f"{BOLD}{RED}ERROR{ENDC}: {text}")


def log_info(text: str) -> None:
    print(f"{BOLD}{BLUE}INFO{ENDC}: {text}")


# From https://stackoverflow.com/a/34325723 CC BY-SA 4.0
def progressBar(
    iterable, prefix="", suffix="", decimals=1, length=100, fill="█", printEnd="\r"
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)

    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total))
        )
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + "-" * (length - filledLength)
        print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)

    printProgressBar(0)
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    print()


def excel_file_to_csv(excel_file_path: Path) -> str:
    df = pandas.read_excel(excel_file_path)
    return df.to_csv(None, index=None, header=True)


def create_and_save_qr_code(data: str, path: Path) -> None:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(fill="black", back_color="white")
    image.save(path)


def valididate_header(header: List[str], column_no: int, column_name: str) -> None:
    found_val = header[column_no].lower()
    if not found_val == column_name.lower():
        error = InvalidHeader(column_no, column_name, found_val)
        log_error(str(error))
        raise error


def main(args: Namespace) -> int:
    log_info(f"Excel File Path found is `{args.excel_file_path.resolve()}`")

    csv_content = excel_file_to_csv(args.excel_file_path)
    csv_data = csv.reader(csv_content.splitlines(), delimiter=",")

    csv_data_iterator = iter(csv_data)
    header = next(csv_data_iterator)

    valididate_header(header, 0, "name")
    valididate_header(header, 1, "address")
    valididate_header(header, 2, "contact number")
    valididate_header(header, 3, "room id")

    csv_data_no_header = list(csv_data_iterator)

    try:
        os.makedirs(args.output_folder)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    for row in progressBar(
        csv_data_no_header, prefix="Encoding progress:", suffix="Complete", length=50
    ):
        name = row[0]
        address = row[1]
        contact_number = row[2]
        room_id = row[3]

        qr_content = f"""
name: {name}
address: {address}
contact_number: {contact_number}
room_id: {room_id}
"""
        create_and_save_qr_code(
            qr_content, args.output_folder / f"{name}_{contact_number}.png"
        )

    log_info(f"Done. Saved QR codes at path {args.output_folder.resolve()}")

    return 0


def parse_args() -> Namespace:
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="Generate QR codes from an Excel file. It must have the following rows: "
        "Name(str), Address(str), Contact Number(int), Room ID(str)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Use verbose output"
    )
    parser.add_argument("excel_file_path", type=Path, help="Path to the Excel file")
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Directory where to store the output QR codes",
    )
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main(parse_args()))
