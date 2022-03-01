from mongoengine import  *
from datetime import datetime


class UserCard(Document):
    userId = ObjectIdField(required=True)
    cardno =StringField(required=True)
    email =StringField(required=True)
    cvv = StringField(required=True)
    expirymonth = StringField(required=True)
    expiryyear = StringField(required=True)
    pin = IntField(required=True)
    suggested_auth = StringField(required=True)
    currency = StringField(required=True, default="NGN")
    txRef = StringField(required=True)
    is_completed =  BooleanField(default=False)
    token = StringField()
    country = StringField(required=True, default="NG")
    created_at = DateField(default=datetime.utcnow)
    meta = {"db_alias": "core", "collection":"card"}

    @queryset_manager
    def getUserCard(doc_cls, queryset, is_completed:bool, txRef:str):
        return queryset.filter(is_completed=is_completed, txRef=txRef).first()

    def to_json(self, *args, **kwargs):
        return {
            "cardno":self.cardno
        }

