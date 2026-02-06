"""Script to create an Azure AI Search index for product data and upload products."""

import json
import os
from typing import Any

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import dotenv
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential

dotenv.load_dotenv()

EMBEDDING_DIMENSIONS = 3072  # text-embedding-3-large dimensions


def create_product_index_schema(index_name: str) -> SearchIndex:
    """Create the schema for the product index.

    Args:
        index_name: Name of the index to create

    Returns:
        SearchIndex object with the schema
    """
    fields = [
        SimpleField(
            name="sku",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="name",
            type=SearchFieldDataType.String,
            sortable=True,
        ),
        SearchableField(
            name="description",
            type=SearchFieldDataType.String,
        ),
        SimpleField(
            name="price",
            type=SearchFieldDataType.Double,
            filterable=True,
            sortable=True,
            facetable=True,
        ),
        SimpleField(
            name="stock_level",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
            facetable=True,
        ),
        SearchField(
            name="categories",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            searchable=True,
            filterable=True,
            facetable=True,
        ),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="embedding-profile",
        ),
    ]

    # Configure vector search
    vector_search = VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="embedding-profile",
                algorithm_configuration_name="hnsw-config",
            )
        ],
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config",
                parameters=HnswParameters(metric="cosine"),
            )
        ],
    )

    # Configure semantic search for better relevance
    semantic_config = SemanticConfiguration(
        name="products-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="name"),
            content_fields=[SemanticField(field_name="description")],
            keywords_fields=[SemanticField(field_name="categories")],
        ),
    )

    semantic_search = SemanticSearch(
        default_configuration_name="products-semantic-config",
        configurations=[semantic_config],
    )

    return SearchIndex(
        name=index_name,
        fields=fields,
        semantic_search=semantic_search,
        vector_search=vector_search,
    )


def create_index(index_client: SearchIndexClient, index_name: str) -> None:
    """Create the search index if it doesn't exist.

    Args:
        index_client: Azure Search Index Client
        index_name: Name of the index to create
    """
    print(f"Creating or updating index '{index_name}'...")
    index_schema = create_product_index_schema(index_name)
    index_client.create_or_update_index(index_schema)
    print(f"Index '{index_name}' created/updated successfully.")


def generate_embeddings(openai_client: AzureOpenAI, products: list[dict[str, Any]]) -> None:
    """Generate embeddings for products using OpenAI.

    Args:
        openai_client: OpenAI client
        products: List of product dictionaries (modified in place)
    """
    print("Generating embeddings for products...")

    for i, product in enumerate(products):
        # Create text to embed from name, description, and categories
        text_to_embed = f"{product['name']} {product['description']} {' '.join(product['categories'])}"

        # Generate embedding
        response = openai_client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL_NAME"), input=text_to_embed
        )
        product["embedding"] = response.data[0].embedding

        if (i + 1) % 100 == 0:
            print(f"  Generated embeddings for {i + 1}/{len(products)} products")

    print(f"Generated embeddings for all {len(products)} products.")


def upload_products(search_client: SearchClient, products: list[dict[str, Any]]) -> None:
    """Upload products to the search index.

    Args:
        search_client: Azure Search Client
        products: List of product dictionaries
    """
    print(f"Uploading {len(products)} products...")

    # Upload in batches of 1000 (Azure AI Search limit)
    batch_size = 1000
    for i in range(0, len(products), batch_size):
        batch = products[i : i + batch_size]
        search_client.upload_documents(documents=batch)
        print(f"Uploaded batch {i // batch_size + 1} ({len(batch)} products)")

    print(f"Successfully uploaded {len(products)} products.")


def main() -> None:
    """Main function to create index and upload products."""
    # Load Azure Search environment variables
    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
    AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
    # Load Azure OpenAI environment variables
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")    

    azure_credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)

    openai_client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2024-10-21"
    )

    # Create index search clients
    index_client = SearchIndexClient(endpoint=AZURE_SEARCH_ENDPOINT, credential=azure_credential)
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=azure_credential
    )

    # Create the index
    create_index(index_client, AZURE_SEARCH_INDEX_NAME)

    # Load product data
    print("Loading product data from product_data_flat.json...")
    with open("zava_product_data/product_data_flat.json") as f:
        products = json.load(f)
    print(f"Loaded {len(products)} products.")

    # Generate embeddings
    generate_embeddings(openai_client, products)

    # Upload products
    upload_products(search_client, products)

    print("\n✓ All operations completed successfully!")
    print(f"  - Index: {AZURE_SEARCH_INDEX_NAME}")
    print(f"  - Products uploaded: {len(products)}")


if __name__ == "__main__":
    main()
