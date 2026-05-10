import re


CONTRACT_PATTERN = re.compile(r'^[A-Z]{2}-\d{6}\.\d{4}$')
MIN_YEAR = 2024
MAX_YEAR = 2035


def is_valid_contract(value: str) -> bool:
    match = CONTRACT_PATTERN.match(value)
    if not match:
        return False
    year = int(value.split('.')[-1])
    return MIN_YEAR <= year <= MAX_YEAR