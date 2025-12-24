import re
from typing import List

def celsius_to_fahrenheit(celsius: float) -> float:
    return round((celsius * 9/5) + 32, 1)

def knots_to_mph(knots: float) -> float:
    return round(knots * 1.15078, 1)

def format_visibility(visibility_str: str) -> str:
    if not visibility_str: return "N/A"
    return visibility_str.replace("SM", " miles")

def parse_lowest_ceiling(clouds: List[str]) -> float:
    lowest = float('inf')
    if not clouds: return lowest
    for layer in clouds:
        match = re.match(r'(BKN|OVC)(\d{3})', layer)
        if match:
            height_ft = int(match.group(2)) * 100
            if height_ft < lowest:
                lowest = height_ft
    return lowest