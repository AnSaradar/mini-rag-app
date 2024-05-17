from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile # type: ignore
from models.enums import ResponseSignal
import re
import os
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
    


    def generate_unique_filename(self , original_filename : str ,project_id : str):
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id = project_id)
        cleaned_filename = self.get_clean_filename(original_filename = original_filename)
        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_filename 
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_filename 
            )
        
        return new_file_path

    def get_clean_filename(self , original_filename : str):
        # remove any special characters except underscore and .
        original_filename = original_filename.strip()
        return re.sub(r'[^a-zA-Z0-9_.]', '_', original_filename)
