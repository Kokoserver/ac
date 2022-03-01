from datetime import datetime
from mongoengine import *
from access360.api.model.course.courseModel import Course

class Cart(Document):
    userId = ObjectIdField(required=True)
    course = ListField(ReferenceField(document_type=Course, dbref=True))
    created_at = DateField(default=datetime.utcnow)
    meta = {"db_alias":"core", "collection":"carts"}
    def to_json(self, *args, **kwargs):
        return {
            "userId":str(self.userId),
            "course":[{"id":str(course.id), "price":course.price}   for course in self.course],
            "total_price":self.getTotalCost(),
            "created_at":str(self.created_at)
        }

    def getTotalCost(self):
        total_price = 0
        for course in self.course:
            price = course.to_json()["price"]
            total_price =  total_price + price
        return  total_price








