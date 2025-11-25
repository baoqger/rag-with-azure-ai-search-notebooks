# Azure AI Search Demos

This repository contains many notebooks that explain how Azure AI Search works, including several showcasing how vector search works.

## Environment setup

1. Run `azd up` on [azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo/) with multimodal feature enabled. This will create the necessary resources for the Azure OpenAI, Azure AI Search services, and the Azure AI Vision service.

2. Create a .env with these variables, with the values taken from `.azure/ENV-NAME/.env` in the azure-search-openai-demo repository.

    ```shell
    AZURE_OPENAI_SERVICE=YOUR-SERVICE-NAME
    AZURE_OPENAI_DEPLOYMENT_NAME=YOUR-OPENAI-DEPLOYMENT-NAME
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=YOUR-EMBED-DEPLOYMENT-NAME
    AZURE_SEARCH_SERVICE=YOUR-SEARCH-SERVICE-NAME
    AZURE_SEARCH_INDEX=YOUR-SEARCH-INDEX-NAME
    AZURE_SEARCH_EMBEDDING_FIELD=YOUR-EMBEDDING-FIELD-NAME
    AZURE_VISION_ENDPOINT=YOUR-VISION-ENDPOINT
    AZURE_TENANT_ID=YOUR-TENANT-ID
    ```

3. Login to your Azure account using the Azure CLI. Specify `--tenant-id` if you deployed that repo to a non-default tenant.

    ```shell
    azd auth login
    ```

4. Create a Python virtual environment or open the project in a container.

5. Install the requirements:

    ```shell
    pip install -r requirements.txt
    ```

## Search on documents

These notebooks operate on the index from the [azure-search-openai-demo](https://github.com/Azure-Samples/azure-search-openai-demo/) repository, which contains chunked documents from a fictional company.

* [Vector Embeddings Notebook](./vector_embeddings.ipynb)
* [Azure AI Search Notebook](./azure_ai_search.ipynb)
* [Image Search Notebook](./image_search.ipynb)
* [Azure AI Search Relevance Notebook](./search_relevance.ipynb)
* [RAG with Azure AI Search](./rag.ipynb)
* [RAG Evaluation](./rag_eval.ipynb)

You can find video recordings going through the notebooks [here](https://github.com/microsoft/aitour-rag-with-ai-search/tree/main/session-delivery-resources#video-recordings).

## Search on product catalog

You can also try out search techniques on a Zava product catalog.
First, create the search index and upload the products by running:

```shell
python zava_product_upload.py
```

Then, explore the different search techniques with these Python scripts or notebooks:

* [Keyword Search](./zava_search_keyword.py) | [Notebook](./zava_search_keyword.ipynb)
* [Vector Search](./zava_search_vector.py) | [Notebook](./zava_search_vector.ipynb)
* [Hybrid Search with RRF](./zava_search_rrf.py) | [Notebook](./zava_search_rrf.ipynb)
* [Hybrid Search with RRF + Reranker](./zava_search_reranker.py) | [Notebook](./zava_search_reranker.ipynb)
