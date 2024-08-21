from pydantic import BaseModel, Field


class WPSWatchImage(BaseModel):
    file_path: str = Field(..., title="Attachment path within storage")


class WPSWatchImageMetadata(BaseModel):
    camera_id: str = Field(..., title="Camera name")

    class Config:
        extra = "allow"  # To allow adding extra fields with field mappings
