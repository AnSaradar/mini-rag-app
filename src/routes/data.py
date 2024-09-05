from fastapi import FastAPI, APIRouter, Depends, UploadFile, status ,Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings ,Settings
import os
import aiofiles
from controllers import DataController , ProjectController , ProcessController 
from models.enums import ResponseSignal
from .schemes import ProcessRequest
import logging
from models.ProjectModel import ProjectModel
from models.ChunckModel import DataChunckModel
from models.db_schmes import DataChunk

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1" , "data"],
)

logger = logging.getLogger('uvivorn.error')

#We use request to accsess the fields of the app route , in our case the db client & connection
@data_router.post("/upload/{project_id}")
async def upload_data(request : Request ,project_id : str ,file : UploadFile,
                       app_settings : Settings = Depends(get_settings)):
        

        project_model = await ProjectModel.create_instance(
              db_client=request.app.db_client
        )

        project = await project_model.get_project_or_create_one(project_id=project_id)


        is_valid , result_signal = DataController().validate_uploaded_file(file)

        if not is_valid:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                     content={
                                             "signal" : result_signal
                                     })
        
        file_path , file_id = DataController().generate_unique_filepath(orig_file_name = file.filename , project_id = project_id)
        logger.info(f"File Path : {file_path} "+"\n" +file_id)
        try:
            async with aiofiles.open(file_path, "wb") as f:
                while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                    await f.write(chunk)
        
        except Exception as e:
            logger.error(f"Error While uploading file : {e}")
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                        "signal" : ResponseSignal.FILE_UPLOAD_FAILED.value,
                                        
                                })
        

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={
                                    "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                                    "file_id": file_id,
                                    "project_id":str(project._id)
                            })


@data_router.post("/process/{project_id}")
async def process_data(request : Request ,project_id : str ,process_request : ProcessRequest):
        
        file_id = process_request.file_id
        chunk_size = process_request.chunck_size
        overlap_size = process_request.overlap_size
        do_reset = process_request.do_reset

        

        project_model = await ProjectModel.create_instance(
              db_client=request.app.db_client
        )

        project = await project_model.get_project_or_create_one(project_id=project_id)

              

        process_controller = ProcessController(project_id = project_id)
        file_content = process_controller.get_file_content(file_id = file_id)
        file_chunks = process_controller.process_file_content(file_content = file_content ,
                 file_id = file_id , chunck_size = chunk_size , overlap_size = overlap_size)
        
        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                        "signal" : ResponseSignal.PROCESSING_FAILED.value
                                })
        
        file_chunks_records = [
              
              DataChunk(chunk_text = chunck.page_content , chunk_metadata = chunck.metadata ,
                         chunk_order =i+1 , chunk_project_id = project.id)
              
                
              for i,chunck in enumerate(file_chunks)
        ]

        
        chunck_model = await DataChunckModel.create_instance(
                db_client=request.app.db_client
        )

        if do_reset == 1:
              _ = await chunck_model.delete_chuncks_by_project_id(project_id = project.id)

        
        no_records = await chunck_model.insert_many_chuncks(file_chunks_records)

        return JSONResponse(
              status_code=status.HTTP_200_OK,   
              content={
                    "signal":ResponseSignal.PROCESSING_SUCCESS.value,
                    "inserted_chuncks":no_records
              }
        )