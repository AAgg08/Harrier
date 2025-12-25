import requests

def get_metar_data(icao_code: str, api_key: str = None) -> dict:
    """
    Fetches REAL LIVE METAR data from the NOAA Aviation Weather Center.
    Cost: FREE. No API Key required.
    """
    icao = icao_code.upper()
    url = f"https://aviationweather.gov/api/data/metar?ids={icao}&format=json"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if not data:
            return {}

        metar = data[0]

        # Extract Cloud Layers
        cloud_layers = []
        for c in metar.get('clouds', []):
            cover = c.get('cover', 'CLR')
            base = c.get('base', None)
            if base:
                fmt_base = int(base / 100)
                cloud_layers.append(f"{cover}{fmt_base:03d}")
            else:
                cloud_layers.append(cover)

        return {
            "icao": icao,
            "temperature_c": metar.get('temp', 0.0),
            "wind_speed_kt": metar.get('wspd', 0.0),
            "wind_direction_deg": metar.get('wdir', 0),
            "visibility_sm": extract_visibility(metar.get('visib', '10')),
            "clouds": cloud_layers,
            "raw": metar.get('rawOb', 'Raw data unavailable')
        }

    except Exception as e:
        print(f"Weather Fetch Failed: {e}")
        return {}

def extract_visibility(vis_entry):
    try:
        if isinstance(vis_entry, (int, float)):
            return float(vis_entry)
        clean = str(vis_entry).replace('+', '')
        return float(clean)
    except:
        return 10.0
