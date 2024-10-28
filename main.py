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

# Constants
DEFAULT__EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "my_collection"
SYSTEM_PROMPT_KEY = "SYSTEM_PROMPT"
USER_PROMPT_KEY = "USER_PROMPT"

logger = logging.getLogger(__name__)
logging.basicConfig(filename='run_log.log', encoding='utf-8', level=logging.DEBUG)

class Raggle:
    """
    Class to build an end-to-end search system using Retrieval-Augmented Generation (RAG).

    This class integrates web searching, data scraping, processing,
    and generating responses based on user queries.
    """

    def __init__(self, embedding_model=None):
        """
        Initializes the Raggle class.

        Parameters:
        - embedding_model: Optional custom embedding model. If None,
          a default model is used.
        """
        self.embedding_model = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=DEFAULT__EMBEDDING_MODEL_NAME
            )
            if embedding_model is None
            else embedding_model
        )
        self.__init_vectorDB()

        logger.debug('raggle is initlised and ready')

    def __init_vectorDB(self):
            """Initializes the vector database (Chroma, for now) for storing embeddings."""
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME, embedding_function=self.embedding_model
            )
    def get_search_results(self, query: str) -> Dict[str, WebResultMetaData] | None:
        """
        Retrieves search results from the web.

        Parameters:
        - query: The search query string.

        Returns:
        - A dictionary containing web result metadata or None if no results found.
        """
        try:
                return search_web_brave(query)
        except Exception as e:
                self.logger.error(f"Error during web search: {e}")
                return None

    def scrape_data(
        self, webMetadata: Dict[str, WebResultMetaData]
    ) -> Dict[str, WebResultMetaData]:
        """
        Scrapes data from the provided web metadata.

        Parameters:
        - webMetadata: A dictionary containing metadata from web search results.

        Returns:
        - A dictionary containing scraped information.
        """
        try:
            return scraper(webMetadata)
        except Exception as e:
            self.logger.error(f"Error during data scraping: {e}")
            return {}

    def ingest_data(self, webMetadata: Dict[str, WebResultMetaData]):
        """
        Ingests and processes scraped data into the vector database.

        Parameters:
        - webMetadata: A dictionary containing scraped metadata to be ingested.
        """
        try:
            processed_chunks = chunk_data_and_preprocess(webMetadata)
            self.collection.add(
                documents=processed_chunks["documents"],
                ids=processed_chunks["ids"],
                metadatas=processed_chunks["metaData"],
            )
            self.logger.debug("Data ingested to vectorDB successfully.")
        except Exception as e:
            self.logger.error(f"Error during data ingestion to vectorDB: {e}")


    def count_collection(self):
        """
        Counts the number of items in the vector database.

        Returns:
        - The count of items in the collection.
        """
        return self.collection.count()

    def get_relevent_documents(self, query):
        """
        Performs a query search in the vector database.

        Parameters:
        - query: The query string to search.

        Returns:
        - The relevent documents from the vector database.
        """
        try:
            results = self.collection.query(
                query_texts=[query],  # Chroma will embed this for you
                )
            return results
        except Exception as e:
            self.logger.error(f"Error during search query: {e}")
            return {}


    def generate_answer(self, query, query_search_results):
        """
        Generates an answer based on the query and search results.

        Parameters:
        - query: The original query string.
        - query_search_results: The results obtained from the search query.

        Returns:
        - The generated response based on the query and context.
        """
        try:
            SYSTEM_PROMPT:str = read_prompts(SYSTEM_PROMPT_KEY)
            USER_PROMPT:str = str(read_prompts(USER_PROMPT_KEY))
            context:str = "###".join(query_search_results["documents"][0])
            prompt=SYSTEM_PROMPT+USER_PROMPT.format(query=query,context=context)
            return google_genai_inference(prompt)
        except Exception as e:
            self.logger.error(f"Error during answer generation: {e}")
            return "Error generating answer."

    def search_web(self,QUERY):
        """
        Conducts a web search and generates a response based on the query.

        Parameters:
        - QUERY: The search query string.

        Returns:
        - The generated response from the web search and data processing.
        """
        search_links = self.get_search_results(QUERY)
        logging.debug('Internet metadata search completed ')
        if search_links is None:
            print("No Search could be done on internet")
            logging.error('ERROR: No Search could be done on internet')
            exit(-1)
        scrapped_information = self.scrape_data(search_links)
        logging.debug('Internet data scrapping completed ')
        logging.debug('data_ingest to vectorDB: START')
        self.ingest_data(scrapped_information)
        logging.debug('data_ingest to vectorDB: DONE')
        logging.debug('Searching for Query:: START')
        query_search_results = self.get_relevent_documents(QUERY)
        logging.debug('Searching for Query:: RELAVENT CHUNKS RETERIEVED')
        generated_reponse=self.generate_answer(QUERY, query_search_results)
        logging.debug('Searching for Query:: COMPLETED WITH RESPONSE')
        return generated_reponse


if __name__ == "__main__":
    QUERY = "What are the different compoenents of RAG"
    r = Raggle()
    generated_reponse=r.search_web(QUERY)
    with open("temp/output.txt", "w") as f:
        f.write(generated_reponse)
