import os
import aiofiles
from fastapi import UploadFile

STORAGE_DIR = "./storage"


async def save_to_disk(file: UploadFile, file_uid: str):
    os.makedirs(STORAGE_DIR, exist_ok=True)
    file_path = os.path.join(STORAGE_DIR, file_uid)
    size = 0
    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await file.read(1024):
            size += len(content)
            await out_file.write(content)
    return file_path, size


async def upload_to_cloud(file_path: str, file_uid: str):
    print(f"Uploading {file_path} to cloud as {file_uid}")


async def get_file_path(file_uid: str):
    file_path = os.path.join(STORAGE_DIR, file_uid)
    return file_path if os.path.exists(file_path) else None