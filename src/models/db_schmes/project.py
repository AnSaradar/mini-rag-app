from pydantic import BaseModel , Field , validator
from typing import Optional
from bson.objectid import ObjectId
class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") #default id , when inserting it will be None
    project_id : str = Field(... , min_length=1) 

    @validator("project_id")
    def validate_project_id(cls , value):
        if not value.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        return value
    
    #To make the pydantic libraries ignore any errors caused by unknown fields
    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def get_indexes(cls):

        return [{
            "key": [("project_id",1)], ## 1 for Ascending order & -1 for descending order
            "name": "project_id_index_1",
            "unique": True, ## Redundant values are not accepted
        }]