from typing import Dict, List
import requests
import os
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from custom_types import WebResultMetaData

load_dotenv()



def parse_brave_results(json_reponse)-> List[WebResultMetaData]:
    def extract_web_metadata(data:dict):
        return WebResultMetaData(**{key: data[key] for key in ('title', 'description', 'url')})
    all_web_search = json_reponse['web']['results']
    extracted_info=list(map(extract_web_metadata,all_web_search))
    return extracted_info

def scraper(webMetadata: List[WebResultMetaData])->List[WebResultMetaData]:
    header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    for metadata in webMetadata:
        try:
            response = requests.get(metadata.url,headers=header)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(['script', 'style']):
                script.decompose()
            main_content = soup.find('main') or soup.find('article') or soup.body
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)  # Use separator to maintain structure
                # Optionally filter out short lines or noise
                filtered_text = "\n".join(line for line in text.splitlines() if len(line) > 30)  # Filter short lines
                filtered_text=filtered_text.encode('ascii', 'ignore').decode() # applies ascii filter - removes unicode characters.
            metadata.scrapped_data = filtered_text if filtered_text else '' # or response.json() if it's a JSON response

        except requests.RequestException as e:
            print(f"Error fetching {metadata.url}: {e}")
    return webMetadata

def search_web_brave(query):
    api_key=os.environ.get("SEARCH_API")
    # Define the endpoint for Brave Search
    url = "https://api.search.brave.com/res/v1/web/search"

    # Set up the parameters for the search
    params = {
        'q': query,
        'source': 'web',
        'count': 10  # Number of results to return
    }

    # Set up headers including the API key
    headers = {
        'X-Subscription-Token': api_key
    }
    # Send a GET request to the Brave Search API
    response = requests.get(url, params=params, headers=headers)


    # Check if w   the request was successful
    if response.status_code == 200:
        return parse_brave_results(response.json())  # Return the JSON response
    else:
        print(f"Error: {response.status_code}")
        return None


def chunk_data(webMetadata: List[WebResultMetaData]):
    pass

# this function needs to changed.
def chunk_results(scrape_results: Dict[str, str], size: int, overlap: int
) -> Dict[str, List[str]]:
    chunking_results: Dict[str, List[str]] = {}
    for url, text in scrape_results.items():
        chunks = []
        for pos in range(0, len(text), size - overlap):
            chunks.append(text[pos : pos + size])
        chunking_results[url] = chunks
    return chunking_results


# # code used to parse brave output from a json file
# Load JSON data from a file
# def load_json_from_file(file_path):
#     with open(file_path, 'r') as file:
#         return json.load(file)

# file_path = './temp/brave_output.json'
# json_object = load_json_from_file(file_path)
# print(parse_brave_results(json_object))