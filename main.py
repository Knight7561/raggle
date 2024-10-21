from utils import search_web_brave


class raggle():
    '''
    Class to build a end-to-end Search.
    '''
    def __init__(self):
        # self.searchApiKey=os.environ.get("SEARCH_API") #skipping line because getting key from the utils would be a better idea
        pass

    def get_search_results(self,query:str):
        return search_web_brave(query)


if __name__=="__main__":
    r=raggle()
    query=r.get_search_results("Latest papers in RAG")
    print("reponse\n\n\n")
    print(query)