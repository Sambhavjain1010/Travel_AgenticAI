# weather and flight APIs are working, rest are not working
import requests
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

load_dotenv()

class APICallerError(Exception):
    """Custom exception for API caller errors"""
    pass

class APICaller:
    def __init__(self):
        self.amadeus_token = None
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.x_rapidapi_key = os.getenv("X_RAPIDAPI_KEY")
        self.x_rapidapi_host = os.getenv("X_RAPIDAPI_HOST")
        self.aviationstack_api_key = os.getenv("AVIATIONSTACK_API_KEY")
        self.aviationstack_api_endpoint = os.getenv("AVIATIONSTACK_API_ENDPOINT")
        self.amadeus_safety_api_key = os.getenv("AMADEUS_SAFETY_API_KEY")
        self.amadeus_safety_api_secret = os.getenv("AMADEUS_SAFETY_API_SECRET")

    def _get_amadeus_token(self):
        """Get Amadeus API access token"""
        if self.amadeus_token:
            return self.amadeus_token
        
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.amadeus_safety_api_key,
            'client_secret': self.amadeus_safety_api_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            self.amadeus_token = response.json()['access_token']
            return self.amadeus_token
        except Exception as e:
            raise APICallerError(f"Failed to get Amadeus token: {str(e)}")

    def get_visa_info(self, destination_country: str, passport_country: str) -> Dict[str, Any]:
        """Get Visa requirements using X-RapidAPI"""
        try: 
            url = "https://visa-requirement.p.rapidapi.com/visa-requirements"

            headers = {
                'X-RapidAPI-Key': self.x_rapidapi_key,
                'X-RapidAPI-Host': 'visa-requirement.p.rapidapi.com',
                'Content-Type': "application/x-www-form-urlencoded"
            }

            params = {
                'passport': passport_country,
                'destination': destination_country
            }

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                'passport_country': passport_country,
                'destination_country': destination_country,
                'visa_required': data.get('visa_required', 'Unknown'),
                'requirements': data.get('requirements', []),
                'processing_time': data.get('processing_time', 'N/A'),
                'visa_type': data.get('visa_type', 'N/A'),
                'max_stay': data.get('max_stay', 'N/A'),
                'notes': data.get('notes', '')
            }
        except Exception as e:
            return {
                'passport_country': passport_country,
                'destination_country': destination_country,
                'error': f"Could not fetch visa info: {str(e)}",
                'visa_required': 'Please check official government sources'
            }
    def _get_city_coordinates_amadeus(self, city: str) -> Optional[Dict[str, float]]:
        token = self._get_amadeus_token()
        url = "https://test.api.amadeus.com/v1/reference-data/locations"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "keyword": city,
            "subType": "CITY"
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("data"):
                geo = data["data"][0]["geoCode"]
                return {"lat": geo["latitude"], "lon": geo["longitude"]}
            return None
        except:
            return None
        
    def get_safety_index(self, city: str) ->Dict[str, Any]:
        """Get safety index for a city"""
        try:
            # using Amadeus Safe Place API
            token = self._get_amadeus_token()

            # Getting coordinates for the city
            geocoding_response = self._get_city_coordinates_amadeus(city)
            if not geocoding_response:
                raise APICallerError("Could not geocode city")
            
            lat, lon = geocoding_response['lat'], geocoding_response['lon']

            url = "https://test.api.amadeus.com/v1/safety/safety-rated-locations"
            headers = {"Authorization": f"Bearer {token}"}

            params = {
                'latitude': lat,
                'longitude': lon,
                'radius': 10
            }

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            
            if not data.get('data'):
                return {
                    'city': city,
                    'error': 'No safety data available for this location',
                    'overall_safety': 'N/A'
                }
            
            safety_data = data['data'][0]
            safety_scores = safety_data.get('safetyScores', {})
            
            return {
                'city': city,
                'latitude': lat,
                'longitude': lon,
                'overall_safety': safety_scores.get('overall', 'N/A'),
                'lgbtq_safety': safety_scores.get('lgbtq', 'N/A'),
                'medical_safety': safety_scores.get('medical', 'N/A'),
                'theft_safety': safety_scores.get('theft', 'N/A'),
                'women_safety': safety_scores.get('women', 'N/A'),
                'physical_harm': safety_scores.get('physicalHarm', 'N/A'),
                'political_freedom': safety_scores.get('politicalFreedom', 'N/A')
            }
        except Exception as e:
            return {
                'city': city,
                'error': f"Could not fetch safety info: {str(e)}",
                'overall_safety': 'Please check local travel advisories'
            }
    
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
        
    def get_airport_info(self, airport_code: str) -> Dict[str, Any]:
        """Get airport information using AviationStack"""
        try:
            url = f"{self.aviationstack_api_endpoint}/airports"
            
            params = {
                'access_key': self.aviationstack_api_key,
                'search': airport_code
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('data'):
                return {
                    'airport_code': airport_code,
                    'error': 'Airport not found'
                }
            
            airport = data['data'][0]
            return {
                'airport_code': airport_code,
                'name': airport.get('airport_name', 'N/A'),
                'iata_code': airport.get('iata_code', 'N/A'),
                'icao_code': airport.get('icao_code', 'N/A'),
                'country': airport.get('country_name', 'N/A'),
                'city': airport.get('city_name', 'N/A'),
                'timezone': airport.get('timezone', 'N/A'),
                'latitude': airport.get('latitude', 'N/A'),
                'longitude': airport.get('longitude', 'N/A')
            }
        except Exception as e:
            return {
                'airport_code': airport_code,
                'error': f"Could not fetch airport info: {str(e)}"
            }
        
    def _geocode_city(self, city: str) -> Optional[Dict[str, float]]:
        """Helper function to get geocode of a city using OpenWeatherMap geocoding"""

        try:
            url="http://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': city,
                'limit': 1,
                'appid': self.openweather_api_key
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data:
                return {
                    'lat': data[0]['lat'],
                    'lon': data[0]['lon']
                }
            return None
        except:
            return None