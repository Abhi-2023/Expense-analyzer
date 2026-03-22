from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from utils.jwt import get_current_user
from ml.file_parser import parse_file
from ml.predict_pipeline import predict, build_summary

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard/data")
def get_dashboard_data(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    file_record = (
        db.query(models.UploadedFile)
        .filter(models.UploadedFile.user_id == current_user.id)
        .order_by(models.UploadedFile.uploaded_at.desc())
        .first()
    )

    if not file_record:
        return {"has_data": False}

    rows = parse_file(file_record.filepath)

    if not rows:
        return {"has_data": False}

    enriched_rows = predict(rows)

    summary = build_summary(enriched_rows)

    return {
        "has_data": True,
        "filename": file_record.filename,
        "total_transactions": len(enriched_rows),
        "rows": enriched_rows,
        "summary": summary,
    }
