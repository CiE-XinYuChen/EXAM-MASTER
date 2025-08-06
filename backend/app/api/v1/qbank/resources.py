"""
Resource management endpoints for file upload and download
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
import os
import shutil
from pathlib import Path
import mimetypes
from app.core.database import get_qbank_db, get_main_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.question_models import Question, QuestionOption, QuestionResource
from app.models.user_models import User, UserBankPermission
from app.schemas.question_schemas import ResourceResponse

router = APIRouter()

# Allowed file extensions and their types
ALLOWED_EXTENSIONS = {
    'image': {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp'},
    'video': {'.mp4', '.webm', '.avi', '.mov', '.mkv'},
    'audio': {'.mp3', '.wav', '.ogg', '.m4a', '.flac'},
    'document': {'.pdf', '.doc', '.docx', '.txt', '.tex', '.md'}
}

# Maximum file sizes (in bytes)
MAX_FILE_SIZES = {
    'image': 10 * 1024 * 1024,      # 10MB
    'video': 100 * 1024 * 1024,     # 100MB
    'audio': 20 * 1024 * 1024,      # 20MB
    'document': 20 * 1024 * 1024    # 20MB
}


def get_file_type(filename: str) -> Optional[str]:
    """Determine file type from extension"""
    ext = Path(filename).suffix.lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return None


def validate_file(file: UploadFile) -> str:
    """Validate uploaded file"""
    # Check file extension
    file_type = get_file_type(file.filename)
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed extensions: {', '.join(sum(ALLOWED_EXTENSIONS.values(), set()))}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Move to end of file
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZES[file_type]:
        max_size_mb = MAX_FILE_SIZES[file_type] / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size for {file_type} is {max_size_mb}MB"
        )
    
    return file_type


def check_question_write_permission(
    question_id: str,
    user: User,
    qbank_db: Session,
    main_db: Session
) -> Question:
    """Check if user has write permission for a question"""
    question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    if user.role != "admin":
        perm = main_db.query(UserBankPermission).filter(
            UserBankPermission.user_id == user.id,
            UserBankPermission.bank_id == question.bank_id
        ).first()
        
        if not perm or perm.permission not in ["write", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to modify this question"
            )
    
    return question


@router.post("/upload", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_resource(
    file: UploadFile = File(...),
    question_id: str = Form(...),
    option_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Upload a resource file for a question or option"""
    # Validate file
    file_type = validate_file(file)
    
    # Check permission
    question = check_question_write_permission(question_id, current_user, qbank_db, main_db)
    
    # Validate option if provided
    if option_id:
        option = qbank_db.query(QuestionOption).filter(
            QuestionOption.id == option_id,
            QuestionOption.question_id == question_id
        ).first()
        
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Option not found or doesn't belong to this question"
            )
    
    # Generate unique filename
    resource_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    safe_filename = f"{resource_id}{file_ext}"
    
    # Create directory structure
    resource_dir = settings.resource_dir / file_type / question.bank_id
    resource_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = resource_dir / safe_filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Get file info
    file_size = file_path.stat().st_size
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    # Create database record
    resource = QuestionResource(
        id=resource_id,
        question_id=question_id,
        option_id=option_id,
        resource_type=file_type,
        file_path=str(file_path.relative_to(settings.resource_dir)),
        file_name=file.filename,
        file_size=file_size,
        mime_type=mime_type,
        meta_data={"description": description} if description else None
    )
    
    qbank_db.add(resource)
    qbank_db.commit()
    qbank_db.refresh(resource)
    
    # Add URL for accessing the resource
    resource.url = f"/api/v1/qbank/resources/{resource_id}/download"
    
    return resource


@router.get("/{resource_id}/download")
async def download_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Download a resource file"""
    # Get resource
    resource = qbank_db.query(QuestionResource).filter(
        QuestionResource.id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Check permission (read permission is enough for download)
    question = qbank_db.query(Question).filter(
        Question.id == resource.question_id
    ).first()
    
    if current_user.role != "admin":
        perm = main_db.query(UserBankPermission).filter(
            UserBankPermission.user_id == current_user.id,
            UserBankPermission.bank_id == question.bank_id
        ).first()
        
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to access this resource"
            )
    
    # Get file path
    file_path = settings.resource_dir / resource.file_path
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource file not found on disk"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=resource.file_name,
        media_type=resource.mime_type
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource_info(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Get resource information"""
    # Get resource
    resource = qbank_db.query(QuestionResource).filter(
        QuestionResource.id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Check permission
    question = qbank_db.query(Question).filter(
        Question.id == resource.question_id
    ).first()
    
    if current_user.role != "admin":
        perm = main_db.query(UserBankPermission).filter(
            UserBankPermission.user_id == current_user.id,
            UserBankPermission.bank_id == question.bank_id
        ).first()
        
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to access this resource"
            )
    
    # Add URL
    resource.url = f"/api/v1/qbank/resources/{resource_id}/download"
    
    return resource


@router.delete("/{resource_id}", response_model=dict)
async def delete_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Delete a resource"""
    # Get resource
    resource = qbank_db.query(QuestionResource).filter(
        QuestionResource.id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Check permission
    question = check_question_write_permission(
        resource.question_id, 
        current_user, 
        qbank_db, 
        main_db
    )
    
    # Delete file from disk
    file_path = settings.resource_dir / resource.file_path
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Error deleting file: {e}")
    
    # Delete from database
    qbank_db.delete(resource)
    qbank_db.commit()
    
    return {"message": "Resource deleted successfully"}


@router.post("/batch-upload", response_model=List[ResourceResponse], status_code=status.HTTP_201_CREATED)
async def batch_upload_resources(
    files: List[UploadFile] = File(...),
    question_id: str = Form(...),
    option_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Upload multiple resources at once"""
    # Check permission once
    question = check_question_write_permission(question_id, current_user, qbank_db, main_db)
    
    # Validate option if provided
    if option_id:
        option = qbank_db.query(QuestionOption).filter(
            QuestionOption.id == option_id,
            QuestionOption.question_id == question_id
        ).first()
        
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Option not found or doesn't belong to this question"
            )
    
    uploaded_resources = []
    errors = []
    
    for file in files:
        try:
            # Validate file
            file_type = validate_file(file)
            
            # Generate unique filename
            resource_id = str(uuid.uuid4())
            file_ext = Path(file.filename).suffix
            safe_filename = f"{resource_id}{file_ext}"
            
            # Create directory structure
            resource_dir = settings.resource_dir / file_type / question.bank_id
            resource_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = resource_dir / safe_filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file info
            file_size = file_path.stat().st_size
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Create database record
            resource = QuestionResource(
                id=resource_id,
                question_id=question_id,
                option_id=option_id,
                resource_type=file_type,
                file_path=str(file_path.relative_to(settings.resource_dir)),
                file_name=file.filename,
                file_size=file_size,
                mime_type=mime_type
            )
            
            qbank_db.add(resource)
            resource.url = f"/api/v1/qbank/resources/{resource_id}/download"
            uploaded_resources.append(resource)
            
        except HTTPException as e:
            errors.append(f"{file.filename}: {e.detail}")
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    if uploaded_resources:
        qbank_db.commit()
        for resource in uploaded_resources:
            qbank_db.refresh(resource)
    
    if errors:
        # Return partial success with errors
        return HTTPException(
            status_code=status.HTTP_207_MULTI_STATUS,
            detail={
                "uploaded": len(uploaded_resources),
                "failed": len(errors),
                "errors": errors,
                "resources": uploaded_resources
            }
        )
    
    return uploaded_resources