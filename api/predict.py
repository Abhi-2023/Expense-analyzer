from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from utils.jwt import get_current_user
from ml.file_parser import parse_file
from ml.predict_pipeline import predict, build_summary
from schemas.prediction import PredictRequest

router = APIRouter(prefix='/api', tags=['predict'])

@router.post('/predict')
def predict_transactions(
    request: PredictRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    file_record = db.query(models.UploadedFile).filter(
        models.UploadedFile.id == request.file_id,
        models.UploadedFile.user_id == current_user.id
    ).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    rows = parse_file(file_record.filepath)

    if not rows:
        raise HTTPException(status_code=400, detail="No valid rows found in file")

    enriched_rows = predict(rows)

    summary = build_summary(enriched_rows)

    return {
        "file_id": request.file_id,
        "total_transactions": len(enriched_rows),
        "rows": enriched_rows,
        "summary": summary
    }
