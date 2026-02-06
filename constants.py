import os


DEFAULT_MAX_TOKENS = 512

# Azure Open AI Model Deployment Names

AZURE_GPT_4_DEPLOYMENT = os.getenv("AZURE_GPT_4_DEPLOYMENT")

# Azure OpenAI Model Versions
AZURE_GPT_4_VERSION = os.getenv(
    "AZURE_GPT_4_VERSION"
)
AZURE_TEXT_EMBEDDING_ADA_002_DEPLOYMENT = os.getenv(
    "AZURE_TEXT_EMBEDDING_ADA_002_DEPLOYMENT"
)

# Azure Open AI Keys(GPT-4 128K)
AZURE_OPEN_AI_KEY = os.getenv("AZURE_OPEN_AI_KEY")
AZURE_OPEN_AI_ENDPOINT = os.getenv("AZURE_OPEN_AI_ENDPOINT")

# GOOGLE_APPLICATION_CREDENTIALS = "C:\credentials\coforge-idp-project-fe97ba5e9388.json"
# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

# Response dict
RESPONSE_DICT = {
    "id": "",
    "input_text": "",
    "response_text": "",
    "prompt_tokens": 0,
    "response_tokens": 0,
    "total_tokens": 0,
    "model_role": "",
    "model_type": ""
}
provider = "azure"
model_name = "gpt-4"