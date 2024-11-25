from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FileMetadata(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False)
    original_name = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    format_type = Column(String, nullable=False)
    extension = Column(String, nullable=False)