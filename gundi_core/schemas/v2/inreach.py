import re
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from email.utils import parseaddr
from pydantic import BaseModel, Field, validator, root_validator


class InreachCoordinate(BaseModel):
    Latitude: float = Field(..., ge=-90.0, le=90.0)
    Longitude: float = Field(..., ge=-360.0, le=360.0)


class InreachReferencePoint(BaseModel):
    Altitude: int = 0
    Coordinate: InreachCoordinate
    Course: int = Field(0, ge=-360.0, le=360.0)
    Label: str = ""
    Speed: int = 0


PHONENUMBER_RE = re.compile("\+?[\d\.\-\(\)]{8,12}")


# Schema for InReach Inbound IPC (Sending messages to InReach Service)
class InReachIPCMessage(BaseModel):
    Message: str
    Recipients: List[str]
    Sender: str
    ReferencePoint: Optional[InreachReferencePoint]
    Timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda val: f"/Date({int(val.timestamp()*1000)})/"}

    @validator("Sender")
    def clean_sender(cls, v):
        # Accept a value with a single @
        if len(parseaddr(v)[1].split("@")) == 2:
            return v

        if PHONENUMBER_RE.match(v):
            return v

        raise ValueError("Sender must be a valid email address or phone number.")
