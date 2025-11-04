"""
Wrong Questions API - 错题本管理
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime
import uuid

from app.core.database import get_qbank_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.models.user_practice import UserWrongQuestion
from app.models.question_models_v2 import QuestionV2, QuestionType
from app.schemas.wrong_questions_schemas import (
    WrongQuestionResponse,
    WrongQuestionWithDetailsResponse,
    WrongQuestionListResponse,
    WrongQuestionQuery,
    WrongQuestionCorrectRequest,
    WrongQuestionStatistics,
    WrongQuestionAnalysis
)

router = APIRouter()


# ==================== Wrong Question Management Endpoints ====================

@router.get("", response_model=WrongQuestionListResponse, tags=["❌ Wrong Questions"])
async def list_wrong_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=10000),
    bank_id: Optional[str] = None,
    question_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    corrected: Optional[bool] = None,
    min_error_count: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取错题列表"""

    # 基础查询 - join题目表
    query = db.query(UserWrongQuestion, QuestionV2).join(
        QuestionV2,
        UserWrongQuestion.question_id == QuestionV2.id
    ).filter(
        UserWrongQuestion.user_id == current_user.id
    )

    # 筛选条件
    if bank_id:
        query = query.filter(UserWrongQuestion.bank_id == bank_id)
    if question_type:
        query = query.filter(QuestionV2.type == question_type)
    if difficulty:
        query = query.filter(QuestionV2.difficulty == difficulty)
    if corrected is not None:
        query = query.filter(UserWrongQuestion.corrected == corrected)
    if min_error_count:
        query = query.filter(UserWrongQuestion.error_count >= min_error_count)
    if search:
        query = query.filter(QuestionV2.stem.contains(search))

    # 按错误次数倒序，然后按最后错误时间倒序
    query = query.order_by(
        desc(UserWrongQuestion.error_count),
        desc(UserWrongQuestion.last_error_at)
    )

    total = query.count()

    # 统计未订正数量
    uncorrected_count = db.query(func.count(UserWrongQuestion.id)).filter(
        and_(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.corrected == False
        )
    ).scalar() or 0

    results = query.offset(skip).limit(limit).all()

    # 构造响应
    wrong_questions_with_details = []
    for wrong_q, question in results:
        wrong_questions_with_details.append(WrongQuestionWithDetailsResponse(
            id=wrong_q.id,
            user_id=wrong_q.user_id,
            question_id=wrong_q.question_id,
            bank_id=wrong_q.bank_id,
            error_count=wrong_q.error_count,
            last_error_answer=wrong_q.last_error_answer,
            corrected=wrong_q.corrected,
            first_error_at=wrong_q.first_error_at,
            last_error_at=wrong_q.last_error_at,
            corrected_at=wrong_q.corrected_at,
            question_number=question.number if hasattr(question, 'number') else None,
            question_type=question.type.value,
            question_stem=question.stem,
            question_difficulty=question.difficulty.value if question.difficulty else None,
            question_tags=question.tags,
            has_image=question.has_image if hasattr(question, 'has_image') else False,
            has_video=question.has_video if hasattr(question, 'has_video') else False,
            has_audio=question.has_audio if hasattr(question, 'has_audio') else False,
            correct_answer=question.correct_answer if hasattr(question, 'correct_answer') else None
        ))

    return WrongQuestionListResponse(
        wrong_questions=wrong_questions_with_details,
        total=total,
        uncorrected_count=uncorrected_count
    )


@router.get("/{wrong_question_id}", response_model=WrongQuestionWithDetailsResponse, tags=["❌ Wrong Questions"])
async def get_wrong_question(
    wrong_question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取错题详情"""

    result = db.query(UserWrongQuestion, QuestionV2).join(
        QuestionV2,
        UserWrongQuestion.question_id == QuestionV2.id
    ).filter(
        and_(
            UserWrongQuestion.id == wrong_question_id,
            UserWrongQuestion.user_id == current_user.id
        )
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="错题不存在"
        )

    wrong_q, question = result

    return WrongQuestionWithDetailsResponse(
        id=wrong_q.id,
        user_id=wrong_q.user_id,
        question_id=wrong_q.question_id,
        bank_id=wrong_q.bank_id,
        error_count=wrong_q.error_count,
        last_error_answer=wrong_q.last_error_answer,
        corrected=wrong_q.corrected,
        first_error_at=wrong_q.first_error_at,
        last_error_at=wrong_q.last_error_at,
        corrected_at=wrong_q.corrected_at,
        question_type=question.type.value,
        question_stem=question.stem,
        question_difficulty=question.difficulty.value if question.difficulty else None,
        question_tags=question.tags,
        has_image=question.has_image,
        has_video=question.has_video,
        has_audio=question.has_audio,
        correct_answer=question.correct_answer
    )


@router.put("/{wrong_question_id}/correct", response_model=WrongQuestionResponse, tags=["❌ Wrong Questions"])
async def mark_as_corrected(
    wrong_question_id: str,
    correct_request: WrongQuestionCorrectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """标记错题为已订正/未订正"""

    wrong_q = db.query(UserWrongQuestion).filter(
        and_(
            UserWrongQuestion.id == wrong_question_id,
            UserWrongQuestion.user_id == current_user.id
        )
    ).first()

    if not wrong_q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="错题不存在"
        )

    # 更新订正状态
    wrong_q.corrected = correct_request.corrected
    if correct_request.corrected:
        wrong_q.corrected_at = datetime.utcnow()
    else:
        wrong_q.corrected_at = None

    db.commit()
    db.refresh(wrong_q)

    return wrong_q


@router.delete("/{wrong_question_id}", tags=["❌ Wrong Questions"])
async def delete_wrong_question(
    wrong_question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """从错题本删除"""

    wrong_q = db.query(UserWrongQuestion).filter(
        and_(
            UserWrongQuestion.id == wrong_question_id,
            UserWrongQuestion.user_id == current_user.id
        )
    ).first()

    if not wrong_q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="错题不存在"
        )

    db.delete(wrong_q)
    db.commit()

    return {"success": True, "message": "已从错题本删除"}


@router.delete("/question/{question_id}", tags=["❌ Wrong Questions"])
async def delete_wrong_question_by_question_id(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """通过题目ID从错题本删除"""

    wrong_q = db.query(UserWrongQuestion).filter(
        and_(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.question_id == question_id
        )
    ).first()

    if not wrong_q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该题目不在错题本中"
        )

    db.delete(wrong_q)
    db.commit()

    return {"success": True, "message": "已从错题本删除"}


# ==================== Statistics Endpoints ====================

@router.get("/stats/overview", response_model=WrongQuestionStatistics, tags=["❌ Wrong Questions"])
async def get_wrong_question_statistics(
    bank_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取错题统计"""

    query = db.query(UserWrongQuestion, QuestionV2).join(
        QuestionV2,
        UserWrongQuestion.question_id == QuestionV2.id
    ).filter(
        UserWrongQuestion.user_id == current_user.id
    )

    if bank_id:
        query = query.filter(UserWrongQuestion.bank_id == bank_id)

    results = query.all()

    total_wrong_questions = len(results)
    uncorrected_count = sum(1 for wq, _ in results if not wq.corrected)
    corrected_count = total_wrong_questions - uncorrected_count

    # 错误次数分布
    error_distribution = {}
    for wq, _ in results:
        count_key = str(wq.error_count)
        error_distribution[count_key] = error_distribution.get(count_key, 0) + 1

    # 题型分布
    type_distribution = {}
    for wq, q in results:
        q_type = q.type.value
        type_distribution[q_type] = type_distribution.get(q_type, 0) + 1

    # 难度分布
    difficulty_distribution = {}
    for wq, q in results:
        if q.difficulty:
            diff = q.difficulty.value
            difficulty_distribution[diff] = difficulty_distribution.get(diff, 0) + 1

    # 找出错误最多的题型和难度
    most_wrong_type = max(type_distribution.items(), key=lambda x: x[1])[0] if type_distribution else None
    most_wrong_difficulty = max(difficulty_distribution.items(), key=lambda x: x[1])[0] if difficulty_distribution else None

    return WrongQuestionStatistics(
        total_wrong_questions=total_wrong_questions,
        uncorrected_count=uncorrected_count,
        corrected_count=corrected_count,
        most_wrong_type=most_wrong_type,
        most_wrong_difficulty=most_wrong_difficulty,
        error_distribution=error_distribution,
        type_distribution=type_distribution,
        difficulty_distribution=difficulty_distribution
    )


@router.get("/stats/count", tags=["❌ Wrong Questions"])
async def get_wrong_question_count(
    bank_id: Optional[str] = None,
    corrected: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取错题数量"""

    query = db.query(func.count(UserWrongQuestion.id)).filter(
        UserWrongQuestion.user_id == current_user.id
    )

    if bank_id:
        query = query.filter(UserWrongQuestion.bank_id == bank_id)
    if corrected is not None:
        query = query.filter(UserWrongQuestion.corrected == corrected)

    count = query.scalar() or 0

    return {"total": count, "bank_id": bank_id, "corrected": corrected}


# ==================== Analysis Endpoints ====================

@router.get("/analysis/{question_id}", response_model=WrongQuestionAnalysis, tags=["❌ Wrong Questions"])
async def analyze_wrong_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """分析单个错题（包含常见错误）"""

    # 获取错题记录
    wrong_q = db.query(UserWrongQuestion).filter(
        and_(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.question_id == question_id
        )
    ).first()

    if not wrong_q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该题目不在错题本中"
        )

    # 获取题目
    question = db.query(QuestionV2).filter(
        QuestionV2.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    # 获取该用户所有错误答案（从答题记录中）
    from app.models.user_practice import UserAnswerRecord

    error_records = db.query(UserAnswerRecord).filter(
        and_(
            UserAnswerRecord.user_id == current_user.id,
            UserAnswerRecord.question_id == question_id,
            UserAnswerRecord.is_correct == False
        )
    ).order_by(desc(UserAnswerRecord.created_at)).all()

    # 统计常见错误
    common_mistakes = []
    answer_counts = {}
    for record in error_records:
        answer_str = str(record.user_answer)
        answer_counts[answer_str] = answer_counts.get(answer_str, 0) + 1

    for answer_str, count in sorted(answer_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
        common_mistakes.append({
            "answer": eval(answer_str) if answer_str.startswith("{") else answer_str,
            "count": count
        })

    return WrongQuestionAnalysis(
        question_id=question.id,
        question_stem=question.stem,
        question_type=question.type.value,
        error_count=wrong_q.error_count,
        common_mistakes=common_mistakes,
        correct_answer=question.correct_answer or {},
        explanation=question.explanation,
        related_knowledge=question.tags  # 用标签作为相关知识点
    )


# ==================== Batch Operations ====================

@router.post("/batch/correct", tags=["❌ Wrong Questions"])
async def batch_mark_corrected(
    question_ids: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """批量标记为已订正"""

    wrong_questions = db.query(UserWrongQuestion).filter(
        and_(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.question_id.in_(question_ids)
        )
    ).all()

    corrected_count = 0
    for wq in wrong_questions:
        if not wq.corrected:
            wq.corrected = True
            wq.corrected_at = datetime.utcnow()
            corrected_count += 1

    db.commit()

    return {
        "success": True,
        "message": f"已标记 {corrected_count} 道题为已订正",
        "corrected_count": corrected_count
    }


@router.delete("/batch/delete", tags=["❌ Wrong Questions"])
async def batch_delete_wrong_questions(
    question_ids: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """批量从错题本删除"""

    deleted_count = db.query(UserWrongQuestion).filter(
        and_(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.question_id.in_(question_ids)
        )
    ).delete(synchronize_session=False)

    db.commit()

    return {
        "success": True,
        "message": f"已从错题本删除 {deleted_count} 道题",
        "deleted_count": deleted_count
    }
