from langchain.tools import tool
from tools.api_caller import APICaller
import json
from tools.web_scrapper import LLMWebScrapper

api_caller = APICaller()
web_scrapper = LLMWebScrapper()

@tool
def get_weather_tool (city: str) ->str:
    """
    Finds the weather forecast for a given city. 
    Use this for any questions about weather conditions.
    Input should be a single city name (e.g. 'Paris').
    """
    weather_data = api_caller.get_weather_forecast(city=city)
    return json.dumps(weather_data)

@tool
def get_flights_tool(origin_city: str, dest_city: str) -> str:
    """
    Finds flight information between an origin and a destination. 
    Use this for any questions about finding flights.
    Input should be two city names separated by a comma (e.g. 'New Delhi, London').
    """
    flight_data = api_caller.plan_flights(origin_place=origin_city, dest_place=dest_city)
    return json.dumps(flight_data)

@tool
def get_visa_requirements_tool (dest_country: str, passport_country: str) -> str:
    """
    Finds the visa requirements for a traveler.
    Use this for any questions about visas.
    Input should be the destination country and the passport-holding country, separated by a comma (e.g. 'France, India').
    """
    if not passport_country:
        passport_country = "India"
    visa_data = web_scrapper.scrape_visa_requirements(destination_country=dest_country, passport_country=passport_country)
    return json.dumps(visa_data)
