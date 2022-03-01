from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
import smtplib
from google.cloud import storage
from email.message import EmailMessage
from access360.settings import EMAIL,PASSWORD
import random
import string

# message = EmailMessage()

class Access360FullMixin:
    @staticmethod
    def  Response(userMessage:dict, success:bool, status_code)->dict:
        if success:
            return JSONResponse(content={"status":"success", "message":userMessage}, status_code=status_code)
        return JSONResponse(content={"status": "error", "message": userMessage}, status_code=status_code)

    @staticmethod
    def getData(data:dict) -> dict:
        try:
            if data:
                for data in data:
                    return data
        except Exception.__base__:
            ErrorResponseData = {"error": "Invalid details to iterate"}
            return Access360FullMixin.Response(userMessage=ErrorResponseData, success=False,
                                               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def getDataList(data: list) -> list:
        try:
            if data:
                return [data.to_json(indent=4) for  data in data]
        except Exception.__base__:
            ErrorResponseData = {"error": "Invalid details to iterate"}
            return Access360FullMixin.Response(userMessage=ErrorResponseData, success=False,
                                               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @staticmethod
    def getRandomString(stringLength:int):
        try:
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(stringLength))
            return result_str
        except Exception.__base__:
            ErrorResponseData = {"error": "Invalid details to iterate"}
            return Access360FullMixin.Response(userMessage=ErrorResponseData, success=False,
                                               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def upload_blob(bucket_name:str, file:dict, filename:str):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        url = blob.upload_from_filename(file)
        return  url

    @staticmethod
    def download_blob(bucket_name, source_blob_name, destination_file_name):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)


    @staticmethod
    def mailUser(userEmail:str, emailMessage:str, emailTitle):
        ######################### setting mail server #######################
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as access360Mail:
            try:
                ######################### Authenticate account #######################
                access360Mail.login(EMAIL, PASSWORD)
                ######################### setting up mail body #######################
                # message["subject"] = emailTitle
                # message['from'] = EMAIL
                # message['to'] = userEmail
                # message.set_content(emailMessage)
                # access360Mail.send_message(message)
                message = f"subject:{emailTitle}\n\n body:{emailMessage}"
                access360Mail.sendmail(EMAIL, userEmail, message)
                ######################### return success message #######################
                return "message sent successfully"
                
            except Exception.__base__:
                ######################### return error if mail failed to send #######################
                return "Error sending message"
            





