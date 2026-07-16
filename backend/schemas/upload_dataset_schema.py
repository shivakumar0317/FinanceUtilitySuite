from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UploadHistoryItem(BaseModel):
    id: int
    dataset_type: str
    filename: str
    content_type: str | None
    row_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
