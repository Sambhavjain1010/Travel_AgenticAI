from langchain_core.prompts import PromptTemplate

def build_prompt():
    prompt = PromptTemplate(
        template="""
        I'm planning a {duration} day trip to {destination} with {traveler_type} for a {interests} vacation.
        """,
        input_variables=['duration', 'destination', 'traveler_type', 'interests']
    )

    return prompt