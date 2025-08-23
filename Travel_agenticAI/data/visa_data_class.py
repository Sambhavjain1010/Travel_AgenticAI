from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any, List
from enum import Enum

class VisaRequirement(BaseModel):
    visa_type: Literal['visa_free', 'visa_on_arrival', 'e_visa', 'visa_required', 'unknown'] = Field(description="Type of visa requirement")
    max_stay_days: Optional[int] = Field(description="Maximum number of days allowed for stay")
    processing_time: Optional[str] = Field(description="Visa processing time")
    validity_period: Optional[str] = Field(description="Visa validity period")
    cost: Optional[str] = Field(description="Cost/Fee of visa")
    requirements: Optional[List[str]] = Field(description="List of required documents and conditions")

class ExtractedVisaInfo(BaseModel):
    destination_country: str = Field(description="Destination country name")
    passport_country: str = Field(description="Passport/citizenship country")
    visa_requirement: VisaRequirement = Field(description="Visa requirement details")
    special_notes: List[str] = Field(description="Important notes, restrictions, or special conditions")
    reciprocity_info: Optional[str] = Field(description="Any reciprocity agreements mentioned")
    embassy_info: Optional[str] = Field(description="Embassy or consulate information if mentioned")
    last_updated: Optional[str] = Field(description="When the information was last updated")
    confidence_level: float = Field(description="Confidence in extracted information (0.0-1.0)")