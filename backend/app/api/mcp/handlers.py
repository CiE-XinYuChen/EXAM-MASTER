"""
MCP Tool Handlers - 工具处理函数实现
每个MCP工具对应一个处理函数，负责执行具体的业务逻辑
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.question_models_v2 import QuestionV2, QuestionBankV2, QuestionType
from app.models.user_practice import (
    PracticeSession, UserAnswerRecord, UserFavorite, UserWrongQuestion,
    PracticeMode, SessionStatus
)
from app.models.activation import UserBankAccess
from app.models.user_statistics import UserBankStatistics
from datetime import datetime
import uuid


# ==================== Helper Functions ====================

def check_bank_access(db: Session, user_id: int, bank_id: str) -> bool:
    """检查用户是否有权限访问题库"""
    access = db.query(UserBankAccess).filter(
        and_(
            UserBankAccess.user_id == user_id,
            UserBankAccess.bank_id == bank_id,
            UserBankAccess.is_active == True
        )
    ).first()

    if not access:
        return False

    if access.is_expired():
        return False

    return True


def get_accessible_banks(db: Session, user_id: int) -> List[str]:
    """获取用户有权限访问的所有题库ID"""
    accesses = db.query(UserBankAccess).filter(
        and_(
            UserBankAccess.user_id == user_id,
            UserBankAccess.is_active == True
        )
    ).all()

    bank_ids = []
    for access in accesses:
        if not access.is_expired():
            bank_ids.append(access.bank_id)

    return bank_ids


def format_question_for_practice(question: QuestionV2, include_answer: bool = False) -> Dict[str, Any]:
    """格式化题目数据用于答题"""
    data = {
        "id": question.id,
        "bank_id": question.bank_id,
        "type": question.type.value,
        "stem": question.stem,
        "options": question.options,
        "difficulty": question.difficulty.value if question.difficulty else None,
        "tags": question.tags,
        "has_image": question.has_image,
        "has_video": question.has_video,
        "has_audio": question.has_audio
    }

    if include_answer:
        data["correct_answer"] = question.correct_answer
        data["explanation"] = question.explanation

    return data


# ==================== Tool Handlers ====================

async def handle_get_question_banks(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """获取题库列表"""
    user_id = params["user_id"]
    include_stats = params.get("include_stats", False)

    # 获取有权限的题库ID
    bank_ids = get_accessible_banks(qbank_db, user_id)

    if not bank_ids:
        return {
            "success": True,
            "banks": [],
            "message": "用户暂无可访问的题库"
        }

    # 获取题库信息
    banks = qbank_db.query(QuestionBankV2).filter(
        QuestionBankV2.id.in_(bank_ids)
    ).all()

    result_banks = []
    for bank in banks:
        bank_data = {
            "id": bank.id,
            "name": bank.name,
            "description": bank.description,
            "category": bank.category,
            "tags": bank.tags
        }

        if include_stats:
            # 获取统计信息
            stats = qbank_db.query(UserBankStatistics).filter(
                and_(
                    UserBankStatistics.user_id == user_id,
                    UserBankStatistics.bank_id == bank.id
                )
            ).first()

            if stats:
                bank_data["statistics"] = {
                    "total_questions": stats.total_questions,
                    "practiced_questions": stats.practiced_questions,
                    "correct_count": stats.correct_count,
                    "accuracy_rate": stats.accuracy_rate
                }
            else:
                total_q = qbank_db.query(func.count(QuestionV2.id)).filter(
                    QuestionV2.bank_id == bank.id
                ).scalar() or 0
                bank_data["statistics"] = {
                    "total_questions": total_q,
                    "practiced_questions": 0,
                    "correct_count": 0,
                    "accuracy_rate": 0.0
                }

        result_banks.append(bank_data)

    return {
        "success": True,
        "banks": result_banks,
        "total": len(result_banks)
    }


async def handle_get_questions(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """获取题目列表"""
    user_id = params["user_id"]
    bank_id = params["bank_id"]
    question_types = params.get("question_types", [])
    difficulty = params.get("difficulty")
    mode = params.get("mode", "all")
    search = params.get("search")
    limit = params.get("limit", 20)

    # 检查权限
    if not check_bank_access(qbank_db, user_id, bank_id):
        return {
            "success": False,
            "error": "您没有访问该题库的权限"
        }

    # 根据模式获取题目
    if mode == "wrong_only":
        # 只获取错题
        wrong_q_ids = qbank_db.query(UserWrongQuestion.question_id).filter(
            and_(
                UserWrongQuestion.user_id == user_id,
                UserWrongQuestion.bank_id == bank_id,
                UserWrongQuestion.corrected == False
            )
        ).all()
        question_ids = [q[0] for q in wrong_q_ids]

        query = qbank_db.query(QuestionV2).filter(
            QuestionV2.id.in_(question_ids)
        )

    elif mode == "favorite_only":
        # 只获取收藏
        fav_q_ids = qbank_db.query(UserFavorite.question_id).filter(
            and_(
                UserFavorite.user_id == user_id,
                UserFavorite.bank_id == bank_id
            )
        ).all()
        question_ids = [q[0] for q in fav_q_ids]

        query = qbank_db.query(QuestionV2).filter(
            QuestionV2.id.in_(question_ids)
        )

    elif mode == "unpracticed":
        # 未练习的题目
        practiced_q_ids = qbank_db.query(UserAnswerRecord.question_id).filter(
            and_(
                UserAnswerRecord.user_id == user_id,
                UserAnswerRecord.bank_id == bank_id
            )
        ).distinct().all()
        practiced_ids = [q[0] for q in practiced_q_ids]

        query = qbank_db.query(QuestionV2).filter(
            and_(
                QuestionV2.bank_id == bank_id,
                ~QuestionV2.id.in_(practiced_ids) if practiced_ids else True
            )
        )

    else:
        # 所有题目
        query = qbank_db.query(QuestionV2).filter(
            QuestionV2.bank_id == bank_id
        )

    # 应用筛选
    if question_types:
        query = query.filter(QuestionV2.type.in_(question_types))
    if difficulty:
        query = query.filter(QuestionV2.difficulty == difficulty)
    if search:
        query = query.filter(QuestionV2.stem.contains(search))

    # 限制数量
    questions = query.limit(limit).all()

    # 格式化题目（不包含答案）
    result_questions = [format_question_for_practice(q, include_answer=False) for q in questions]

    return {
        "success": True,
        "questions": result_questions,
        "total": len(result_questions)
    }


async def handle_get_question_detail(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """获取题目详情"""
    user_id = params["user_id"]
    question_id = params["question_id"]
    include_history = params.get("include_history", False)

    # 获取题目
    question = qbank_db.query(QuestionV2).filter(
        QuestionV2.id == question_id
    ).first()

    if not question:
        return {
            "success": False,
            "error": "题目不存在"
        }

    # 检查权限
    if not check_bank_access(qbank_db, user_id, question.bank_id):
        return {
            "success": False,
            "error": "您没有访问该题库的权限"
        }

    # 格式化题目
    result = format_question_for_practice(question, include_answer=False)

    # 添加用户相关信息
    # 是否收藏
    is_favorite = qbank_db.query(UserFavorite).filter(
        and_(
            UserFavorite.user_id == user_id,
            UserFavorite.question_id == question_id
        )
    ).first() is not None

    # 是否在错题本
    wrong_q = qbank_db.query(UserWrongQuestion).filter(
        and_(
            UserWrongQuestion.user_id == user_id,
            UserWrongQuestion.question_id == question_id
        )
    ).first()

    result["is_favorite"] = is_favorite
    result["is_in_wrong_book"] = wrong_q is not None
    result["error_count"] = wrong_q.error_count if wrong_q else 0

    if include_history:
        # 获取答题历史
        records = qbank_db.query(UserAnswerRecord).filter(
            and_(
                UserAnswerRecord.user_id == user_id,
                UserAnswerRecord.question_id == question_id
            )
        ).order_by(UserAnswerRecord.created_at.desc()).limit(5).all()

        result["answer_history"] = [
            {
                "user_answer": r.user_answer,
                "is_correct": r.is_correct,
                "time_spent": r.time_spent,
                "created_at": r.created_at.isoformat()
            }
            for r in records
        ]

    return {
        "success": True,
        "question": result
    }


async def handle_submit_answer(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """提交答案"""
    user_id = params["user_id"]
    question_id = params["question_id"]
    session_id = params.get("session_id")
    user_answer = params["user_answer"]
    time_spent = params.get("time_spent")

    # 获取题目
    question = qbank_db.query(QuestionV2).filter(
        QuestionV2.id == question_id
    ).first()

    if not question:
        return {
            "success": False,
            "error": "题目不存在"
        }

    # 判断答案是否正确
    is_correct = False
    correct_answer = question.correct_answer or {}

    if question.type == QuestionType.single:
        is_correct = user_answer.get("answer") == correct_answer.get("answer")
    elif question.type == QuestionType.multiple:
        user_ans = set(user_answer.get("answers", []))
        correct_ans = set(correct_answer.get("answers", []))
        is_correct = user_ans == correct_ans
    elif question.type == QuestionType.judge:
        is_correct = user_answer.get("answer") == correct_answer.get("answer")

    # 创建答题记录
    record = UserAnswerRecord(
        id=str(uuid.uuid4()),
        user_id=user_id,
        question_id=question_id,
        session_id=session_id,
        bank_id=question.bank_id,
        user_answer=user_answer,
        is_correct=is_correct,
        time_spent=time_spent,
        question_snapshot={
            "type": question.type.value,
            "stem": question.stem,
            "options": question.options
        },
        correct_answer=correct_answer,
        created_at=datetime.utcnow()
    )

    qbank_db.add(record)

    # 更新错题本
    if not is_correct:
        wrong_q = qbank_db.query(UserWrongQuestion).filter(
            and_(
                UserWrongQuestion.user_id == user_id,
                UserWrongQuestion.question_id == question_id
            )
        ).first()

        if wrong_q:
            wrong_q.error_count += 1
            wrong_q.last_error_answer = user_answer
            wrong_q.last_error_at = datetime.utcnow()
            wrong_q.corrected = False
        else:
            wrong_q = UserWrongQuestion(
                id=str(uuid.uuid4()),
                user_id=user_id,
                question_id=question_id,
                bank_id=question.bank_id,
                error_count=1,
                last_error_answer=user_answer,
                corrected=False,
                first_error_at=datetime.utcnow(),
                last_error_at=datetime.utcnow()
            )
            qbank_db.add(wrong_q)
    else:
        # 如果答对了，标记错题为已订正
        wrong_q = qbank_db.query(UserWrongQuestion).filter(
            and_(
                UserWrongQuestion.user_id == user_id,
                UserWrongQuestion.question_id == question_id
            )
        ).first()

        if wrong_q and not wrong_q.corrected:
            wrong_q.corrected = True
            wrong_q.corrected_at = datetime.utcnow()

    # 更新会话统计（如果有）
    if session_id:
        session = qbank_db.query(PracticeSession).filter(
            PracticeSession.id == session_id
        ).first()

        if session:
            session.completed_count += 1
            if is_correct:
                session.correct_count += 1
            session.last_activity_at = datetime.utcnow()

    qbank_db.commit()

    return {
        "success": True,
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "explanation": question.explanation,
        "time_spent": time_spent,
        "record_id": record.id
    }


async def handle_get_wrong_questions(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """获取错题列表"""
    user_id = params["user_id"]
    bank_id = params.get("bank_id")
    corrected = params.get("corrected")
    min_error_count = params.get("min_error_count")
    limit = params.get("limit", 20)

    query = qbank_db.query(UserWrongQuestion, QuestionV2).join(
        QuestionV2,
        UserWrongQuestion.question_id == QuestionV2.id
    ).filter(
        UserWrongQuestion.user_id == user_id
    )

    if bank_id:
        query = query.filter(UserWrongQuestion.bank_id == bank_id)
    if corrected is not None:
        query = query.filter(UserWrongQuestion.corrected == corrected)
    if min_error_count:
        query = query.filter(UserWrongQuestion.error_count >= min_error_count)

    query = query.order_by(UserWrongQuestion.error_count.desc())
    results = query.limit(limit).all()

    wrong_questions = []
    for wrong_q, question in results:
        q_data = format_question_for_practice(question, include_answer=False)
        q_data["error_count"] = wrong_q.error_count
        q_data["last_error_answer"] = wrong_q.last_error_answer
        q_data["corrected"] = wrong_q.corrected
        q_data["last_error_at"] = wrong_q.last_error_at.isoformat()
        wrong_questions.append(q_data)

    return {
        "success": True,
        "wrong_questions": wrong_questions,
        "total": len(wrong_questions)
    }


async def handle_search_questions(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """搜索题目"""
    user_id = params["user_id"]
    query_str = params["query"]
    search_in = params.get("search_in", ["stem", "options", "explanation", "tags"])
    bank_ids = params.get("bank_ids")
    limit = params.get("limit", 20)

    # 获取有权限的题库
    accessible_banks = get_accessible_banks(qbank_db, user_id)

    if bank_ids:
        # 筛选出用户有权限的题库
        bank_ids = [bid for bid in bank_ids if bid in accessible_banks]
    else:
        bank_ids = accessible_banks

    if not bank_ids:
        return {
            "success": True,
            "questions": [],
            "total": 0,
            "message": "没有可搜索的题库"
        }

    # 构建搜索查询
    query = qbank_db.query(QuestionV2).filter(
        QuestionV2.bank_id.in_(bank_ids)
    )

    # 根据搜索范围构建条件
    conditions = []
    if "stem" in search_in:
        conditions.append(QuestionV2.stem.contains(query_str))
    if "explanation" in search_in and query_str:
        conditions.append(QuestionV2.explanation.contains(query_str))

    if conditions:
        query = query.filter(or_(*conditions))

    questions = query.limit(limit).all()

    result_questions = [format_question_for_practice(q, include_answer=False) for q in questions]

    return {
        "success": True,
        "questions": result_questions,
        "total": len(result_questions)
    }


# 其他handler函数继续...
async def handle_get_user_statistics(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """获取用户统计"""
    user_id = params["user_id"]
    bank_id = params.get("bank_id")

    if bank_id:
        # 单个题库统计
        stats = qbank_db.query(UserBankStatistics).filter(
            and_(
                UserBankStatistics.user_id == user_id,
                UserBankStatistics.bank_id == bank_id
            )
        ).first()

        if not stats:
            return {
                "success": True,
                "statistics": None,
                "message": "该题库暂无统计数据"
            }

        return {
            "success": True,
            "statistics": {
                "bank_id": stats.bank_id,
                "total_questions": stats.total_questions,
                "practiced_questions": stats.practiced_questions,
                "correct_count": stats.correct_count,
                "wrong_count": stats.wrong_count,
                "accuracy_rate": stats.accuracy_rate,
                "favorite_count": stats.favorite_count,
                "wrong_questions_count": stats.wrong_questions_count,
                "total_time_spent": stats.total_time_spent
            }
        }
    else:
        # 所有题库统计汇总
        all_stats = qbank_db.query(UserBankStatistics).filter(
            UserBankStatistics.user_id == user_id
        ).all()

        total_practiced = sum(s.practiced_questions for s in all_stats)
        total_correct = sum(s.correct_count for s in all_stats)
        total_wrong = sum(s.wrong_count for s in all_stats)
        overall_accuracy = (total_correct / (total_correct + total_wrong) * 100) if (total_correct + total_wrong) > 0 else 0.0

        return {
            "success": True,
            "statistics": {
                "banks_accessed": len(all_stats),
                "total_practiced": total_practiced,
                "total_correct": total_correct,
                "total_wrong": total_wrong,
                "overall_accuracy_rate": overall_accuracy,
                "total_favorites": sum(s.favorite_count for s in all_stats),
                "total_wrong_questions": sum(s.wrong_questions_count for s in all_stats),
                "total_time_spent": sum(s.total_time_spent for s in all_stats)
            }
        }


async def handle_add_favorite(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """添加收藏"""
    user_id = params["user_id"]
    question_id = params["question_id"]
    note = params.get("note")

    # 检查是否已收藏
    existing = qbank_db.query(UserFavorite).filter(
        and_(
            UserFavorite.user_id == user_id,
            UserFavorite.question_id == question_id
        )
    ).first()

    if existing:
        return {
            "success": False,
            "error": "已经收藏过该题目"
        }

    # 获取题目（用于获取bank_id）
    question = qbank_db.query(QuestionV2).filter(
        QuestionV2.id == question_id
    ).first()

    if not question:
        return {
            "success": False,
            "error": "题目不存在"
        }

    # 创建收藏
    favorite = UserFavorite(
        id=str(uuid.uuid4()),
        user_id=user_id,
        question_id=question_id,
        bank_id=question.bank_id,
        note=note,
        created_at=datetime.utcnow()
    )

    qbank_db.add(favorite)
    qbank_db.commit()

    return {
        "success": True,
        "favorite_id": favorite.id,
        "message": "收藏成功"
    }


async def handle_get_favorites(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """获取收藏列表"""
    user_id = params["user_id"]
    bank_id = params.get("bank_id")
    limit = params.get("limit", 20)

    query = qbank_db.query(UserFavorite, QuestionV2).join(
        QuestionV2,
        UserFavorite.question_id == QuestionV2.id
    ).filter(
        UserFavorite.user_id == user_id
    )

    if bank_id:
        query = query.filter(UserFavorite.bank_id == bank_id)

    query = query.order_by(UserFavorite.created_at.desc())
    results = query.limit(limit).all()

    favorites = []
    for fav, question in results:
        q_data = format_question_for_practice(question, include_answer=False)
        q_data["favorite_id"] = fav.id
        q_data["note"] = fav.note
        q_data["favorited_at"] = fav.created_at.isoformat()
        favorites.append(q_data)

    return {
        "success": True,
        "favorites": favorites,
        "total": len(favorites)
    }


async def handle_create_practice_session(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """创建答题会话"""
    user_id = params["user_id"]
    bank_id = params["bank_id"]
    mode = params["mode"]
    question_types = params.get("question_types")
    difficulty = params.get("difficulty")

    # 检查权限
    if not check_bank_access(qbank_db, user_id, bank_id):
        return {
            "success": False,
            "error": "您没有访问该题库的权限"
        }

    # 获取题目列表（简化版，实际应该调用get_questions的逻辑）
    query = qbank_db.query(QuestionV2).filter(
        QuestionV2.bank_id == bank_id
    )

    if question_types:
        query = query.filter(QuestionV2.type.in_(question_types))
    if difficulty:
        query = query.filter(QuestionV2.difficulty == difficulty)

    questions = query.all()
    question_ids = [q.id for q in questions]

    # 创建会话
    session = PracticeSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        bank_id=bank_id,
        mode=PracticeMode[mode],
        question_types=question_types,
        difficulty=difficulty,
        total_questions=len(question_ids),
        question_ids=question_ids,
        current_index=0,
        completed_count=0,
        correct_count=0,
        status=SessionStatus.in_progress,
        started_at=datetime.utcnow()
    )

    qbank_db.add(session)
    qbank_db.commit()

    return {
        "success": True,
        "session_id": session.id,
        "total_questions": len(question_ids),
        "mode": mode,
        "message": "答题会话创建成功"
    }


async def handle_get_question_explanation(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """获取题目解析"""
    user_id = params["user_id"]
    question_id = params["question_id"]
    include_related = params.get("include_related", False)

    question = qbank_db.query(QuestionV2).filter(
        QuestionV2.id == question_id
    ).first()

    if not question:
        return {
            "success": False,
            "error": "题目不存在"
        }

    result = format_question_for_practice(question, include_answer=True)

    if include_related and question.tags:
        # 获取相关题目（同标签）
        related = qbank_db.query(QuestionV2).filter(
            and_(
                QuestionV2.bank_id == question.bank_id,
                QuestionV2.id != question_id
            )
        ).limit(5).all()

        result["related_questions"] = [
            {"id": q.id, "stem": q.stem[:100] + "..."} for q in related
        ]

    return {
        "success": True,
        "question": result
    }


async def handle_mark_wrong_question_corrected(params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """标记错题已订正"""
    user_id = params["user_id"]
    question_id = params["question_id"]

    wrong_q = qbank_db.query(UserWrongQuestion).filter(
        and_(
            UserWrongQuestion.user_id == user_id,
            UserWrongQuestion.question_id == question_id
        )
    ).first()

    if not wrong_q:
        return {
            "success": False,
            "error": "该题目不在错题本中"
        }

    wrong_q.corrected = True
    wrong_q.corrected_at = datetime.utcnow()
    qbank_db.commit()

    return {
        "success": True,
        "message": "已标记为订正"
    }


# ==================== Handler Registry ====================

HANDLER_MAP = {
    "get_question_banks": handle_get_question_banks,
    "get_questions": handle_get_questions,
    "get_question_detail": handle_get_question_detail,
    "submit_answer": handle_submit_answer,
    "get_wrong_questions": handle_get_wrong_questions,
    "search_questions": handle_search_questions,
    "get_user_statistics": handle_get_user_statistics,
    "add_favorite": handle_add_favorite,
    "get_favorites": handle_get_favorites,
    "create_practice_session": handle_create_practice_session,
    "get_question_explanation": handle_get_question_explanation,
    "mark_wrong_question_corrected": handle_mark_wrong_question_corrected
}


async def execute_tool(tool_name: str, params: Dict[str, Any], qbank_db: Session) -> Dict[str, Any]:
    """执行MCP工具"""
    if tool_name not in HANDLER_MAP:
        return {
            "success": False,
            "error": f"未知的工具: {tool_name}"
        }

    handler = HANDLER_MAP[tool_name]

    try:
        result = await handler(params, qbank_db)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"工具执行失败: {str(e)}"
        }
