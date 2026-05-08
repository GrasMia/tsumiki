from datetime import datetime
from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from app.models import Status


class DirInfo(BaseModel):
    name: str
    created_at: datetime
    modified_at: datetime

    @field_serializer(*["created_at", "modified_at"])
    def serialize_datetime(self, val: datetime) -> str:
        return val.isoformat(timespec="seconds")

    model_config = ConfigDict(from_attributes=True)


class FileInfo(BaseModel):
    name: str
    size: int = Field(gt=0)
    sha256: str = Field(min_length=64, max_length=64)
    created_at: datetime
    modified_at: datetime

    @field_serializer(*["created_at", "modified_at"])
    def serialize_datetime(self, val: datetime) -> str:
        return val.replace(microsecond=0).isoformat()

    model_config = ConfigDict(from_attributes=True)


class FileMetadata(BaseModel):
    name: str
    size: int = Field(gt=0)
    sha256: str = Field(min_length=64, max_length=64)


class ChunkInfo(BaseModel):
    id: str = Field(min_length=36, max_length=36)
    chunk_index: int = Field(ge=0)
    total_chunks: int = Field(ge=0)
    status: Status

    model_config = ConfigDict(from_attributes=True)


class ChunkMetadata(BaseModel):
    id: str = Field(min_length=36, max_length=36)
    chunk_index: int = Field(ge=0)
    md5: str = Field(...)

    @staticmethod
    async def init_by_form(
        id: str = Form(...),
        chunk_index: int = Form(...),
        md5: str = Form(...),
    ) -> "ChunkMetadata":
        return ChunkMetadata(id=id, chunk_index=chunk_index, md5=md5)


# class TrashInfo(BaseModel):
#     name: str
#     size: int
#     sha256: str = Field(min_length=64, max_length=64)
#     deleted_at: datetime
#     expires_at: datetime

#     @field_serializer(*["deleted_at", "expires_at"])
#     def serialize_datetime(self, val: datetime) -> str:
#         return val.replace(microsecond=0).isoformat()

#     model_config = ConfigDict(from_attributes=True)
