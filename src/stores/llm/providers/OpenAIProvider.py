from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):

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

        self.client = OpenAI(
            api_key=self.api_key,
            api_url=self.api_url,
        )

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
            self.logger.error("OpenAI client not initialized.")
            return None
        
        if self.generation_model_id is None:
            self.logger.error("Generation model ID not set.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generator_max_output_tokens
        temprature = temprature if temprature else self.default_generation_temprature

        chat_history.append(
            self.construct_prompt(
                prompt = prompt,
                role = OpenAIEnums.USER.value
            )
        )

        response = self.client.chat.completions.create(
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_output_tokens,
            temperature = temprature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating the text with OpenAI")
            return None
        
        return response.choices[0].message["content"]




    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None
        
        if self.embedding_model_id is None:
            self.logger.error("Embedding model ID not set.")
            return None
        
        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            input = text,
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None
        
        return response.data[0].embedding
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }