import sys

BOLD = "\033[1m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
ENDC = "\033[0m"


def log_info(text: str) -> None:
    print(f"{BOLD}{BLUE}INFO{ENDC}: {text}")


def log_warn(text: str) -> None:
    print(f"{BOLD}{YELLOW}WARN{ENDC}: {text}", file=sys.stderr)


def log_error(text: str) -> None:
    print(f"{BOLD}{RED}ERROR{ENDC}: {text}", file=sys.stderr)
