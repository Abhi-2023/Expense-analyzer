import os
import uuid
from fastapi import UploadFile, HTTPException
from config import settings


ALLOWED_TYPES = ['text/csv', 'application/pdf',
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

def validate_file(file : UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail="Only CSV and PDF files are allowed"
        )

def save_file(file: UploadFile) -> tuple[str, str]:
    unique_filename = f'{uuid.uuid4()}_{file.filename}'
    filepath = os.path.join(settings.UPLOAD_DIR, unique_filename)
    with open(filepath, 'wb') as f:
        content = file.file.read()
        f.write(content)
        
    return unique_filename, filepath