import numpy as np
import joblib
import os
from ml.preprocessor import text_preprocessing
from ml.embedder import encode

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTEFACTS_DIR = os.path.join(BASE_DIR, "ml", "artefacts")

model = joblib.load(os.path.join(ARTEFACTS_DIR, "model.pkl"))
label_encoder = joblib.load(os.path.join(ARTEFACTS_DIR, "label_encoder.pkl"))
scaler = joblib.load(os.path.join(ARTEFACTS_DIR, "scaler.pkl"))


def predict(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    descriptions = [text_preprocessing(row["description"]) for row in rows]
    amount = np.array([row["amount"] for row in rows]).reshape(-1, 1)

    embeddings = encode(descriptions)
    log_amounts = np.log1p(amount)
    scaled_amounts = scaler.transform(log_amounts)
    X = np.hstack([embeddings, scaled_amounts])
    X= np.array(X)
    predicted_labels = model.predict(X)
    predicted_proba = model.predict_proba(X)

    categories = label_encoder.inverse_transform(predicted_labels)
    confidence_score = predicted_proba.max(axis=1)

    results = []
    results.extend(
        {
            "description": row["description"],
            "amount": row["amount"],
            "account_number": row.get("account_number", "N/A"),
            "category": categories[i],
            "confidence_score": round(float(confidence_score[i]), 2),
        }
        for i, row in enumerate(rows)
    )
    return results


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from utils.jwt import get_current_user
from ml.file_parser import parse_file
from ml.predict_pipeline import predict

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/dashboard/data")
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    file_record = db.query(models.UploadedFile).filter(
        models.UploadedFile.user_id == current_user.id
    ).order_by(models.UploadedFile.uploaded_at.desc()).first()

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
        "rows": enriched_rows,
        "summary": summary
    }


def build_summary(rows: list[dict]) -> dict:
    total_spend = sum(r["amount"] for r in rows)

    spend_by_category = {}
    for r in rows:
        cat = r["category"]
        spend_by_category[cat] = round(
            spend_by_category.get(cat, 0) + r["amount"], 2
        )

    spend_by_account = {}
    for r in rows:
        acc = r["account_number"]
        spend_by_account[acc] = round(
            spend_by_account.get(acc, 0) + r["amount"], 2
        )

    avg_confidence = round(
        sum(r["confidence_score"] for r in rows) / len(rows), 2
    )

    top_category = max(spend_by_category, key=spend_by_category.get)

    return {
        "total_spend": round(total_spend, 2),
        "avg_per_transaction": round(total_spend / len(rows), 2),
        "top_category": top_category,
        "avg_confidence_score": avg_confidence,
        "spend_by_category": spend_by_category,
        "spend_by_account": spend_by_account
    }