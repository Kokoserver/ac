from fastapi import  APIRouter, status, Depends
from fastapi.background import BackgroundTasks
from fastapi.responses import Response
from mongoengine import errors
from access360.api.model.userModel import accountModel
from access360.api.model.cart.cartMixins import CartMixin
from access360.api.model.userModel.accountMixin import AccountManager
from access360.view.generalMixin import Access360FullMixin
from access360.api.model.userModel.accountPydanticModel import (UserRegisterationInput, UserLoginInput,
                                                              UserPasswordReset, GetPasswordResetLink)
from access360.settings import WEBSITE_URL, WEBSITE_NAME, API_BASE_URI

router = APIRouter(prefix=f"{API_BASE_URI}", tags=["User Account"])

@router.post("/register")
def registerUserAccount(user:UserRegisterationInput, background:BackgroundTasks):
    if user.password.strip() == user.confirmPassword.strip():
        try:
            password = AccountManager.hash_password(password=user.password)
            newUserDetails = {
                "username": user.username,
                "email": user.email,
                "gender": user.gender,
                "password": password
            }
            newUser = accountModel.UserAccount(**newUserDetails).save(clean=True)
            if newUser:
                mailData = {
                    "title":"Account verification",
                    "message":f" Welcome to {WEBSITE_NAME}, {newUser.username}\n "
                              f"Your account was created successfully please "
                              f"verify your email to continue\n {WEBSITE_URL}{API_BASE_URI}/user/{newUser.id}"
                }
                
                background.add_task(Access360FullMixin.mailUser, userEmail=newUser.email,
                                             emailTitle=mailData.get("title"),
                                             emailMessage=mailData.get("message"))

                SuccessResponseData = {
                    "user": newUser.to_json(indent=4),
                    "message": "Account was created successfully",
                    "confirm email": "A mail was sent to your to confirm your email address"
                    }

                return Access360FullMixin.Response(userMessage=SuccessResponseData, success=True,
                                                   status_code=status.HTTP_201_CREATED)
            ErrorResponseData = {"message": "Error creating account, check your detail and try again"}
            return Access360FullMixin.Response(userMessage=ErrorResponseData, success=False,
                                               status_code=status.HTTP_400_BAD_REQUEST)
        except errors.ValidationError:
            ErrorResponseData = {"message": "Error creating account, check your detail and try again"}
            return Access360FullMixin.Response(userMessage=ErrorResponseData, success=False,
                                               status_code=status.HTTP_400_BAD_REQUEST)

        except errors.NotUniqueError:
            ErrorResponseData = {"message": "Account already exist, try again or do forget password"}
            return Access360FullMixin.Response(userMessage=ErrorResponseData, success=False,
                                               status_code=status.HTTP_400_BAD_REQUEST)

    ErrorResponseData = {"message":"Password do not match, try again"}
    return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                       success=False,
                                       status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/user/{userId}")
def confirmEmail(userId:str):

    user = accountModel.UserAccount.get_singleUserById(userId=userId)
    if user:
        user.update(active=True)
        SuccessResponseData = {
            "user": user.to_json(indent=4),
            "message": "Account verified successfully",
            "extra":{
                "login":"please login to continue",
                "method":"post",
                "body":{"email":"string", "password":"string"}
            }
        }
        return Access360FullMixin.Response(userMessage=SuccessResponseData,
                                           status_code=status.HTTP_200_OK, success=True)
    ErrorResponseData = {"message": "Account does not exist"}
    return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                       status_code=status.HTTP_401_UNAUTHORIZED,
                                       success=False)
@router.post("/passwordResetting")
def getPasswordLink(userOldData:GetPasswordResetLink, background:BackgroundTasks):
    user = accountModel.UserAccount.get_singleUserByEmail(email=userOldData.email)
    if user:
        passcodeString = Access360FullMixin.getRandomString(stringLength=5)
        if passcodeString:
            user.update(passwordCode=passcodeString)
            mailData = {
                "title": "Password reset",
                "message": f"password reset pass code\n CODE: {passcodeString.upper()}"
            }
            background.add_task(Access360FullMixin.mailUser, userEmail=user.email,
                                emailTitle=mailData.get("title"),
                                emailMessage=mailData.get("message"))
            ErrorResponseData = {"message": "Check your email for pass code"}
            return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                               status_code=status.HTTP_200_OK,
                                               success=False)
    ErrorResponseData = {"message": "Account does not exist"}
    return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                       status_code=status.HTTP_401_UNAUTHORIZED,
                                       success=False)




@router.put("/passwordReset/")
def passwordReset(userOldData:UserPasswordReset):
    user = accountModel.UserAccount.get_singleUserByEmail(email=userOldData.email)
    if user:
        if userOldData.passcode.strip().lower() == user.passwordCode:
            if userOldData.password.strip() == userOldData.confirmPassword.strip():
                newPassword = AccountManager.hash_password(password=userOldData.password)
                if newPassword:
                    user.update(password=newPassword, passwordCode=None)
                    SuccessResponseData = {
                        "user": user.to_json(indent=4),
                        "message": "password change successfully",
                        "extra": {
                            "login": "please login to continue",
                            "method": "post",
                            "body": {"email": "string", "password": "string"}
                        }
                    }
                    return Access360FullMixin.Response(userMessage=SuccessResponseData,
                                                       status_code=status.HTTP_200_OK, success=True)
                ErrorResponseData = {"message": "could not change password"}
                return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                                   status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                   success=False)
            ErrorResponseData = {"message": "password does not match "}
            return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                               status_code=status.HTTP_400_BAD_REQUEST,
                                               success=False)

        ErrorResponseData = {"message": "incorrect passcode"}
        return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                           status_code=status.HTTP_400_BAD_REQUEST,
                                           success=False)

    ErrorResponseData = {"message": "Account does not exist"}
    return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                       status_code=status.HTTP_401_UNAUTHORIZED,
                                       success=False)

@router.post("/login")
def loginUserAccount(userIn:UserLoginInput, response:Response):
    try:
        user = accountModel.UserAccount.get_singleUserByEmail(email=userIn.email)
        if user:
            if user.active:
                if AccountManager.check_password(userIn.password, user.password):
                    encode_jwt_access, encode_jwt_refresh = AccountManager.JwtEncoder(user=user.to_json())
                    if encode_jwt_access and encode_jwt_refresh:
                        response.set_cookie(key="refresh_token",
                                            value=encode_jwt_refresh,
                                            httponly=True,
                                            max_age=172800,
                                            expires=172800,
                                            domain=WEBSITE_URL,
                                            secure=True)
                        SuccessResponseData = {
                            "user": user.to_json(indent=4),
                            "message": "logged in successfully",
                            "access_token": encode_jwt_access,
                            "access_token_type": "Bearer",
                            "expires": 1800
                        }
                        return Access360FullMixin.Response(userMessage=SuccessResponseData,
                                                           status_code=status.HTTP_200_OK, success=True)
                ErrorResponseData = {"message": "Password does not match"}
                return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                                   status_code=status.HTTP_401_UNAUTHORIZED,
                                                   success=False)

            ErrorResponseData = {"message": "Email was sent to you, please verify your email"}
            return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                               status_code=status.HTTP_401_UNAUTHORIZED,
                                               success=False)

        ErrorResponseData = {"message": "Account does not exist"}
        return Access360FullMixin.Response(userMessage=ErrorResponseData,
                                           status_code=status.HTTP_401_UNAUTHORIZED,
                                           success=False)
    except errors.DoesNotExist:
        return Access360FullMixin.Response(userMessage={"message":"user does not exist"},
                                           status_code=status.HTTP_400_BAD_REQUEST, success=False)
    except Exception.__base__:
        return Access360FullMixin.Response(userMessage={"message":"error logging user in"},
                                           status_code=status.HTTP_401_UNAUTHORIZED, success=False)


@router.get("/me")
def getUserAccount(user:dict = Depends(AccountManager.authenticate_user)):
    data = {"user":user, "cart":CartMixin.getUserCart(userId=user["id"])}
    return data








