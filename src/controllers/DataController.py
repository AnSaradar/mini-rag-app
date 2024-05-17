from .BaseController import BaseController
from fastapi import UploadFile # type: ignore
from models.enums import ResponseSignal

class DataController(BaseController):

    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024
    

    def validate_uploaded_file(self, file : UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False , ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False , ResponseSignal.FILE_MAX_SIZE_EXCEEDED.value
        

        return True , ResponseSignal.FILE_VALIDATE_SUCCESS.value
