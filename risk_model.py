from typing import Dict, Tuple, List
from backend.utils import parse_lowest_ceiling

class RiskModel:
    def predict(self, weather_data: Dict) -> Tuple[int, List[str], str]:
        score = 0
        factors = []

        # 1. Wind Analysis
        wind = weather_data.get("wind_speed_kt", 0)
        if wind >= 25:
            score += 40
            factors.append(f"High Wind ({wind} kts)")
        elif wind >= 15:
            score += 20
            factors.append(f"Gusty Wind ({wind} kts)")

        # 2. Visibility Analysis
        vis = weather_data.get("visibility_sm")
        if vis is not None:
            if vis < 1.0:
                score += 40
                factors.append(f"Low Visibility ({vis} sm)")
            elif vis < 3.0:
                score += 20
                factors.append(f"Reduced Visibility ({vis} sm)")

        # 3. Ceiling Analysis
        clouds = weather_data.get("clouds", [])
        ceiling = parse_lowest_ceiling(clouds)
        
        if ceiling < 1000:
            score += 30
            factors.append(f"Low Ceiling ({ceiling} ft)")
        elif ceiling < 3000:
            score += 10
            factors.append(f"Marginal Ceiling ({ceiling} ft)")

        # Final Score
        score = min(score, 100)
        
        if score < 30: level = "LOW"
        elif score < 60: level = "MODERATE"
        else: level = "HIGH"
            
        return score, factors, level