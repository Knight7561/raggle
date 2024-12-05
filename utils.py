from typing import Dict
import requests
import os
import json
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from custom_types import WebResultMetaData
from sentence_transformers import CrossEncoder
import numpy as np

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}
SEARCH_API_KEY = os.environ.get("SEARCH_API")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
PROMPTS_FILE_PATH = "assets/prompts.json"


def extract_web_metadata(data: dict):
    """Extracts metadata from web search result."""
    return {
        data["url"]: WebResultMetaData(
            **{key: data[key] for key in ("title", "description", "url")}
        )
    }

def parse_brave_results(json_reponse) -> Dict[str, WebResultMetaData]:
    """Parses the JSON response from Brave search results."""
    all_web_search = json_reponse["web"]["results"]
    extracted_info = list(map(extract_web_metadata, all_web_search))
    result = {}
    for d in extracted_info:
        result.update(d)
    return result


def scraper(webMetadata: Dict[str, WebResultMetaData]) -> Dict[str, WebResultMetaData]:
    """Scrapes the content from web pages using the provided metadata."""
    header = DEFAULT_HEADERS
    for _, metadata in webMetadata.items():
        try:
            response = requests.get(metadata.url, headers=header)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            main_content = soup.find("main") or soup.find("article") or soup.body
            if main_content:
                text = main_content.get_text(
                    separator="\n", strip=True
                )  # Use separator to maintain structure
                # Optionally filter out short lines or noise
                filtered_text = "\n".join(
                    line for line in text.splitlines() if len(line) > 30
                )  # Filter short lines
                filtered_text = filtered_text.encode(
                    "ascii", "ignore"
                ).decode()  # applies ascii filter - removes unicode characters.
            metadata.scrapped_data = (
                filtered_text if filtered_text else ""
            )  # or response.json() if it's a JSON response

        except requests.RequestException as e:
            logger.error(f"Error fetching {metadata.url}: {e}")
    return webMetadata


def search_web_brave(query) -> Dict[str, WebResultMetaData] | None:
    """Searches the web using Brave and returns metadata."""
    if not SEARCH_API_KEY:
        logger.error("SEARCH_API environment variable not set.")
        return None
    # Set up headers including the API key
    headers = {"X-Subscription-Token": SEARCH_API_KEY}
    # Send a GET request to the Brave Search API
    response = requests.get(
        BRAVE_SEARCH_URL,
        params={"q": query, "source": "web", "count": 10},
        headers=headers,
    )

    # Check if the request was successful
    if response.status_code == 200:
        return parse_brave_results(response.json())  # Return the JSON response
    else:
        logger.error(
            f"Error during Brave search: {response._content} response.status_code : {response.status_code}"
        )
        return None


def chunk_data_and_preprocess(
    webMetadata: Dict[str, WebResultMetaData], size: int = 1000, overlap: int = 200
) -> dict[str, list]:
    """Chunks the scraped data into manageable pieces for processing."""
    processed_chunks: dict[str, list] = {"documents": [], "ids": [], "metaData": []}
    for url, webMetaData in webMetadata.items():
        text = webMetaData.scrapped_data
        for pos in range(0, len(text), size - overlap):
            processed_chunks["documents"].append(text[pos : pos + size])
            processed_chunks["ids"].append(url + "_" + str(pos))
            processed_chunks["metaData"].append(
                {"title": webMetaData.title, "url": webMetaData.url}
            )
    return processed_chunks


def rerank_documents(query: str, relevent_documents: dict) -> dict:
    """
    Reranks documents based on their relevance to the query using a Cross-Encoder.

    Parameters:
        query (str): The original search query.
        documents (dict): List of document texts to be reranked, of format
            {'ids': [[...]], 'distances': [[...]], 'metadatas': [[...]], 'embeddings': None, 'documents': [[...]], 'uris': None, 'data': None}

    Returns:
        List[Tuple[str, float]]: A list of tuples where each tuple contains
                                  a document and its corresponding relevance score.
    """
    reranker = CrossEncoder("cross-encoder/ms-marco-TinyBERT-L-2")
    if not len(relevent_documents["documents"][0])>0:
        logger.error(f"Error: The No relevant documents found to rerank.")
        return relevent_documents
    inputs = [[query, doc] for doc in relevent_documents["documents"][0]]
    scores = reranker.predict(inputs)
    relevent_documents["reranked_scores"] = [list(scores)]
    sorted_indices = np.argsort(scores)[::-1]
    for i in relevent_documents.keys():
        # Below line avoids sorting in any key which iis not related to data.
        if len(relevent_documents[i][0])==len(sorted_indices):
            relevent_documents[i] = (
                [[relevent_documents[i][0][idx] for idx in sorted_indices]]
                if relevent_documents[i] is not None
                else relevent_documents[i]
            )
    return relevent_documents

def read_prompts(prompt_name, file_path=PROMPTS_FILE_PATH):
    """Reads prompts from a specified JSON file and returns them as a list."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data.get(prompt_name, [])
    except FileNotFoundError:
        logger.error(f"Error: The file {file_path} does not exist.")
    except json.JSONDecodeError:
        logger.error(f"Error: The file {file_path} is not a valid JSON.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    return []


def google_genai_inference(prompt):
    """Generates content using Google's generative AI model."""
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "response_mime_type": "text/plain",
    }
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY environment variable not set.")
        return "API key not set."
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro", generation_config=generation_config
    )
    response = model.generate_content(prompt)
    return response.text


def rewrite_query(query):
    QUERY_REWRITE_PROMPT:str = str(read_prompts('QUERY_REWRITE_PROMPT'))
    prompt=QUERY_REWRITE_PROMPT.format(query=query)
    return google_genai_inference(prompt)