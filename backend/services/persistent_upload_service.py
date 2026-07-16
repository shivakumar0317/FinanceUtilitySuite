from __future__ import annotations

from threading import Lock
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.models.uploaded_dataset import UploadedDataset


class PersistentUploadService:
    PORTFOLIO_LIVE = "portfolio_live"
    MTF = "mtf"

    @classmethod
    def save_dataframe(
        cls,
        db: Session,
        *,
        user_id: int,
        dataset_type: str,
        filename: str,
        content_type: str | None,
        dataframe: pd.DataFrame,
    ) -> UploadedDataset:
        payload = cls._dataframe_to_payload(dataframe)

        try:
            db.execute(
                update(UploadedDataset)
                .where(
                    UploadedDataset.user_id == user_id,
                    UploadedDataset.dataset_type == dataset_type,
                    UploadedDataset.is_active.is_(True),
                )
                .values(is_active=False)
            )

            record = UploadedDataset(
                user_id=user_id,
                dataset_type=dataset_type,
                filename=filename or "upload",
                content_type=content_type,
                row_count=len(payload),
                payload=payload,
                is_active=True,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def list_history(db: Session, *, user_id: int, dataset_type: str) -> list[UploadedDataset]:
        statement = (
            select(UploadedDataset)
            .where(
                UploadedDataset.user_id == user_id,
                UploadedDataset.dataset_type == dataset_type,
            )
            .order_by(UploadedDataset.created_at.desc())
        )
        return list(db.scalars(statement).all())

    @staticmethod
    def get_active(db: Session, *, user_id: int, dataset_type: str) -> UploadedDataset | None:
        statement = (
            select(UploadedDataset)
            .where(
                UploadedDataset.user_id == user_id,
                UploadedDataset.dataset_type == dataset_type,
                UploadedDataset.is_active.is_(True),
            )
            .order_by(UploadedDataset.created_at.desc())
            .limit(1)
        )
        return db.scalar(statement)

    @classmethod
    def activate(
        cls,
        db: Session,
        *,
        user_id: int,
        dataset_type: str,
        upload_id: int,
    ) -> UploadedDataset:
        record = cls._get_owned_record(
            db,
            user_id=user_id,
            dataset_type=dataset_type,
            upload_id=upload_id,
        )
        try:
            db.execute(
                update(UploadedDataset)
                .where(
                    UploadedDataset.user_id == user_id,
                    UploadedDataset.dataset_type == dataset_type,
                )
                .values(is_active=False)
            )
            record.is_active = True
            db.commit()
            db.refresh(record)
            return record
        except Exception:
            db.rollback()
            raise

    @classmethod
    def delete(
        cls,
        db: Session,
        *,
        user_id: int,
        dataset_type: str,
        upload_id: int,
    ) -> None:
        record = cls._get_owned_record(
            db,
            user_id=user_id,
            dataset_type=dataset_type,
            upload_id=upload_id,
        )
        was_active = record.is_active
        try:
            db.delete(record)
            db.flush()
            if was_active:
                replacement = db.scalar(
                    select(UploadedDataset)
                    .where(
                        UploadedDataset.user_id == user_id,
                        UploadedDataset.dataset_type == dataset_type,
                    )
                    .order_by(UploadedDataset.created_at.desc())
                    .limit(1)
                )
                if replacement is not None:
                    replacement.is_active = True
            db.commit()
        except Exception:
            db.rollback()
            raise

    @classmethod
    def restore_dataframe(
        cls,
        db: Session,
        *,
        user_id: int,
        dataset_type: str,
    ) -> pd.DataFrame | None:
        record = cls.get_active(db, user_id=user_id, dataset_type=dataset_type)
        return None if record is None else pd.DataFrame(record.payload)

    @classmethod
    def restore_cache(
        cls,
        db: Session,
        *,
        user_id: int,
        dataset_type: str,
        cache: dict[int, pd.DataFrame],
        lock: Lock,
    ) -> bool:
        with lock:
            if user_id in cache:
                return True
        dataframe = cls.restore_dataframe(db, user_id=user_id, dataset_type=dataset_type)
        if dataframe is None:
            return False
        with lock:
            cache[user_id] = dataframe
        return True

    @staticmethod
    def clear_cache(*, user_id: int, cache: dict[int, pd.DataFrame], lock: Lock) -> None:
        with lock:
            cache.pop(user_id, None)

    @staticmethod
    def _get_owned_record(
        db: Session,
        *,
        user_id: int,
        dataset_type: str,
        upload_id: int,
    ) -> UploadedDataset:
        record = db.scalar(
            select(UploadedDataset).where(
                UploadedDataset.id == upload_id,
                UploadedDataset.user_id == user_id,
                UploadedDataset.dataset_type == dataset_type,
            )
        )
        if record is None:
            raise ValueError("Upload record not found.")
        return record

    @classmethod
    def _dataframe_to_payload(cls, dataframe: pd.DataFrame) -> list[dict]:
        clean = dataframe.copy().replace([np.inf, -np.inf], np.nan)
        clean = clean.where(pd.notna(clean), None)
        return [cls._json_safe(row) for row in clean.to_dict(orient="records")]

    @classmethod
    def _json_safe(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): cls._json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._json_safe(item) for item in value]
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass
        return value
