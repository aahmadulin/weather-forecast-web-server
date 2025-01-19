import httpx
import asyncio

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

async def get_weather(latitude, longitude, current=None, hourly=None):
    async with httpx.AsyncClient() as client:
        params = {
            "latitude": latitude,
            "longitude": longitude,
        }

        if current:
            params["current"] = current

        if hourly:
            params["hourly"] = hourly

        response = await client.get(OPEN_METEO_URL, params=params)
        return response.json()

def fetch_weather(latitude, longitude, current="temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,pressure_msl", hourly="precipitation"):
    return asyncio.run(get_weather(latitude, longitude, current, hourly))
