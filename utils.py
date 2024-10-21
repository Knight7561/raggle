import requests
import os
import json

from dotenv import load_dotenv

load_dotenv()



def parse_brave_results(json_reponse):
    def extract_web_metadata(data:dict):
        return {key: data[key] for key in ('title', 'description', 'url')}
    all_web_search = json_reponse['web']['results']
    extracted_info=list(map(extract_web_metadata,all_web_search))
    return extracted_info

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
    print(url,params,headers)
    # Send a GET request to the Brave Search API
    response = requests.get(url, params=params, headers=headers)


    # Check if w   the request was successful
    if response.status_code == 200:
        return parse_brave_results(response.json())  # Return the JSON response
    else:
        print(f"Error: {response.status_code}")
        return None

# # code used to parse brave output from a json file
# Load JSON data from a file
# def load_json_from_file(file_path):
#     with open(file_path, 'r') as file:
#         return json.load(file)

# file_path = './temp/brave_output.json'
# json_object = load_json_from_file(file_path)
# print(parse_brave_results(json_object))