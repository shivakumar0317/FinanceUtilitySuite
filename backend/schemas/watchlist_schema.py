from pydantic import BaseModel, Field, field_validator
class WatchlistCreate(BaseModel):
    symbol: str = Field(min_length=1,max_length=40)
    exchange: str = Field(default="NSE",min_length=1,max_length=20)
    @field_validator("symbol","exchange")
    @classmethod
    def clean(cls,value:str)->str:
        return value.strip().upper()
