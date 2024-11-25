import os
import asyncio

STORAGE_DIR = "./storage"
CLEANUP_THRESHOLD_DAYS = 7


async def cleanup_files():
    now = asyncio.get_event_loop().time()
    for file_name in os.listdir(STORAGE_DIR):
        file_path = os.path.join(STORAGE_DIR, file_name)
        file_mtime = os.path.getmtime(file_path)
        if now - file_mtime > CLEANUP_THRESHOLD_DAYS * 86400:
            os.remove(file_path)
            print(f"Deleted old file: {file_path}")
