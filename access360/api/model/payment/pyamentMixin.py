from access360.api.model.payment.paymentModel import Invoice
from fastapi import HTTPException, status
from os import urandom
from access360.settings import (PAYMENT_PUBLIC_KEY, PAYMENT_SECRET_KEY, WEBSITE_URL, API_BASE_URI)
from rave_python import Rave, Misc
class Access360Payment(object):
    rave = Rave(publicKey=PAYMENT_PUBLIC_KEY, secretKey=PAYMENT_SECRET_KEY)
    """this is the getKey function that generates an encryption Key for you by passing your Secret Key as a parameter."""
    def __init__(self, cardno:str, cvv:str, expirymonth:str,expiryyear:str,
                 currency:str,amount:str, email:str, pin:str, suggested_auth:str, username:str
                 ):
        self.email = email
        self.cardno = cardno
        self.cvv = cvv
        self.expirymonth = expirymonth
        self.expiryyear = expiryyear
        self.currency  = currency
        self.suggested_auth = suggested_auth
        self.pin = pin
        self.amount = amount
        self.paymentRef_str = urandom(8).hex()
        self.username = username

    def makePay(self):
        payload = {
            "cardno": self.cardno,
            "cvv": self.cvv,
            "expirymonth": self.expirymonth,
            "expiryyear": self.expiryyear,
            "amount": self.amount,
            "email": self.email,
            "username":self.username,
            "suggested_auth":self.suggested_auth
        }
        try:
            res = Access360Payment.rave.Card.charge(payload)
            if res["suggestedAuth"]:
                arg = Misc.getTypeOfArgsRequired(res["suggestedAuth"])
                if arg == "pin":
                    Misc.updatePayload(res["suggestedAuth"], payload, pin=self.pin)
                res = Access360Payment.rave.Card.charge(payload)
                return {"validated":"successfully",
                        "error":res["error"], "validation":"otp required" if  res["validationRequired"] else "address",
                        "validation_token":res["flwRef"],
                        "validation_reference":res["txRef"],
                        "details":{
                            "message":"require validation otp",
                            "validation url":f"{WEBSITE_URL}/{API_BASE_URI}/validate/payment",
                            "method":"post",
                            "body":{"txRef":res["txRef"], "flwRef":res["flwRef"]}}
                        }
        except Exception as e:
            return {"error":e}

    @staticmethod
    def validate_Payment(flwRef:str, otp:str):
        try:
           validate = Access360Payment.rave.Card.validate(flwRef, otp)
           if not validate["transactionComplete"]:
               return False
           return True
        except Exception as e:
            return  {"error":e}

    @staticmethod
    def verify_payment(txRef:str):
        try:
           res = Access360Payment.rave.Card.verify(txRef)
           if res:
               return res

        except Exception as e:
            return {"error":e}
