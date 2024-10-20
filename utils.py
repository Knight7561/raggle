import requests
import os

def search_brave(query):
    api_key=os.environ.get("SEARCH_API")
    # Define the endpoint for Brave Search
    url = "https://search.brave.com/api/search"

    # Set up the parameters for the search
    params = {
        'q': query,
        'source': 'web',
        'count': 10  # Number of results to return
    }

    # Set up headers including the API key
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    print(url,params,headers)
    # Send a GET request to the Brave Search API
    response = requests.get(url, params=params, headers=headers)


    # Check if w   the request was successful
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        print(f"Error: {response.status_code}")
        return None