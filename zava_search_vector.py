import os

import azure.identity
import dotenv
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import OpenAI

from render_table import render_product_results

dotenv.load_dotenv()

azure_credential = azure.identity.AzureCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"])
token_provider = azure.identity.get_bearer_token_provider(
    azure_credential, "https://cognitiveservices.azure.com/.default"
)

openai_client = OpenAI(
    base_url=f"https://{os.environ['AZURE_OPENAI_SERVICE']}.openai.azure.com/openai/v1", api_key=token_provider
)

search_client = SearchClient(
    f"https://{os.environ['AZURE_SEARCH_SERVICE']}.search.windows.net",
    "zava-products-index",
    credential=azure_credential,
)

search_query = "100 foot hose that won't break"

search_vector = (
    openai_client.embeddings.create(model=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"], input=search_query)
    .data[0]
    .embedding
)

results = search_client.search(
    None, top=5, vector_queries=[VectorizedQuery(vector=search_vector, k_nearest_neighbors=50, fields="embedding")]
)

render_product_results(results, f"Vector search results for '{search_query}'")
