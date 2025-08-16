import streamlit as st
from inputs.prompt_input import build_prompt
from data.input_parser import TravelQuery
from models.llm_generator import build_llm
from langchain_core.output_parsers import StrOutputParser

llm = build_llm()
structured_model = llm.with_structured_output(TravelQuery)
parser = StrOutputParser()
prompt = build_prompt()

input_text = st.text_input("Enter the Input")

if input_text:
    with st.spinner("Generating your itenary......"):
        structured_result = structured_model.invoke(input_text)

        travel_dict = dict(structured_result)
        print(travel_dict['traveler_type'])
        print(structured_result)
        chain = prompt | llm | parser
        result = chain.invoke(travel_dict)

        st.markdown(result)