from fastapi import APIRouter, Depends, status
from access360.api.model.userModel.accountMixin import AccountManager
from access360.view.generalMixin import Access360FullMixin
from access360.settings import API_BASE_URI
from access360.api.model.cart.cartMixins import CartMixin
from access360.api.model.cart.cartPydanticModel import AddCart, RemoveCart

router = APIRouter(prefix=API_BASE_URI, tags=["cart"])

@router.get("/cart")
def getUserCart(user:dict = Depends(AccountManager.authenticate_user)):
    if user:
        userId = user.get("id", None)
        if userId:
            userCart = CartMixin.getUserCart(userId=userId)
            if userCart:
                successResponse = {"data":userCart }
                return Access360FullMixin.Response(userMessage=successResponse,
                                                   status_code=status.HTTP_200_OK,
                                                   success=True)
            errorResponse = {"message":"Cart is empty"}
            return Access360FullMixin.Response(userMessage=errorResponse,
                                               success=False,
                                               status_code=status.HTTP_404_NOT_FOUND)
        errorResponse = {"message": "User is not Authenticated"}
        return Access360FullMixin.Response(userMessage=errorResponse,
                                           success=False,
                                           status_code=status.HTTP_401_UNAUTHORIZED)
    errorResponse = {"message": "User does not Authenticated"}
    return Access360FullMixin.Response(userMessage=errorResponse,
                                       success=False,
                                       status_code=status.HTTP_401_UNAUTHORIZED)

@router.post("/cart")
def addNewCart(cart:AddCart, user:dict = Depends(AccountManager.authenticate_user)):
    if cart:
        data = {"userId":user.get("id"), "courseId":cart.courseId}
        newCart = CartMixin.addToCart(data=data)
        if newCart:
            successResponse = {"data":newCart, "message":"course added to cart"}
            return Access360FullMixin.Response(userMessage=successResponse,
                                        success=True,
                                        status_code=status.HTTP_200_OK)
        errorResponse = {"message": "error adding course to cart"}
        return Access360FullMixin.Response(userMessage=errorResponse,
                                    success=False,
                                    status_code=status.HTTP_400_BAD_REQUEST)
    successResponse = {"message": "can't add empty course to cart"}
    return Access360FullMixin.Response(userMessage=successResponse,
                                success=True,
                                status_code=status.HTTP_200_OK)


@router.delete("/cart")
def removeProductFromCart(cart:RemoveCart, user:dict = Depends(AccountManager.authenticate_user)):
    data = {"userId":user.get("id"),"courseId":cart.courseId}
    removeCourse = CartMixin.removeCourseFromCart(data=data)
    if removeCourse:
        successResponse = {"message":"Course removed from cart", "courseId":cart.courseId}
        return Access360FullMixin.Response(userMessage=successResponse,
                                           success=True,
                                           status_code=status.HTTP_200_OK)
    errorResponse = {"message": "Error removing course from cart, course not in cart"}
    return Access360FullMixin.Response(userMessage=errorResponse,
                                success=False,
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)















