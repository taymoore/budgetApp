from pydantic import BaseModel
import datetime


class Entry(BaseModel):
    bank_code: str
    category: str
    sub_category: str
    amount: float
    date: datetime.date

    def __hash__(self) -> int:
        return hash(self.bank_code) + hash(self.date) + hash(self.amount)
