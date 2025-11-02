"""
Statistics API - 用户统计数据
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, date, timedelta
import uuid

from app.core.database import get_main_db, get_qbank_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.models.user_statistics import UserDailyStatistics, UserBankStatistics
from app.models.user_practice import UserAnswerRecord, PracticeSession, UserFavorite, UserWrongQuestion
from app.models.question_models_v2 import QuestionBankV2, QuestionV2
from app.schemas.statistics_schemas import (
    DailyStatisticsResponse,
    DailyStatisticsListResponse,
    BankStatisticsResponse,
    BankStatisticsListResponse,
    OverviewStatistics,
    DetailedStatistics,
    StatisticsQuery
)

router = APIRouter()


# ==================== Helper Functions ====================

def update_daily_statistics(main_db: Session, user_id: int, practice_date: date):
    """更新每日统计（在main.db中）"""

    # 查找或创建当天的统计记录
    stats = main_db.query(UserDailyStatistics).filter(
        and_(
            UserDailyStatistics.user_id == user_id,
            func.date(UserDailyStatistics.date) == practice_date
        )
    ).first()

    if not stats:
        stats = UserDailyStatistics(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=datetime.combine(practice_date, datetime.min.time())
        )
        main_db.add(stats)

    return stats


def update_bank_statistics(qbank_db: Session, user_id: int, bank_id: str):
    """更新分题库统计（在question_bank.db中）"""

    # 查找或创建该题库的统计记录
    stats = qbank_db.query(UserBankStatistics).filter(
        and_(
            UserBankStatistics.user_id == user_id,
            UserBankStatistics.bank_id == bank_id
        )
    ).first()

    if not stats:
        # 获取题库总题数
        total_questions = qbank_db.query(func.count(QuestionV2.id)).filter(
            QuestionV2.bank_id == bank_id
        ).scalar() or 0

        stats = UserBankStatistics(
            id=str(uuid.uuid4()),
            user_id=user_id,
            bank_id=bank_id,
            total_questions=total_questions,
            first_practiced_at=datetime.utcnow()
        )
        qbank_db.add(stats)

    return stats


# ==================== Daily Statistics Endpoints ====================

@router.get("/daily", response_model=DailyStatisticsListResponse, tags=["📊 Statistics"])
async def get_daily_statistics(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    main_db: Session = Depends(get_main_db)
):
    """获取每日统计"""

    query = main_db.query(UserDailyStatistics).filter(
        UserDailyStatistics.user_id == current_user.id
    )

    # 日期范围筛选
    if start_date:
        query = query.filter(func.date(UserDailyStatistics.date) >= start_date)
    if end_date:
        query = query.filter(func.date(UserDailyStatistics.date) <= end_date)
    else:
        # 默认显示最近30天
        default_end = date.today()
        default_start = default_end - timedelta(days=30)
        if not start_date:
            query = query.filter(func.date(UserDailyStatistics.date) >= default_start)

    # 按日期倒序
    query = query.order_by(desc(UserDailyStatistics.date))

    total_days = query.count()
    statistics = query.offset(skip).limit(limit).all()

    # 计算日期范围
    date_range = {}
    if statistics:
        date_range = {
            "start": statistics[-1].date.strftime("%Y-%m-%d"),
            "end": statistics[0].date.strftime("%Y-%m-%d")
        }

    return DailyStatisticsListResponse(
        statistics=statistics,
        total_days=total_days,
        date_range=date_range
    )


# ==================== Bank Statistics Endpoints ====================

@router.get("/bank/{bank_id}", response_model=BankStatisticsResponse, tags=["📊 Statistics"])
async def get_bank_statistics(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db)
):
    """获取指定题库的统计"""

    stats = qbank_db.query(UserBankStatistics).filter(
        and_(
            UserBankStatistics.user_id == current_user.id,
            UserBankStatistics.bank_id == bank_id
        )
    ).first()

    if not stats:
        # 如果没有统计记录，返回初始数据
        bank = qbank_db.query(QuestionBankV2).filter(
            QuestionBankV2.id == bank_id
        ).first()

        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题库不存在"
            )

        total_questions = qbank_db.query(func.count(QuestionV2.id)).filter(
            QuestionV2.bank_id == bank_id
        ).scalar() or 0

        # 返回初始统计
        return BankStatisticsResponse(
            id="",
            user_id=current_user.id,
            bank_id=bank_id,
            bank_name=bank.name,
            total_questions=total_questions,
            practiced_questions=0,
            correct_count=0,
            wrong_count=0,
            accuracy_rate=0.0,
            favorite_count=0,
            wrong_questions_count=0,
            total_time_spent=0,
            type_statistics={},
            first_practiced_at=None,
            last_practiced_at=None,
            updated_at=datetime.utcnow()
        )

    # 获取题库名称
    bank = qbank_db.query(QuestionBankV2).filter(
        QuestionBankV2.id == bank_id
    ).first()

    # 构造响应
    response_dict = {
        "id": stats.id,
        "user_id": stats.user_id,
        "bank_id": stats.bank_id,
        "bank_name": bank.name if bank else None,
        "total_questions": stats.total_questions,
        "practiced_questions": stats.practiced_questions,
        "correct_count": stats.correct_count,
        "wrong_count": stats.wrong_count,
        "accuracy_rate": stats.accuracy_rate,
        "favorite_count": stats.favorite_count,
        "wrong_questions_count": stats.wrong_questions_count,
        "total_time_spent": stats.total_time_spent,
        "type_statistics": stats.type_statistics,
        "first_practiced_at": stats.first_practiced_at,
        "last_practiced_at": stats.last_practiced_at,
        "updated_at": stats.updated_at
    }

    return BankStatisticsResponse(**response_dict)


@router.get("/banks", response_model=BankStatisticsListResponse, tags=["📊 Statistics"])
async def get_all_bank_statistics(
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db)
):
    """获取所有题库的统计"""

    stats_list = qbank_db.query(UserBankStatistics).filter(
        UserBankStatistics.user_id == current_user.id
    ).order_by(desc(UserBankStatistics.last_practiced_at)).all()

    # 获取题库名称
    bank_ids = [s.bank_id for s in stats_list]
    banks = qbank_db.query(QuestionBankV2).filter(
        QuestionBankV2.id.in_(bank_ids)
    ).all()
    bank_names = {b.id: b.name for b in banks}

    # 构造响应
    response_list = []
    for stats in stats_list:
        response_list.append(BankStatisticsResponse(
            id=stats.id,
            user_id=stats.user_id,
            bank_id=stats.bank_id,
            bank_name=bank_names.get(stats.bank_id),
            total_questions=stats.total_questions,
            practiced_questions=stats.practiced_questions,
            correct_count=stats.correct_count,
            wrong_count=stats.wrong_count,
            accuracy_rate=stats.accuracy_rate,
            favorite_count=stats.favorite_count,
            wrong_questions_count=stats.wrong_questions_count,
            total_time_spent=stats.total_time_spent,
            type_statistics=stats.type_statistics,
            first_practiced_at=stats.first_practiced_at,
            last_practiced_at=stats.last_practiced_at,
            updated_at=stats.updated_at
        ))

    return BankStatisticsListResponse(
        statistics=response_list,
        total=len(response_list)
    )


# ==================== Overview Statistics Endpoints ====================

@router.get("/overview", response_model=OverviewStatistics, tags=["📊 Statistics"])
async def get_overview_statistics(
    current_user: User = Depends(get_current_user),
    main_db: Session = Depends(get_main_db),
    qbank_db: Session = Depends(get_qbank_db)
):
    """获取总览统计"""

    # 从分题库统计中获取数据
    bank_stats_list = qbank_db.query(UserBankStatistics).filter(
        UserBankStatistics.user_id == current_user.id
    ).all()

    total_banks_accessed = len(bank_stats_list)
    total_questions_practiced = sum(s.practiced_questions for s in bank_stats_list)
    total_correct = sum(s.correct_count for s in bank_stats_list)
    total_wrong = sum(s.wrong_count for s in bank_stats_list)
    total_time_spent = sum(s.total_time_spent for s in bank_stats_list)

    overall_accuracy_rate = (total_correct / (total_correct + total_wrong) * 100) if (total_correct + total_wrong) > 0 else 0.0

    # 获取总收藏数和错题数
    total_favorites = qbank_db.query(func.count(UserFavorite.id)).filter(
        UserFavorite.user_id == current_user.id
    ).scalar() or 0

    total_wrong_questions = qbank_db.query(func.count(UserWrongQuestion.id)).filter(
        and_(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.corrected == False
        )
    ).scalar() or 0

    # 获取总会话数
    total_sessions = qbank_db.query(func.count(PracticeSession.id)).filter(
        PracticeSession.user_id == current_user.id
    ).scalar() or 0

    # 获取练习天数和连续天数
    daily_stats = main_db.query(UserDailyStatistics).filter(
        UserDailyStatistics.user_id == current_user.id
    ).order_by(UserDailyStatistics.date).all()

    total_practice_days = len(daily_stats)

    # 计算连续学习天数
    consecutive_days = 0
    if daily_stats:
        today = date.today()
        for i in range(len(daily_stats) - 1, -1, -1):
            stat_date = daily_stats[i].date.date()
            expected_date = today - timedelta(days=(len(daily_stats) - 1 - i))
            if stat_date == expected_date:
                consecutive_days += 1
            else:
                break

    # 最后练习日期
    last_practice_date = bank_stats_list[0].last_practiced_at if bank_stats_list else None
    if bank_stats_list and len(bank_stats_list) > 1:
        last_practice_date = max(s.last_practiced_at for s in bank_stats_list if s.last_practiced_at)

    return OverviewStatistics(
        total_banks_accessed=total_banks_accessed,
        total_questions_practiced=total_questions_practiced,
        total_correct=total_correct,
        total_wrong=total_wrong,
        overall_accuracy_rate=overall_accuracy_rate,
        total_time_spent=total_time_spent,
        total_sessions=total_sessions,
        total_favorites=total_favorites,
        total_wrong_questions=total_wrong_questions,
        consecutive_days=consecutive_days,
        total_practice_days=total_practice_days,
        last_practice_date=last_practice_date
    )


# ==================== Detailed Statistics Endpoints ====================

@router.get("/detailed", response_model=DetailedStatistics, tags=["📊 Statistics"])
async def get_detailed_statistics(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    main_db: Session = Depends(get_main_db),
    qbank_db: Session = Depends(get_qbank_db)
):
    """获取详细统计（包含图表数据）"""

    # 获取总览统计
    overview = await get_overview_statistics(current_user, main_db, qbank_db)

    # 每日趋势数据
    daily_query = main_db.query(UserDailyStatistics).filter(
        UserDailyStatistics.user_id == current_user.id
    )

    if start_date:
        daily_query = daily_query.filter(func.date(UserDailyStatistics.date) >= start_date)
    if end_date:
        daily_query = daily_query.filter(func.date(UserDailyStatistics.date) <= end_date)
    else:
        # 默认30天
        default_end = date.today()
        default_start = default_end - timedelta(days=30)
        if not start_date:
            daily_query = daily_query.filter(func.date(UserDailyStatistics.date) >= default_start)

    daily_stats = daily_query.order_by(UserDailyStatistics.date).all()
    daily_trend = [
        {
            "date": s.date.strftime("%Y-%m-%d"),
            "questions_answered": s.questions_answered,
            "questions_correct": s.questions_correct,
            "accuracy_rate": s.accuracy_rate
        }
        for s in daily_stats
    ]

    # 题库分布
    bank_stats = qbank_db.query(UserBankStatistics).filter(
        UserBankStatistics.user_id == current_user.id
    ).all()

    # 获取题库名称
    bank_ids = [s.bank_id for s in bank_stats]
    banks = qbank_db.query(QuestionBankV2).filter(
        QuestionBankV2.id.in_(bank_ids)
    ).all()
    bank_names = {b.id: b.name for b in banks}

    bank_distribution = [
        {
            "bank_id": s.bank_id,
            "bank_name": bank_names.get(s.bank_id, "未知题库"),
            "practiced_questions": s.practiced_questions,
            "accuracy_rate": s.accuracy_rate
        }
        for s in bank_stats
    ]

    # 题型分布（汇总所有题库）
    type_stats_combined = {}
    for s in bank_stats:
        if s.type_statistics:
            for q_type, stats in s.type_statistics.items():
                if q_type not in type_stats_combined:
                    type_stats_combined[q_type] = {"total": 0, "correct": 0, "wrong": 0}
                type_stats_combined[q_type]["total"] += stats.get("total", 0)
                type_stats_combined[q_type]["correct"] += stats.get("correct", 0)
                type_stats_combined[q_type]["wrong"] += stats.get("wrong", 0)

    type_distribution = [
        {
            "type": q_type,
            "total": stats["total"],
            "correct": stats["correct"],
            "wrong": stats["wrong"],
            "accuracy_rate": (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
        }
        for q_type, stats in type_stats_combined.items()
    ]

    # 难度分布（需要从答题记录中统计）
    # 这里简化处理，可以后续优化
    difficulty_distribution = []

    # 正确率趋势（从每日统计中获取）
    accuracy_trend = [
        {
            "date": s.date.strftime("%Y-%m-%d"),
            "accuracy_rate": s.accuracy_rate
        }
        for s in daily_stats
    ]

    return DetailedStatistics(
        overview=overview,
        daily_trend=daily_trend,
        bank_distribution=bank_distribution,
        type_distribution=type_distribution,
        difficulty_distribution=difficulty_distribution,
        accuracy_trend=accuracy_trend
    )
