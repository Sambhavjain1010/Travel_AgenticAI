# weather and flight APIs are working, rest are not working
import requests
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from airports import airport_data
from dotenv import load_dotenv

load_dotenv()

class APICallerError(Exception):
    """Custom exception for API caller errors"""
    pass

class APICaller:
    def __init__(self):
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.aviationstack_api_key = os.getenv("AVIATIONSTACK_API_KEY")
        self.aviationstack_api_endpoint = os.getenv("AVIATIONSTACK_API_ENDPOINT")

    def get_weather_forecast(self, city:str, days:int = 5) -> Dict[str, Any]:
        """Get weather forecast for a city"""

        try:
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': city,
                'appid': self.openweather_api_key,
                'units': 'metric',
                'cnt': min(days * 8, 40)
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            forecasts = []
            daily_forecasts = {}

            for item in data['list']:
                date = item['dt_txt'].split(' ')[0]  
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(item)

            for date, day_forecasts in list(daily_forecasts.items())[:days]:  
                midday_forecast = None
                for forecast in day_forecasts:
                    if '12:00:00' in forecast['dt_txt']:
                        midday_forecast = forecast
                        break
                
                if not midday_forecast:
                    midday_forecast = day_forecasts[0]
                
                forecasts.append({
                    'date': date,
                    'datetime': midday_forecast['dt_txt'],
                    'temperature': midday_forecast['main']['temp'],
                    'feels_like': midday_forecast['main']['feels_like'],
                    'humidity': midday_forecast['main']['humidity'],
                    'description': midday_forecast['weather'][0]['description'].title(),
                    'main': midday_forecast['weather'][0]['main'],
                    'wind_speed': midday_forecast.get('wind', {}).get('speed', 'N/A'),
                    'clouds': midday_forecast.get('clouds', {}).get('all', 'N/A')
                })
            
            return {
                'city': city,
                'country': data['city']['country'],
                'timezone': data['city']['timezone'],
                'forecasts': forecasts,
                'total_forecasts': len(forecasts)
            }
        except Exception as e:
            return {
                'city': city,
                'error': f"Could not fetch weather info: {str(e)}",
                'forecasts': []
            }
        
    def find_flights(self, origin: str, destination: str, departure_date: str = None,
                     return_date: str = None, adults: int = 1) -> Dict[str, Any]:
        """Find flights between two locations"""
        try:
            url = f"{self.aviationstack_api_endpoint}/flights"
            params = {
                'access_key': self.aviationstack_api_key,
                'dep_iata': origin,
                'arr_iata': destination,
                'limit': 10
            }

            if departure_date:
                params['flight_date'] = departure_date
            
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            flights = []
            
            if not data.get('data'):
                return {
                    'origin': origin,
                    'destination': destination,
                    'flights': [],
                    'error': 'No flights found for the specified route',
                    'suggestions': 'Try checking major airport codes or different dates'
                }
            for flight in data['data'][:5]:
                airline = flight.get('airline') or {}
                flight_info = {
                    'flight_number': f"{airline.get('iata', 'N/A')}{(flight.get('flight') or {}).get('number', '')}",
                    'airline': airline.get('name', 'Unknown'),
                    'aircraft': (flight.get('aircraft') or {}).get('registration', 'N/A'),
                    'departure': {
                        'airport': (flight.get('departure') or {}).get('airport', 'N/A'),
                        'scheduled': (flight.get('departure') or {}).get('scheduled', 'N/A'),
                        'estimated': (flight.get('departure') or {}).get('estimated', 'N/A'),
                        'terminal': (flight.get('departure') or {}).get('terminal', 'N/A'),
                        'gate': (flight.get('departure') or {}).get('gate', 'N/A')
                    },
                    'arrival': {
                        'airport': (flight.get('arrival') or {}).get('airport', 'N/A'),
                        'scheduled': (flight.get('arrival') or {}).get('scheduled', 'N/A'),
                        'estimated': (flight.get('arrival') or {}).get('estimated', 'N/A'),
                        'terminal': (flight.get('arrival') or {}).get('terminal', 'N/A'),
                        'gate': (flight.get('arrival') or {}).get('gate', 'N/A')
                    },
                    'status': flight.get('flight_status', 'Unknown')
                }
                flights.append(flight_info)

            return {
                'origin': origin,
                'destination': destination,
                'flights': flights,
                'search_date': departure_date or 'Live data',
                'note': 'Live flight tracking data'
            }
        except Exception as e:
            return {
                'origin': origin,
                'destination': destination,
                'error': f"Could not fetch flight details {str(e)}",
                'flights': [],
                'suggestion': 'Please verify airport codes and try again'
            }
        
    def get_route_flights(self, origin: str, destination: str) -> Dict[str, Any]:
        """Get route information between airports using AviationStack"""
        try:
            url = f"{self.aviationstack_api_endpoint}/routes"
            
            params = {
                'access_key': self.aviationstack_api_key,
                'dep_iata': origin,
                'arr_iata': destination
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('data'):
                return {
                    'origin': origin,
                    'destination': destination,
                    'routes': [],
                    'message': 'No routes found between these airports'
                }
            
            routes = []
            for route in data['data']:
                route_info = {
                    'airline': route.get('airline_name', 'Unknown'),
                    'airline_iata': route.get('airline_iata', 'N/A'),
                    'flight_number': route.get('flight_number', 'N/A'),
                    'departure_airport': route.get('dep_airport', 'N/A'),
                    'arrival_airport': route.get('arr_airport', 'N/A')
                }
                routes.append(route_info)
            
            return {
                'origin': origin,
                'destination': destination,
                'routes': routes,
                'total_routes': len(routes)
            }
        except Exception as e:
            return {
                'origin': origin,
                'destination': destination,
                'error': f"Could not fetch route info: {str(e)}",
                'routes': []
            }
        
    def get_iata_codes(self, place: str, country: str = None, max_results: int = 3) -> list:
        url = f"{self.aviationstack_api_endpoint}/airports"
        params = {
            'access_key': self.aviationstack_api_key,
            'search': place
        }

        if country:
            params['country_name'] = country
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json().get("data", [])
            airports = sorted(
                [ap for ap in data if ap.get("iata_code")],
                key=lambda ap: ("international" not in (ap.get("airport_name") or "").lower(), ap.get("airport_name") or "")
            )
            seen_iata = set()
            top = []
            for ap in airports:
                code = ap["iata_code"]
                if code not in seen_iata:
                    seen_iata.add(code)
                    top.append({
                        "airport_name": ap.get("airport_name"),
                        "iata_code": code,
                        "city": ap.get("city_name"),
                        "country": ap.get("country_name")
                    })
                if len(top) >= max_results:
                    break
            return top
        except Exception as e:
            print(f"[airport lookup] Error: {e}")
            return []
        
    def get_main_iata_for_place(self, place, country=None):
        airports = self.get_iata_codes(place, country)
        if airports:
            # Default: pick first (most likely the main airport)
            return airports[0]['iata_code']
        return None

    def plan_flights(self, origin_place, dest_place, departure_date=None, return_date=None):
        origin_code = self.get_main_iata_for_place(origin_place)
        dest_code = self.get_main_iata_for_place(dest_place)
        if not origin_code or not dest_code:
            return {
                "error": f"Could not resolve airport codes for '{origin_place}' or '{dest_place}'"
            }
        return self.find_flights(origin=origin_code, destination=dest_code, departure_date=departure_date, return_date=return_date)
