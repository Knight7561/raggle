import json
from typing import Dict, List
from utils import (
    search_web_brave,
    scraper,
    chunk_data_and_preprocess,
    read_prompts,
    google_genai_inference,
)
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
        self.__init_vectorDB()

    def __init_vectorDB(self):
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

    def search_query(self, query):
        results = self.collection.query(
            query_texts=[query],  # Chroma will embed this for you
        )
        return results

    def generate_answer(self, query, query_search_results):
        SYSTEM_PROMPT:str = read_prompts("SYSTEM_PROMPT")
        USER_PROMPT:str = str(read_prompts("USER_PROMPT"))
        context:str = "###".join(query_search_results["documents"][0])
        prompt=SYSTEM_PROMPT+USER_PROMPT.format(query=query,context=context)
        return google_genai_inference(prompt)


if __name__ == "__main__":
    r = raggle()
    QUERY = "What are the different compoenents of RAG"
    search_links = r.get_search_results(QUERY)
    # TODO: if search_links is None, then log error.
    if search_links is None:
        print("No Search could be done on internet")
        exit(-1)
        #TODO add logging
    scrapped_information = r.scrap_data(search_links)
    r.ingest_data(scrapped_information)
    query_search_results = r.search_query(QUERY)
    generated_reponse=r.generate_answer(QUERY, query_search_results)
    print("######## Query",QUERY)
    print(generated_reponse)

    # scrapped_information = json.dumps(
    #     query_search_results, default=lambda x: x.__dict__
    # )
    # with open("temp/output.json", "w") as f:
    #     f.write(scrapped_information)
    with open("temp/output.txt", "w") as f:
        f.write(generated_reponse)
