from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums , DocumentTypeEnum
import cohere
import logging

class CoHereProvider(LLMInterface):
    def __init__(self, api_key: str, api_url: str = None,
                       default_input_max_characters: int = 1000,
                       default_generator_max_output_tokens: int = 1000,
                       default_generation_temprature: float = 0.1,
                 ):
        
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generator_max_output_tokens = default_generator_max_output_tokens
        self.default_generation_temprature = default_generation_temprature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)


    def set_generation_model_id(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model_id(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def process_text(self, text : str):
        return text[:self.default_input_max_characters].strip()
    

    def generate_text(self, prompt: str,chat_history: list = [], max_output_tokens: int = None,
                       temprature: float = None):
        
        if not self.client:
            self.logger.error("CoHere client not initialized.")
            return None
        
        if self.generation_model_id is None:
            self.logger.error("CoHere Generation model ID not set.")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generator_max_output_tokens
        temprature = temprature if temprature else self.default_generation_temprature


        response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt),
            max_tokens = max_output_tokens,
            temperature = temprature
        )



        if not response or not response.text:
            self.logger.error("Error while generating the text with CoHere")
            return None
        
        return response.text
    

    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("CoHere client not initialized.")
            return None
        
        if self.embedding_model_id is None:
            self.logger.error("CoHereEmbedding model ID not set.")
            return None
        
        input_type = CohereEnums.DOCUMENT
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CohereEnums.QUERY
        
        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type = input_type,
            embedding_types = ['float'] 
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding the text with CoHere")
            return None
        
        return response.embeddings.float[0]
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }
