from enum import Enum

class ResponseSignal(Enum):

    FILE_TYPE_NOT_SUPPORTED  = "File type not supported"
    FILE_MAX_SIZE_EXCEEDED  = "File max size exceeded"

    FILE_UPLOAD_SUCCESS = "File upload success"
    FILE_UPLOAD_FAILED = "File upload failed"

    FILE_VALIDATE_SUCCESS = "File validate success"
    FILE_VALIDATE_FAILED = "File validate failed"

    PROCESSING_FAILED = "Processing failed"
    PROCESSING_SUCCESS = "Processing success"
    
    NO_FILES_ERROR = "No files were found"
    FILE_ID_ERROR = "no file was found with this id"
    