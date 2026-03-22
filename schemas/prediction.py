from pydantic import BaseModel

class PredictRequest(BaseModel):
    file_id : int