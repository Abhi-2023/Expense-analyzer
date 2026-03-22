from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from db.models import User, UploadedFile
from utils.jwt import get_current_user
from utils.file_utils import validate_file, save_file

router = APIRouter(prefix="/api", tags=["upload"])

@router.post('/upload')
def upload_file(file:UploadFile = File(...), db: Session=Depends(get_db),
                current_user: User = Depends(get_current_user)):
    validate_file(file)
    
    unique_filename, filepath = save_file(file)
    
    uploaded_file = models.UploadedFile(user_id = current_user.id,
                                 filename=unique_filename, filepath=filepath)
    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)
    
    return{
        "file_id" : uploaded_file.id,
        "filename": uploaded_file.filename,
        "message": "File uploaded successfully"
    }
    
@router.get("/preview/{file_id}")
def preview_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_record = db.query(models.UploadedFile).filter(
        models.UploadedFile.id == file_id,
        models.UploadedFile.user_id == current_user.id
    ).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    from ml.file_parser import parse_file
    rows = parse_file(file_record.filepath)

    return {"rows": rows}