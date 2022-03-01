from pydantic import BaseModel

class AddCart(BaseModel):
    courseId:str


class RemoveCart(BaseModel):
    courseId: str


class GetCart(BaseModel):
    userId: str
