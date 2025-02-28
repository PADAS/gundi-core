from pydantic import BaseModel, Field


class TrapTaggerImage(BaseModel):
    file_path: str = Field(..., title="Attachment path within storage")


class TrapTaggerImageMetadata(BaseModel):
    camera: str = Field(..., title="Camera name")
    latitude: str = Field(..., title="Latitude")
    longitude: str = Field(..., title="Longitude")
    timestamp: str = Field(..., title="Timestamp", description="YYYY-MM-DD HH:MM:SS")

    class Config:
        extra = "allow"  # To allow adding extra fields with field mappings
