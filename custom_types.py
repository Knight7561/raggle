from pydantic import BaseModel

class WebResultMetaData(BaseModel):
    title: str=''
    description: str=''
    url: str
    scrapped_data: str =''
