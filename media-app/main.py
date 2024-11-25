import uuid
from fastapi import FastAPI, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import init_db, get_session
from app.models import FileMetadata
from app.utils import save_to_disk, upload_to_cloud, get_file_path
from app.schemas import FileResponse

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile, db: AsyncSession = get_session()):
    try:
        # Генерация UID
        file_uid = str(uuid.uuid4())
        # Сохранение на диск
        file_path, file_size = await save_to_disk(file, file_uid)
        # Сохранение в облако (условное API)
        await upload_to_cloud(file_path, file_uid)
        # Сохранение метаданных в БД
        metadata = FileMetadata(
            uid=file_uid,
            original_name=file.filename,
            size=file_size,
            extension=file.filename.split('.')[-1],
            mime_type=file.content_type
        )
        db.add(metadata)
        await db.commit()
        return FileResponse(uid=file_uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/{file_uid}")
async def download_file(file_uid: str):
    file_path = await get_file_path(file_uid)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        file_path=file_path,
        media_type="application/octet-stream",
        filename=f"{file_uid}"
    )
