from fastapi import status, HTTPException
from access360.api.model.course.courseModel import Course
from access360.api.model.cart.CartModel import Cart
from access360.view.generalMixin import Access360FullMixin
from access360.api.model.userModel.accountModel import UserAccount
class CartMixin(object):
    @staticmethod
    def getUserCart(userId):
        userCartList = Cart.objects(userId=userId).first()
        if userCartList:
            return userCartList.to_json()
        return None

    @staticmethod
    def addToCart(data:dict):
        newCart = Cart.objects(userId=data.get("userId")).first()
        course = Course.objects(id=data.get("courseId")).first()
        check_user_course = UserAccount.objects(id=data.get("userId"), ownedCourse__in=[course]).first()
        if check_user_course:
            errorResponse = {"message": "User already has this course"}
            raise HTTPException(detail=errorResponse, status_code=status.HTTP_400_BAD_REQUEST)
        if newCart:
            if course:
                if course not in newCart.course:
                    addCart = newCart.update(add_to_set__course=course)
                    if addCart:
                       return newCart.to_json()
                    errorResponse = {"message": "Error adding new course to cart"}
                    raise HTTPException(detail=errorResponse, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
                errorResponse = {"message": "course already in cart"}
                raise HTTPException(detail=errorResponse, status_code=status.HTTP_302_FOUND)
            errorResponse = {"message":"Course does not exist"}
            raise HTTPException(detail=errorResponse, status_code=status.HTTP_400_BAD_REQUEST)
        if course:
            cart = Cart(userId=data.get("userId"))
            cart.course.append(course)
            cart.save(clean=True)
            if cart:
                return cart.to_json()
            return False
        errorResponse = {"message": "Course does not exist"}
        return Access360FullMixin.Response(userMessage=errorResponse,
                                           success=False,
                                           status_code=status.HTTP_400_BAD_REQUEST)




    @staticmethod
    def removeCourseFromCart(data:dict):
        userCart = Cart.objects(userId=data.get("userId")).first()
        course = Course.objects(id=data.get("courseId")).first()
        if not userCart:
            errorResponse = {"message": "User does not have any course in cart"}
            raise HTTPException(detail=errorResponse, status_code=status.HTTP_400_BAD_REQUEST)
        if not course:
            errorResponse = {"message": "course does not exist"}
            raise HTTPException(detail=errorResponse, status_code=status.HTTP_404_NOT_FOUND)
        try:
            if course  in userCart.course:
                if userCart.update(pull__course=course):
                   return True
            return False
        except Exception as e:
            raise HTTPException(detail=f"error removing cart {e}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)








