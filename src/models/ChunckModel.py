from .BaseDataModel import BaseDataModel
from .db_schmes import DataChunk
from .enums.DataBaseEnums import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne


class DataChunckModel(BaseDataModel):

    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNCK_NAME.value]

    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
      
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNCK_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNCK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name = index["name"],
                    unique=index["unique"]
                )

    async def create_chunck(self , chunck: DataChunk):
        result = await self.collection.insert_one(chunck.dict(by_alias=True , exclude_unset=True))
        chunck._id = result.inserted_id
        return chunck
    
    async def get_chunck(self , chunck_id:str):
        result = await self.collection.find_one({"_id":ObjectId(chunck_id)})

        if result is None:
            return None
        
        return DataChunk(**result) #from dict to model
    

    
    async def insert_many_chuncks(self , chuncks:list ,batch_size : int=100):

        for i in range(0,len(chuncks),batch_size):
            batch = chuncks[i:i+batch_size]

            operation = [
                InsertOne(chunck.dict(by_alias=True , exclude_unset=True))
                for chunck in batch
            ]

            await self.collection.bulk_write(operation)

        return len(chuncks)
    

    async def delete_chuncks_by_project_id(self , project_id:ObjectId):
        result = await self.collection.delete_many({"chunk_project_id":project_id})

        return result.deleted_count
    

    
