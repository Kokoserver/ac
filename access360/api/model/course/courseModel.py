from datetime import datetime
from mongoengine import *
from statistics import mean





class Course(Document):
    cover_image = URLField(required=True)
    title = StringField(required=True, max_length=500, min_length=5, unique=True)
    details = StringField(required=True, max_length=3000, min_length=5)
    create  = DateTimeField(default=datetime.now)
    price = DecimalField(required=True, default=3000)
    rating  = ListField(max_value=5, min_value=1, default=0.5)
    storage_name = StringField(required=True)
    courseFile = ListField(DictField(), required=True)
    meta = {"db_alias": "core", "collection": "course"}

    def to_json(self, *args, **kwargs):
        return {
            "id":str(self.id),
            "cover_pic":self.cover_image,
            "title":self.title,
            "details":self.details,
            "price":self.price,
            "courseFile":self.courseFile,
            "rating": mean(self.rating),
            "created_at":str(self.create)
        }


