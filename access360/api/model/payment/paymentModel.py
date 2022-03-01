from datetime import datetime
from mongoengine import *



class Invoice(Document):
    userId = ObjectIdField(required=True)
    courseList = ListField(ObjectIdField(), required=True)
    total_price = DecimalField(default=0, required=True)
    paymentStatus = StringField(choices=("success", "pending", "failed"), required=True)
    issued_date = DateField(default=datetime.utcnow)

    def to_json(self, *args, **kwargs):
        return {
            "userid":str(self.userId),
            "course_List":self.courseList,
            "course_count":len(self.courseList),
            "paymentStatus":self.paymentStatus,
            "issued_data":str(self.issued_date)
        }

    @queryset_manager
    def getUserInvoice(doc_cls, queryset, userId) -> dict:
        userInvoice = queryset.filter(userId=userId).all()
        if userInvoice:
            return userInvoice
        return False


class Payment(Document):
    pass




