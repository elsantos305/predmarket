from pydantic import BaseModel
import datetime


class Element(BaseModel):
    price: float
    size: float


class Book(BaseModel):
    asks: list[Element]
    bids: list[Element]
    timestamp: datetime.datetime
