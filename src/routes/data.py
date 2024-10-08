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
from models.AssetModel import AssetModel
from models.db_schmes import DataChunk, Asset
from models.enums.AssetTypeEnum import AssetTypeEnum

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
        
        # store asssets into the mongodb

        asset_model = await AssetModel.create_instance(
              db_client=request.app.db_client
        )

        asset_resource = Asset(
              asset_project_id = project.id,
              asset_type = AssetTypeEnum.FILE.value,
              asset_name = file_id,
              asset_size = os.path.getsize(file_path),
        )
        asset_record = await asset_model.create_asset(asset=asset_resource)
        

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={
                                    "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                                    "file_id": str(asset_record.id),
                            })


@data_router.post("/process/{project_id}")
async def process_data(request : Request ,project_id : str ,process_request : ProcessRequest):
        
        #file_id = process_request.file_id


        chunk_size = process_request.chunck_size
        overlap_size = process_request.overlap_size
        do_reset = process_request.do_reset

        

        project_model = await ProjectModel.create_instance(
              db_client=request.app.db_client
        )

        project = await project_model.get_project_or_create_one(project_id=project_id)

        asset_model = await AssetModel.create_instance(
              db_client=request.app.db_client
             )

        project_files_ids = {}
        if process_request.file_id: # is not None
            asset_record = await asset_model.get_asset_record(asset_name=process_request.file_id,asset_project_id=project.id)
            if asset_record is None:
                 return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,   
                        content={
                              "signal":ResponseSignal.FILE_ID_ERROR.value,
                              
                        }
                  )
            
            project_files_ids = {
                 asset_record.id : asset_record.asset_name
            }
      
        else: # get all the files in the project

            project_files = await asset_model.get_all_project_assets(
                 asset_project_id=project.id,
                 asset_type=AssetTypeEnum.FILE.value) # project.id: uuid based on MONGODB
            
            # Get the asset_name which is the same of the file_id
            project_files_ids = {
                 record.id : record.asset_name
                 for record in project_files  
            }

            if len(project_files_ids) == 0:
                  return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,   
                        content={
                              "signal":ResponseSignal.NO_FILES_ERROR.value,
                              
                        }
                  )
                 

        process_controller = ProcessController(project_id = project_id)


        no_records = 0
        no_files = 0

        chunck_model = await DataChunckModel.create_instance(
                  db_client=request.app.db_client
            )

        if do_reset == 1:
            _ = await chunck_model.delete_chuncks_by_project_id(project_id = project.id)

        for asset_id,file_id in project_files_ids.items():

            file_content = process_controller.get_file_content(file_id = file_id)
            if file_content is None:
                 logger.error(f"Error While processing the file:{file_id}")
                 continue

            file_chunks = process_controller.process_file_content(file_content = file_content ,
                  file_id = file_id , chunck_size = chunk_size , overlap_size = overlap_size)
            
            if file_chunks is None or len(file_chunks) == 0:
                  return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                    content={
                                          "signal" : ResponseSignal.PROCESSING_FAILED.value
                                    })
            
            file_chunks_records = [
                  
                  DataChunk(chunk_text = chunck.page_content , chunk_metadata = chunck.metadata ,
                              chunk_order =i+1 , chunk_project_id = project.id , chunk_asset_id = asset_id)
                  
                  
                  for i,chunck in enumerate(file_chunks)
            ]

            
            no_records += await chunck_model.insert_many_chuncks(file_chunks_records)
            no_files += 1

        return JSONResponse(
              status_code=status.HTTP_200_OK,   
              content={
                    "signal":ResponseSignal.PROCESSING_SUCCESS.value,
                    "inserted_chuncks":no_records,
                    "processed_files":no_files
              }
        )