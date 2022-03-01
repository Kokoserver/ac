from pydantic import  BaseModel, EmailStr, Field, PaymentCardNumber



class PaymentInput(BaseModel):
     cardno:PaymentCardNumber
     cvv:str = Field( ...,title="card cvv", description="Customer cvv", max_length=3, min_length=3)
     expirymonth:str = Field(...,title="card expire month", description="Customer card expire month")
     expiryyear:str = Field(...,title="card expire year", description="Customer card expire year")
     currency:str = Field(title="payment currency", description="currency the customer is paying with e.g NG for naira", default="NGN")
     pin:str = Field(...,title="card pin", description="Customer card pin", min_length=4, max_length=4)
     suggested_auth: str = Field(title="card authentication mode", description=" what mode is Customer card supported e.g PIN, Address", default="pin")

class ValidatedPaymentInput(BaseModel):
     otp:str
     flwRef:str
     txRef:str

