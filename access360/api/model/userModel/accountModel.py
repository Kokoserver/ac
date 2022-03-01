from uuid import uuid4
from datetime import datetime
from mongoengine import *
from access360.api.model.course.courseModel import Course

PAYMENT_STATUS = ("payed", "pending", "failed")

class AcquiredCourse(EmbeddedDocument):
    course = ReferenceField(Course, dbref=True)
    paymentStatus = StringField(choices=PAYMENT_STATUS)
    def to_json(self, *args, **kwargs):
        return {
            "courseId":self.course.id,
            "courseFile":self.course.courseFile
        }


class UserAccount(Document):
    username = StringField(required=True, min_length=3)
    email = EmailField(required=True,  unique=True)
    gender = StringField(choices=("male", "female"), required=True)
    password = StringField(required=True)
    active   = BooleanField(default=False)
    admin    = BooleanField(default=False)
    passwordCode = StringField(default="no passcode")
    created_at = DateField(default=datetime.utcnow)
    ownedCourse = ListField(ReferenceField(Course, dbref=True))
    meta  = {"db_alias":"core", "collection":"user"}

    @queryset_manager
    def get_singleUserByEmail(doc_cls, queryset, email):
        return queryset.filter(email=email).first()

    @queryset_manager
    def get_singleUserById(doc_cls, queryset, userId):
        return queryset.filter(id=userId).first()

    @queryset_manager
    def get_user_courseId(doc_cls, queryset, userId):
        user = queryset.filter(id=userId).first()
        return


    def to_json(self, *args, **kwargs):
        return {
            "id":str(self.pk),
            "username":self.username,
            "email":self.email,
            "gender": self.gender,
            "admin":self.admin,
            "active":self.active,
            "courses":[course.to_json() for course in self.ownedCourse],
            "created_at":str(self.created_at)
        }











