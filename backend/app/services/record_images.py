from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.study import StudyRecord, StudyRecordImage
from app.services.doubao import DoubaoService

ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def save_and_analyze_uploads(
    *,
    db: Session,
    settings: Settings,
    doubao: DoubaoService,
    user_id: int,
    record: StudyRecord,
    files: list[UploadFile],
) -> list[StudyRecordImage]:
    images: list[StudyRecordImage] = []
    for upload in files:
        if not upload.filename:
            continue
        if upload.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported image type: {upload.content_type}",
            )
        image_bytes = upload.file.read()
        if len(image_bytes) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image is too large",
            )

        stored_path = write_image_file(
            settings=settings,
            user_id=user_id,
            record_id=record.id,
            image_bytes=image_bytes,
            content_type=upload.content_type,
        )
        result = doubao.analyze_problem_image(
            image_bytes=image_bytes,
            content_type=upload.content_type,
            record=record,
        )
        image = StudyRecordImage(
            user_id=user_id,
            record_id=record.id,
            original_filename=Path(upload.filename).name,
            stored_path=stored_path,
            content_type=upload.content_type,
            file_size=len(image_bytes),
            analysis_status=result.status,
            analysis_text=result.analysis_text,
            knowledge_points=json.dumps(result.knowledge_points, ensure_ascii=False),
            mistakes=json.dumps(result.mistakes, ensure_ascii=False),
            suggestions=json.dumps(result.suggestions, ensure_ascii=False),
            error_message=result.error_message,
        )
        db.add(image)
        images.append(image)

    if images:
        db.commit()
        for image in images:
            db.refresh(image)
    return images


def write_image_file(
    *,
    settings: Settings,
    user_id: int,
    record_id: int,
    image_bytes: bytes,
    content_type: str,
) -> str:
    suffix = ALLOWED_IMAGE_TYPES[content_type]
    target_dir = Path(settings.upload_dir) / "record-images" / str(user_id) / str(record_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{uuid.uuid4().hex}{suffix}"
    target_path.write_bytes(image_bytes)
    return target_path.as_posix()
