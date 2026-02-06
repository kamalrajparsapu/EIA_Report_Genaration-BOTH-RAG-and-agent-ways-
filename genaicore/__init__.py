#from config import configs
import json
import os


#langchain.debug = True

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import constants
################ Azure Chat GPT 4 128K Open AI Langchain##################
azure_gpt4_openai_text_chat_llm = None
# llm = AzureChatOpenAI(,)
def load_text_chat_azure_gp4_openai(max_tokens=128):
    global azure_gpt4_openai_text_chat_llm
    azure_gpt4_openai_text_chat_llm = AzureChatOpenAI(
        
        azure_endpoint = constants.AZURE_OPEN_AI_ENDPOINT,
        openai_api_key=constants.AZURE_OPEN_AI_KEY,
        openai_api_type="azure",
        azure_deployment=constants.AZURE_GPT_4_DEPLOYMENT,
        api_version = constants.AZURE_GPT_4_VERSION,
        max_tokens=None
    )
    return azure_gpt4_openai_text_chat_llm


################ Azure Open AI Embeddings ##################
azure_openai_text_embeddings_llm = None
def load_text_embeddings_azure_openai():
    global azure_openai_text_embeddings_llm
    model_name = "text-embedding-ada-002"
    azure_openai_text_embeddings_llm = AzureOpenAIEmbeddings(
        azure_deployment = 'embedding-deployment',
        model = model_name,
        azure_endpoint = os.getenv("AZURE_OPENAI_EMBEDDINGS_ENDPOINT"),
        openai_api_key = os.getenv("AZURE_OPENAI__EMBEDDINGS_API_KEY") ,
        openai_api_type = "azure",
        chunk_size = 1
    )
    return azure_openai_text_embeddings_llm



load_text_embeddings_azure_openai()



# if "gpt-4-128K" in models_list:
load_text_chat_azure_gp4_openai(1024)

azure_gpt4_openai_text_chat_llm





