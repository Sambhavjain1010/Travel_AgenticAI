import streamlit as st
from tools.api_caller import APICaller
from tools.web_scrapper import LLMWebScrapper
from inputs.prompt_input import build_prompt
from data.input_parser import TravelQuery
from models.llm_generator import build_llm
from langchain_core.output_parsers import StrOutputParser

llm = build_llm()
structured_model = llm.with_structured_output(TravelQuery)
api_caller = APICaller()
web_scrapper = LLMWebScrapper()
parser = StrOutputParser()
prompt = build_prompt()

st.title("AI Travel Agent")
input_text = st.text_input("Describe your travel plans:", placeholder="e.g. I want to visit Paris with my family for 7 days")

if input_text:
    with st.spinner("🔍 Analyzing your request and gathering real-time data..."):
        structured_result = structured_model.invoke(input_text)

        travel_dict = dict(structured_result)

        st.write("📊 Collecting real-time information...")

        weather_data = api_caller.get_weather_forecast(travel_dict['destination'])
        
        flight_data = None
        origin_country = travel_dict.get('origin') or 'India'

        if travel_dict.get('origin'):
            flight_data = api_caller.find_flights(origin_country, travel_dict['destination'])
        
        visa_data = web_scrapper.scrape_visa_requirements(travel_dict['destination'], origin_country)

        combined_data = {
            'duration': travel_dict.get('duration', 'flexible'),
            'destination': travel_dict.get('destination', ''),
            'traveler_type': travel_dict.get('traveler_type', 'solo'),
            'interests': travel_dict.get('interests', 'tourism'),
            'budget': travel_dict.get('budget', 'not specified'),
            'departure_date': travel_dict.get('departure_date', 'flexible'),
            'origin': origin_country,
            # --- Start of Corrected Block ---
            # This line was missing. The prompt template needs an 'intent' variable.
            'intent': travel_dict.get('intent', 'tourism'),
            # --- End of Corrected Block ---
            'weather_info': weather_data,
            'flight_info': flight_data,
            'visa_info': visa_data
        }
        chain = prompt | llm | parser
        result = chain.invoke(combined_data)

        st.markdown(result)
