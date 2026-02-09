from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
import json
import os
import dotenv
dotenv.load_dotenv()

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
azure_credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
client = SearchIndexClient(endpoint = service_endpoint, credential = azure_credential)

# List existing indexes
indexes = client.list_indexes()

for index in indexes:
   index_dict = index.as_dict()
   print("Index Name:", index_dict['name'])