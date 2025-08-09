# from models.llm_generator import build_llm
from pydantic import BaseModel, Field
from typing import Optional, Literal

class TravelQuery (BaseModel):
    destination: str = Field(description="Place to travel, itenary will be prepared according to this")
    duration: Optional[int] = Field(description="The number of days for travel")
    traveler_type: Optional[Literal['family', 'couple', 'friends', 'solo']] = Field(description="The kind of people user is travelling with")
    interests: Optional[str] = Field(description="The kind of activities user is interested in.")
    budget: Optional[str] = Field(description="User's budget for the trip")