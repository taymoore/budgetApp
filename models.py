from pydantic import BaseModel
import datetime


class Entry(BaseModel):
    bank_code: str
    category: str
    sub_category: str
    amount: float
    date: datetime.date

    def __hash__(self) -> int:
        if self.amount == -461.95:
            print(self.bank_code)
            print(self.date)
            print(self.amount)
        return hash(self.bank_code) + hash(self.date) + hash(self.amount)
