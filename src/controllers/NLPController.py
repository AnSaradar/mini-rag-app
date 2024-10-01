from .BaseController import BaseController
from models.db_schmes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json
class NLPController(BaseController) :
    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    
    def create_collection_name(self , project_id:str): #To Standarize the collection name for any VectorDB
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self , project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name = collection_name)
        
    def get_vector_db_collection_info(self , project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info =self.vectordb_client.get_collection_info(collection_name = collection_name)
        return json.loads(
            json.dumps(collection_info,default=lambda x: x.__dict__)
        )

    def index_into_vector_db(self , project:Project , chunks:List[DataChunk],
                             chunks_ids:List[int],do_reset:bool = False):
        
        collection_name = self.create_collection_name(project_id=project.project_id)

        # Manage Items , and Get data
        texts = [chunk.chunk_text for chunk in chunks]
        metadatas = [chunk.chunk_metadata for chunk in chunks]
        vectors = [
            self.embedding_client.embed_text(text = text, document_type = DocumentTypeEnum.DOCUMENT.value )
            for text in texts
        ]
        # create collection 
        _ = self.vectordb_client.create_collection(
            collection_name = collection_name,
            embedding_size = self.embedding_client.embedding_size,  # We can also get it from .env
            do_reset = do_reset,
        )

        # Insert To VectorDB
        _ = self.vectordb_client.insert_many(
            collection_name = collection_name,
            texts = texts,
            vectors = vectors,
            metadata = metadatas,
            record_ids = chunks_ids
        )

        return True
    
    
    def search_vector_db_collection(self, project : Project , text: str, limit: int=10):
        print("Entered")
        collection_name = self.create_collection_name(project_id=project.project_id)
    
        # Apply Embedding on the text
        vector = self.embedding_client.embed_text(text = text, document_type = DocumentTypeEnum.QUERY.value )

        if not vector or len(vector) == 0 :
            print("Error while embedding text")
            return False
        
        # Apply Semantic Search on VectorDB

        results = self.vectordb_client.search_by_vector(
            collection_name = collection_name,
            vector = vector,
            limit = limit
        )

        if not results:
            print("Error while searching for vectors")
            return False

        return results
    

    def answer_rag_question(self, project: Project, query: str, limit: int = 10):

        # Intilization
        answer , full_prompt , chat_history = None
    
        # Retrive related documents
        retrieved_documents = self.search_vector_db_collection(
            project=project, query=query, limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer , full_prompt , chat_history
        
        # Construct LLM prompt
        system_prompt =  self.template_parser.get(
            "rag","system_prompt",
        )
        
        document_prompts = "\n".join([
            self.template_parser.get(
                "rag","document_prompt",{
                    "doc_num": idx + 1,
                    "chunk_text": doc.text
                }
            )

            for idx , doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get(
            "rag","footer_prompt",
        )


        chat_history = [
            self.generation_client.construct_prompt(
                prompt = system_prompt,
                role = self.generation_client.enums.SYSTEM.value
            )
        ]

        full_prompt = "\n\n".join([document_prompts,footer_prompt])

        answer = self.generation_client.generate_text(
            prompt = full_prompt, chat_history = chat_history
        )

        return answer , full_prompt , chat_history