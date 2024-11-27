import uuid

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import init_db, get_session
from app.models import FileMetadata
from app.tasks import cleanup_files
from app.utils import save_to_disk, upload_to_cloud, get_file_path
from app.schemas import FileResponse

app = FastAPI()


scheduler = BackgroundScheduler()


@app.on_event("startup")
async def on_startup():
    scheduler.add_job(
        func=cleanup_files,
        name="cron",
        trigger=IntervalTrigger(hours=1)
    )
    scheduler.start()
    await init_db()


@app.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile, db: AsyncSession = get_session()):
    try:
        file_uid = str(uuid.uuid4())
        file_path, file_size = await save_to_disk(file, file_uid)
        await upload_to_cloud(file_path, file_uid)
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


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
