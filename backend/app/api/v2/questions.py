from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_qbank_db
from app.core.security import get_admin_user_from_session
from app.services.question_bank_service import QuestionBankService

router = APIRouter()

@router.post("/qbanks/{bank_id}/renumber", tags=["📚 Admin - Question Banks"])
async def renumber_questions(
    bank_id: str,
    current_admin = Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """
    自动重新生成题号
    按题目创建时间顺序，为题库中的所有题目重新分配连续的序号
    """
    service = QuestionBankService(db)
    updated_count = service.renumber_questions(bank_id)
    
    return {
        "success": True, 
        "message": f"已重新编号，共更新 {updated_count} 道题目",
        "updated_count": updated_count
    }
