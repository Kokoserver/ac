from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import status, HTTPException, Depends
from access360.api.model.userModel.accountModel import UserAccount
from datetime import datetime, timedelta
from jose import jwt, JWTError
from access360.settings import (API_BASE_URI, SECRET_KEY, REFRESH_KEY,
                                ACCESS_TOKEN_EXPIRE_TIME, REFRESH_TOKEN_EXPIRE_TIME)
Oauth_schema = OAuth2PasswordBearer(tokenUrl=f"{API_BASE_URI}/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AccountManager(object):
    @staticmethod
    def hash_password(password:bytes):
        convertPassword = pwd_context.hash(secret=password)
        if convertPassword:
            return  convertPassword
        errorResponseData = {
            "status": "error", "message": "Error Creating account please check your details and try again"
        }
        raise HTTPException(detail=errorResponseData, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def check_password(plainPassword, hashedPassword):
        checkPassword = pwd_context.verify(plainPassword, hashedPassword)
        if checkPassword:
            return True
        return False

    @staticmethod
    def get_singleUserDetails(data):
        if data:
            for user in data:
                return user
        return False
    @staticmethod
    def JwtEncoder(user:dict):
        access_token_time = datetime.utcnow() + timedelta(days=int(ACCESS_TOKEN_EXPIRE_TIME))
        refresh_token_time = datetime.utcnow() + timedelta(days=int(REFRESH_TOKEN_EXPIRE_TIME))
        data = {"id":user["id"], "username":user["username"]}
        data_access_token = {"user":data, "exp":access_token_time}
        data_refresh_token = {"user": data, "exp": refresh_token_time}
        try:
            encode_jwt_refresh = jwt.encode(claims=data_refresh_token, key=REFRESH_KEY)
            encode_jwt_access = jwt.encode(claims=data_access_token, key=SECRET_KEY)
            return  encode_jwt_access, encode_jwt_refresh
        except JWTError as e:
            raise  HTTPException(detail={"error":"Error jwt error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)




    @staticmethod
    def authenticate_user(token:str = Depends(Oauth_schema)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token=token, key=SECRET_KEY)
            user: dict = payload.get("user")
            if user is None:
                raise credentials_exception
            currentUser = UserAccount.get_singleUserById(user["id"])
            if currentUser is None:
                raise credentials_exception
            print(currentUser)
            return currentUser.to_json()
        except JWTError:
            raise credentials_exception








