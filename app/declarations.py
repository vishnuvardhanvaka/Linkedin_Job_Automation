from pydantic import BaseModel


class JobAutomate(BaseModel):
    email:str
    password:str

