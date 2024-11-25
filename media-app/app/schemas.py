from pydantic import BaseModel


class FileResponse(BaseModel):
    uid: str
    original_name: str
    size: int
    format_type: str
    extension: str

    class Config:
        orm_mode = True
