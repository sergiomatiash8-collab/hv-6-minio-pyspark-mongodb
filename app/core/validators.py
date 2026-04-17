"""
Data validation schemas using Pydantic. 
Validates data at Bronze, Silver, and Gold layers.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class AmazonReviewBronze(BaseModel):
    """Schema for Bronze layer (raw data)."""
    review_id: str
    product_id: str
    star_rating: int = Field(ge=1, le=5)
    review_date: str
    verified_purchase: Optional[str] = None
    customer_id: Optional[str] = None

    @field_validator('star_rating')
    @classmethod
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('star_rating must be between 1 and 5')
        return v


class AmazonReviewSilver(BaseModel):
    """Schema for Silver layer (cleaned data)."""
    review_id: str = Field(min_length=1)
    product_id: str = Field(min_length=1)
    star_rating: int = Field(ge=1, le=5)
    review_date: datetime
    verified_purchase: bool
    customer_id: str

    @field_validator('review_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace(' ', 'T'))
            except ValueError:
                # Додаткова обробка форматів, якщо ISO не спрацював
                return datetime.strptime(v, '%Y-%m-%d')
        return v


class AmazonReviewGold(BaseModel):
    """Schema for Gold layer (aggregated data)."""
    product_id: str
    avg_rating: float = Field(ge=1.0, le=5.0)
    total_reviews: int = Field(ge=0)
    verified_reviews: int = Field(ge=0)
    last_review_date: datetime