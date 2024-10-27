from typing import Dict
import requests
import os
import json
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

from custom_types import WebResultMetaData

load_dotenv()


def parse_brave_results(json_reponse) -> Dict[str, WebResultMetaData]:
    def extract_web_metadata(data: dict):
        return {
            data["url"]: WebResultMetaData(
                **{key: data[key] for key in ("title", "description", "url")}
            )
        }

    all_web_search = json_reponse["web"]["results"]
    extracted_info = list(map(extract_web_metadata, all_web_search))
    result = {}
    for d in extracted_info:
        result.update(d)
    return result


def scraper(webMetadata: Dict[str, WebResultMetaData]) -> Dict[str, WebResultMetaData]:
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    for key, metadata in webMetadata.items():
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
            print(f"Error fetching {metadata.url}: {e}")
    return webMetadata


def search_web_brave(query) -> Dict[str, WebResultMetaData] | None:
    api_key = os.environ.get("SEARCH_API")
    # Define the endpoint for Brave Search
    url = "https://api.search.brave.com/res/v1/web/search"

    # Set up the parameters for the search
    params = {"q": query, "source": "web", "count": 10}  # Number of results to return

    # Set up headers including the API key
    headers = {"X-Subscription-Token": api_key}
    # Send a GET request to the Brave Search API
    response = requests.get(url, params=params, headers=headers)

    # Check if w   the request was successful
    if response.status_code == 200:
        return parse_brave_results(response.json())  # Return the JSON response
    else:
        print(f"Error: {response.status_code}")
        return None


def chunk_data_and_preprocess(
    webMetadata: Dict[str, WebResultMetaData], size: int = 1000, overlap: int = 200
) -> dict[str, list]:
    for url, webMetaData in webMetadata.items():
        text = webMetaData.scrapped_data
        processed_chunks: dict[str, list] = {"documents": [], "ids": [], "metaData": []}
        for pos in range(0, len(text), size - overlap):
            processed_chunks["documents"].append(text[pos : pos + size])
            processed_chunks["ids"].append(url + "_" + str(pos))
            processed_chunks["metaData"].append(
                {"title": webMetaData.title, "url": webMetaData.url}
            )
    return processed_chunks


def read_prompts(prompt_name, file_path="assets/prompts.json"):
    """Reads prompts from a specified JSON file and returns them as a list."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data.get(prompt_name, [])
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return []


def google_genai_inference(prompt):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "response_mime_type": "text/plain",
    }
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro",generation_config=generation_config)
    response = model.generate_content(prompt)
    return response.text
