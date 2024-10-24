import json
from typing import List
from utils import search_web_brave,scraper
from custom_types import WebResultMetaData


class raggle():
    '''
    Class to build a end-to-end Search.
    '''
    def __init__(self):
        # skipping line because getting key from the utils would be a better idea
        # self.searchApiKey=os.environ.get("SEARCH_API")
        pass

    def get_search_results(self,query:str):
        return search_web_brave(query)

    def scrap_data(self,webMetadata:List[WebResultMetaData]):
        return scraper(webMetadata)


if __name__=="__main__":
    r=raggle()
    search_links=r.get_search_results("What is RAG in AI?")
    scrapped_information=r.scrap_data(search_links)
    scrapped_information=json.dumps(scrapped_information,default=lambda x: x.__dict__)
    with open('temp/output.json', 'w') as f:
        f.write(scrapped_information)