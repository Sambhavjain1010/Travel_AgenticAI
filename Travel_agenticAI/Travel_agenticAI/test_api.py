from tools.api_caller import APICaller

api = APICaller()

# print("Weather API")
# weather_data = api.get_weather_forecast("Delhi")
# print ("weather Data: ", weather_data)

# print("Visa api")
# visa_data = api.get_visa_info("India", "UK")
# print("Visa Data:", visa_data)

# print("Safety API")
# safety_data = api.get_safety_index("Barcelona")
# print("safety data:", safety_data)

print("flight API")
flight_data = api.find_flights("DEL", "LHR")
print("flight data:", flight_data)