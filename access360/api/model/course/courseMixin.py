import os
from mongoengine.errors import NotUniqueError
from access360.view.generalMixin import Access360FullMixin
from fastapi import  status
from google.cloud import storage
from access360.settings import BASE_DIR
from access360.api.model.course.courseModel import Course
from access360.settings import EMAIL
import shutil




class CourseMixin(object):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f"{BASE_DIR}/credential.json"
    @staticmethod
    async def saveCourse(title:str, details:str, files, bucket_name:str, cover_image):
        if Course.objects(title=title).first():
            # ErrorResponseData = {"message": ""}
            # Access360FullMixin.mailUser(emailTitle="Error uploading course",
            #                             emailMessage="Course with this name already exist, "
            #                                          "you can add v2 or make it different", userEmail=EMAIL)
            return Access360FullMixin.Response(userMessage={"message":"Course with this name already exist, "
                                                                      "you can add v2 or make it different"},
                                               success=False,
                                               status_code=status.HTTP_400_BAD_REQUEST)
        course_file, cover_im = await CourseMixin.upload(files, bucket_name, cover_image)
        newCourse = Course(title=title, details=details, courseFile=course_file, cover_image=cover_im, storage_name=bucket_name,rating=[1])
        try:
            newestCourse = newCourse.save()
            if newestCourse:
                SuccessMessage = {"message": newestCourse.to_json()}
                Access360FullMixin.mailUser(emailTitle="Course uploaded success message",
                                            emailMessage=f"Course with title {title} \nuploaded successfully",
                                            userEmail=EMAIL)
                return Access360FullMixin.Response(userMessage=SuccessMessage, success=True,
                                                   status_code=status.HTTP_201_CREATED)


            return
        except NotUniqueError:
            # ErrorResponseData = {"message": "Course with the name already exist, you can add v2 or make it different"}
            # return Access360FullMixin.Response(userMessage=ErrorResponseData, success=False,
            #                                    status_code=status.HTTP_400_BAD_REQUEST)
            Access360FullMixin.mailUser(emailTitle="Error uploading course",
                                        emailMessage="Course with the name already exist, "
                                                     "you can add v2 or make it different", userEmail=EMAIL)


    @staticmethod
    async def upload(files, bucket_name, cover_image):
        returnCourseFile = list()
        cover_im: list = list()
        cloud_storage = storage.Client()
        try:
            bucket = cloud_storage.get_bucket(bucket_name)
            for file in files:
                blob = bucket.blob(f"{file.filename}")
                blob.upload_from_string(
                    await file.read(),
                    content_type=file.content_type)
                blob.make_public()
                returnCourseFile.append({"filename": file.filename, "url": blob.public_url})
        except:
            bucket = cloud_storage.create_bucket(bucket_name)
            bucket.storage_class = "STANDARD"
            bucket = cloud_storage.get_bucket(bucket_name)
            cover_img = bucket.blob(f"{cover_image.filename}")
            cover_img.upload_from_string(
                await cover_image.read(),
                content_type=cover_image.content_type)
            cover_img.make_public()
            for file in files:
                blob = bucket.blob(f"{file.filename}")
                blob.upload_from_string(
                    await file.read(),
                    content_type=file.content_type)
                blob.make_public()
                returnCourseFile.append({"filename": file.filename, "url": blob.public_url})

        return returnCourseFile, cover_im

    @staticmethod
    def getStorageList():
        storage_client = storage.Client()
        buckets = storage_client.list_buckets()
        return Access360FullMixin.getDataList(buckets)

    @staticmethod
    def deleteStorage(bucket_name:str):
            storage_client = storage.Client()
            try:
                bucket = storage_client.get_bucket(bucket_name)
                bucket.delete()
            except:
                return False


    @staticmethod
    def listCourseFile(bucket_name):
        storage_client = storage.Client()
        course = storage_client.list_blobs(bucket_name)
        storages = Access360FullMixin.getDataList(course)
        if storages:
            return storages
        return False

    @staticmethod
    def renameCourse(bucket_name, courseName, newCourseName):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(courseName)
        newCourse = bucket.rename_blob(blob, newCourseName)
        if newCourse:
            return True
        return False

    @staticmethod
    def deleteCourse(bucket_name, courseName):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(courseName)
        if blob.delete():
            return True
        return False
