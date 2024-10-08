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
    
    PROJECT_NOT_FOUND = "Project not found"

    INSERT_INTO_VECTORDB_FAILED = "Inserting into vector db failed"
    INSERT_INTO_VECTORDB_SUCCESS = "Inserting into vector db success"

    VECTORDB_COLLECTION_INFO_RETRIEVED = "Vector db collection info retrieved"

    VECTORDB_SEARCH_ERROR = "Error While searching in VectorDB"
    VECTORDB_SEARCH_SUCCESS = "Search in VectorDB success"

    RAG_ANSWER_ERROR = "RAG ANSWER ERROR"
    RAG_ANSWER_SUCCESS = "RAG ANSWER SUCCESS"