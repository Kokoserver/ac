from fastapi import APIRouter, Form, UploadFile, File, status, HTTPException, Depends
from access360.api.model.userModel.accountMixin import AccountManager
from fastapi.background import BackgroundTasks
from access360.api.model.course.courseMixin import CourseMixin
from access360.view.generalMixin import Access360FullMixin
from access360.settings import API_BASE_URI
from access360.api.model.course.courseModel import Course
router = APIRouter(tags=["Course"], prefix=API_BASE_URI)



@router.post("/course/upload")
async def upload(background:BackgroundTasks, title:str = Form(...), storage_name:str = Form(...),
                 cover_image:UploadFile = Form(...),
                 details:str = Form(...), files:list[UploadFile] = File(...),
                 user:dict=Depends(AccountManager.authenticate_user)):
    if user["admin"]:
        background.add_task(CourseMixin.saveCourse, title=title, details=details, files=files, bucket_name=storage_name, cover_image=cover_image)
        return HTTPException(detail={"message": "Video is processing in the background",
                                     "details": "if any error occur it will be mailed to you to avoid website overloading"},
                             status_code=status.HTTP_202_ACCEPTED,
                             headers=""
                             )
    return Access360FullMixin.Response(userMessage={"message":"Error validating admin"},
                                       status_code=status.HTTP_401_UNAUTHORIZED, success=False)


@router.get("/course/{courseId}")
async def getSingleCourse(courseId:str):
     course = Course.objects(id=courseId).first()
     if course:
         successResponse = {
             "course":course.to_json()
         }
         return Access360FullMixin.Response(userMessage=successResponse, status_code=status.HTTP_200_OK, success=True)
     ErrorResponse = {
         "course": f"course with id {courseId} does ot exist"
     }
     return  Access360FullMixin.Response(userMessage=ErrorResponse, success=True, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/course")
async def getAllCourse():
     allCourse = Course.objects()
     courseList = Access360FullMixin.getDataList(allCourse)
     return courseList

@router.delete("/course/{courseId}")
def deleteCourse(courseId:str, background:BackgroundTasks, user:dict=Depends(AccountManager.authenticate_user)):
    course = Course.objects(id=courseId).first()
    if user["admin"]:
        if course:
            background.add_task(CourseMixin.deleteStorage, bucket_name=course.storage_name)
            course.delete()
            successResponse = {
                "message": "Course deleted successfully"
            }
            return Access360FullMixin.Response(userMessage=successResponse, status_code=status.HTTP_200_OK,
                                               success=True)
        ErrorResponse = {
            "message": "Course does not exist"
        }
        return Access360FullMixin.Response(userMessage=ErrorResponse, status_code=status.HTTP_400_BAD_REQUEST,
                                           success=False)
    return Access360FullMixin.Response(userMessage={"message":"Error validating admin"},
                                       status_code=status.HTTP_401_UNAUTHORIZED, success=False)





















