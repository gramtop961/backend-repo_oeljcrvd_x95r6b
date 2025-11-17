from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import date

PHONE_REGEX = r"^\d{10}$"


class VehiclePhoto(BaseModel):
    url: str
    filename: Optional[str] = None


class Vehicle(BaseModel):
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    price: Optional[float] = None
    mileage: Optional[int] = None
    stock_number: Optional[str] = None
    vin: Optional[str] = Field(None, min_length=11, max_length=17)
    engine: Optional[str] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    fuel_type: Optional[str] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    photos: List[VehiclePhoto] = []
    featured: bool = False

    class Config:
        schema_extra = {
            "example": {
                "year": 2019,
                "make": "Honda",
                "model": "Civic",
                "trim": "EX",
                "price": 16990,
                "mileage": 45500,
                "stock_number": "B1234",
                "vin": "2HGFC2F59KH123456",
                "engine": "2.0L I4",
                "transmission": "Automatic",
                "drivetrain": "FWD",
                "fuel_type": "Gasoline",
                "exterior_color": "White",
                "interior_color": "Black",
                "photos": [{"url": "https://picsum.photos/seed/civic/1200/800"}],
                "featured": True,
            }
        }


class ContactBase(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(..., regex=PHONE_REGEX)


class MessageLead(ContactBase):
    message: Optional[str] = None
    vehicle_id: Optional[str] = None
    trade_in: Optional[bool] = None


class OfferLead(ContactBase):
    offer_amount: float
    vehicle_id: Optional[str] = None


class ApplyOnline(BaseModel):
    # Personal
    first_name: str
    last_name: str
    email: EmailStr
    cell_phone: str = Field(..., regex=PHONE_REGEX)
    home_phone: Optional[str] = Field(None, regex=PHONE_REGEX)
    dob: date
    ssn: str
    dl_number: str
    dl_state: str
    dl_issue_date: date
    dl_expiry_date: date

    # Residential
    street: str
    city: str
    state: str
    zip_code: str
    housing_type: str
    monthly_rent: float
    years_at_address: float
    prev_street: Optional[str] = None
    prev_city: Optional[str] = None
    prev_state: Optional[str] = None
    prev_zip_code: Optional[str] = None

    # Employment
    employer_name: str
    title: str
    employer_phone: str = Field(..., regex=PHONE_REGEX)
    monthly_gross_income: float
    years_at_job: float
    other_income_amount: Optional[float] = None
    other_income_source: Optional[str] = None

    # Interested vehicle
    vehicle_year: Optional[int] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_stock_or_vin: Optional[str] = None


class SellTrade(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(..., regex=PHONE_REGEX)
    zip: str

    year: int
    make: str
    model: str
    trim: Optional[str] = None
    mileage: int
    vin: Optional[str] = None
    condition: Optional[str] = None
    payoff_info: Optional[str] = None


class CarFinder(BaseModel):
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    body_style: Optional[str] = None
    mileage_min: Optional[int] = None
    mileage_max: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    notes: Optional[str] = None

    name: str
    email: EmailStr
    phone: str = Field(..., regex=PHONE_REGEX)
    best_time_to_contact: Optional[str] = None
    consent: bool


class TestDrive(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(..., regex=PHONE_REGEX)
    preferred_datetime: str
    vehicle: Optional[str] = None
    notes: Optional[str] = None


class Referral(BaseModel):
    your_name: str
    your_phone: str = Field(..., regex=PHONE_REGEX)
    your_email: EmailStr
    friend_name: str
    friend_phone: str = Field(..., regex=PHONE_REGEX)
    friend_email: EmailStr
    interested_vehicle: Optional[str] = None


class ContactUs(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(..., regex=PHONE_REGEX)
    message: str


class Feedback(BaseModel):
    rating: int
    name: Optional[str] = None
    phone: Optional[str] = Field(None, regex=PHONE_REGEX)
    email: Optional[EmailStr] = None
    comments: Optional[str] = None

    @validator("rating")
    def rating_range(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v
