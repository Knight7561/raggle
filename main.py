import json
from typing import Dict, List
from utils import search_web_brave, scraper, chunk_data_and_preprocess
from custom_types import WebResultMetaData
import chromadb
from chromadb.utils import embedding_functions


class raggle:
    """
    Class to build a end-to-end Search.
    """

    def __init__(self, embedding_model=None):
        self.embedding_model = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            if embedding_model is None
            else embedding_model
        )
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(
            name="my_collection", embedding_function=self.embedding_model
        )

    def get_search_results(self, query: str) -> Dict[str, WebResultMetaData] | None:
        return search_web_brave(query)

    def scrap_data(
        self, webMetadata: Dict[str, WebResultMetaData]
    ) -> Dict[str, WebResultMetaData]:
        return scraper(webMetadata)

    def ingest_data(self, webMetadata: Dict[str, WebResultMetaData]):
        processed_chunks = chunk_data_and_preprocess(webMetadata)
        self.collection.add(
            documents=processed_chunks["documents"],
            ids=processed_chunks["ids"],
            metadatas=processed_chunks["metaData"],
        )

    def count_collection(self):
        return self.collection.count()

    def search_query(self,query):
        results = self.collection.query(
        query_texts=[query], # Chroma will embed this for you
        n_results=5 # how many results to return
        )
        return results


if __name__ == "__main__":
    r = raggle()
    QUERY="What is RAG in AI?"
    search_links = r.get_search_results(QUERY)
    # TODO: if search_links is None, then log error.
    scrapped_information = r.scrap_data(search_links)
    r.ingest_data(scrapped_information)
    query_search_results=r.search_query(QUERY)

    scrapped_information = json.dumps(
        query_search_results, default=lambda x: x.__dict__
    )
    with open("temp/output.json", "w") as f:
        f.write(scrapped_information)
