from typing import Dict
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
import logging


class raggle:
    """
    Class to build a end-to-end Search.
    """

    def __init__(self, embedding_model=None):
        logger = logging.getLogger(__name__)
        logging.basicConfig(filename='run_log.log', encoding='utf-8', level=logging.DEBUG)
        self.embedding_model = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            if embedding_model is None
            else embedding_model
        )
        self.__init_vectorDB()

        logger.debug('raggle is initlised and ready')

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

    def search_web(self,QUERY):
        search_links = self.get_search_results(QUERY)
        logging.debug('Internet metadata search completed ')
        if search_links is None:
            print("No Search could be done on internet")
            logging.error('ERROR: No Search could be done on internet')
            exit(-1)
        scrapped_information = self.scrap_data(search_links)
        logging.debug('Internet data scrapping completed ')
        logging.debug('data_ingest to vectorDB: START')
        self.ingest_data(scrapped_information)
        logging.debug('data_ingest to vectorDB: DONE')
        logging.debug('Searching for Query:: START')
        query_search_results = self.search_query(QUERY)
        logging.debug('Searching for Query:: RELAVENT CHUNKS RETERIEVED')
        generated_reponse=self.generate_answer(QUERY, query_search_results)
        logging.debug('Searching for Query:: COMPLETED WITH RESPONSE')
        return generated_reponse


if __name__ == "__main__":
    QUERY = "What are the different compoenents of RAG"
    r = raggle()
    generated_reponse=r.search_web(QUERY)
    print(generated_reponse)
    with open("temp/output.txt", "w") as f:
        f.write(generated_reponse)
