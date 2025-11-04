"""导入批次服务"""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional, Sequence

from sqlalchemy.orm import Session

from app.models.import_batch import ImportBatch, ImportBatchItem
from app.schemas.question import QuestionImportItemResult


def create_batch(
    db: Session,
    *,
    user_id: int,
    mode: str,
    original_name: str,
    file_path: str,
    used_ai: bool,
    warnings: Optional[list] = None,
    stats: Optional[dict] = None,
    total_count: int,
) -> ImportBatch:
    batch = ImportBatch(
        user_id=user_id,
        mode=mode,
        original_name=original_name,
        file_path=file_path,
        used_ai=used_ai,
        warnings=warnings or [],
        stats=stats,
        total_count=total_count,
        success_count=0,
        failed_count=0,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def register_items(
    db: Session,
    batch: ImportBatch,
    items: Sequence[QuestionImportItemResult],
) -> None:
    success = 0
    failed = 0
    for item in items:
        record = ImportBatchItem(
            batch_id=batch.id,
            index=item.index,
            question=item.question,
            question_type=item.question_type,
            answer=item.answer,
            status=item.status,
            message=item.message,
            question_id=item.question_id,
        )
        db.add(record)
        if item.status == "success":
            success += 1
        else:
            failed += 1
    batch.success_count = success
    batch.failed_count = failed
    batch.completed_at = datetime.utcnow()
    db.commit()


def list_batches(
    db: Session,
    user_id: int,
    limit: int = 20,
) -> List[ImportBatch]:
    return (
    db.query(ImportBatch)
    .filter(ImportBatch.user_id == user_id)
    .order_by(ImportBatch.created_at.desc())
    .limit(limit)
        .all()
    )


def get_batch(db: Session, user_id: int, batch_id: int) -> ImportBatch:
    batch = (
        db.query(ImportBatch)
        .filter(ImportBatch.user_id == user_id, ImportBatch.id == batch_id)
        .first()
    )
    if batch is None:
        raise LookupError("导入批次不存在")
    _ = list(batch.items)  # 触发懒加载
    return batch
