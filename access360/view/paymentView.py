from access360.api.model.customerCard.invoiceModel import UserCard
from access360.api.model.payment.paymentPydanticModel import PaymentInput, ValidatedPaymentInput
from  access360.api.model.userModel.accountMixin import AccountManager, UserAccount
from access360.api.model.userModel.accountModel import AcquiredCourse
from access360.api.model.payment.pyamentMixin import Access360Payment
from access360.api.model.cart.CartModel import Cart
from access360.api.model.cart.cartMixins import CartMixin
from fastapi import  APIRouter, Depends
from access360.settings import API_BASE_URI

router = APIRouter(prefix=API_BASE_URI, tags=["payment"])
@router.post("/payment")
async def VerifyCoursePayment(userPayment:PaymentInput, user:dict=Depends(AccountManager.authenticate_user)):
    if user:
        paymentData = {**userPayment.dict()}
        userCart = CartMixin.getUserCart(user["id"])
        if userCart:
           totalAmount = userCart["total_price"]
           paymentData.update({"amount":totalAmount, "email":user["email"], "username":user["username"]})
           payment = Access360Payment(**paymentData)
           payment_process = payment.makePay()
           if payment_process:
               if UserCard.objects(cardno=userPayment.cardno).first():
                   return payment_process
               save_user_card = UserCard(**{"userId":user["id"], "email":user["email"], "txRef": payment_process["validation_reference"]}, **userPayment.dict())
               if save_user_card.save(clean=True):
                   return payment_process
           return "error"
        return {"error":"cart is empty"}

@router.post("/validate/payment")
async def validate_payment(paymentDetail:ValidatedPaymentInput, user:dict =Depends(AccountManager.authenticate_user)):
    if user:
        user_cart_course = Cart.objects(userId=user["id"]).first()
        try:
            if user_cart_course:
                payment = Access360Payment.validate_Payment(otp=paymentDetail.otp, flwRef=paymentDetail.flwRef)
                if payment:
                    paymentVerification = Access360Payment.verify_payment(paymentDetail.txRef)
                    if paymentVerification["transactionComplete"]:
                        currentUser = UserAccount.get_singleUserByEmail(email=user["email"])
                        if currentUser and len(user_cart_course["course"]) > 0:
                            for course in user_cart_course["course"]:
                                currentUser["ownedCourse"].append(course) if course not in currentUser[
                                    "ownedCourse"] else ""
                            if currentUser.save():
                                update_user_card = UserCard.getUserCard(is_completed=False,
                                                                        txRef=paymentVerification["txRef"])
                                if update_user_card:
                                    update_user_card.update(token=paymentVerification["cardToken"])
                                user_cart_course.delete()
                                if user_cart_course["course"].clear():
                                    user_cart_course.save()
                            return paymentVerification
            return {"error":"cart is empty"}
        except Exception as e:
            return {"error": e}












