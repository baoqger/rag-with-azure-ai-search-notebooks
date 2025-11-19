import os

import azure.identity
import dotenv
from azure.search.documents import SearchClient

from render_table import render_product_results

dotenv.load_dotenv()

azure_credential = azure.identity.AzureCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"])

search_client = SearchClient(
    f"https://{os.environ['AZURE_SEARCH_SERVICE']}.search.windows.net",
    "zava-products-index",
    credential=azure_credential,
)

search_query = "25 foot hose"
search_query = "water plants efficiently without waste"

results = search_client.search(search_text=search_query, top=5)

render_product_results(results, f"Keyword search results for '{search_query}'")