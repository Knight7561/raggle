import json
from typing import List
from utils import search_web_brave,scraper
from custom_types import WebResultMetaData


class raggle():
    '''
    Class to build a end-to-end Search.
    '''
    def __init__(self):
        # self.searchApiKey=os.environ.get("SEARCH_API") #skipping line because getting key from the utils would be a better idea
        pass

    def get_search_results(self,query:str):
        return search_web_brave(query)

    def scrap_data(self,webMetadata:List[WebResultMetaData]):
        return scraper(webMetadata)


if __name__=="__main__":
    r=raggle()
    search_links=r.get_search_results("Latest papers in RAG")
    scrapped_information=r.scrap_data(search_links)
    print("reponse\n\n\n")
    scrapped_information=json.dumps(scrapped_information,default=lambda x: x.__dict__)
    with open('temp/output.json', 'w') as f:
        f.write(scrapped_information)