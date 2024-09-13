from .BaseDataModel import BaseDataModel
from .db_schmes import Project
from models.enums.DataBaseEnums import DataBaseEnum
class ProjectModel(BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        # Get the collection from the databases
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
    
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name = index["name"],
                    unique = index["unique"]
                )

    async def create_project(self,project:Project):
        # insert_one(Dict)
        # motor is async

        result = await self.collection.insert_one(project.dict(by_alias=True , exclude_unset=True))
        # result.inserted_id: id returned from the database 
        project.id = result.inserted_id

        return project


    async def get_project_or_create_one(self,project_id:str): 
        # find_one : returns dict of project 
        record  = await self.collection.find_one(
            {
                "project_id":project_id
            }
        ) 
        
        if record is None: # not found
            # Create a new project
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)
            return project
        
        return Project(**record) # **record : dict(record) to ProjectModel


    
    async def get_all_projects(self , page:int = 1 , page_size:int = 10):
        
        #Count the number of documents
        total_documents =  await self.collection.find({})

        #Calculate the number of pages 
        total_pages = total_documents // page_size
        if total_documents % page_size > 0 :
            total_pages += 1
        
        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = []

        async for document in cursor:
            projects.append(Project(**document))


        return projects , total_pages


