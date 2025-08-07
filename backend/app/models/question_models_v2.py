"""
Enhanced Question Bank Models with File System Integration
题库模型 v2.0 - 支持文件系统集成
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import BaseQBank


class StorageType(str, enum.Enum):
    """存储类型"""
    local = "local"
    s3 = "s3"
    oss = "oss"
    qiniu = "qiniu"


class ResourceType(str, enum.Enum):
    """资源类型"""
    image = "image"
    audio = "audio"
    video = "video"
    document = "document"
    formula = "formula"


class QuestionType(str, enum.Enum):
    """题目类型"""
    single = "single"        # 单选题
    multiple = "multiple"    # 多选题
    judge = "judge"         # 判断题
    fill = "fill"           # 填空题
    essay = "essay"         # 问答题
    composite = "composite"  # 复合题（包含子题）


class QuestionBankV2(BaseQBank):
    """题库表 - 增强版"""
    __tablename__ = "question_banks_v2"
    
    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    version = Column(String(20), default="1.0.0")
    category = Column(String(50), index=True)
    tags = Column(JSON)  # ["高考", "物理", "力学"]
    
    # 文件系统关联
    folder_path = Column(String(255))  # 相对路径: question_banks/{bank_id}
    storage_type = Column(Enum(StorageType), default=StorageType.local)
    storage_config = Column(JSON)  # 存储配置（如S3 bucket, CDN URL等）
    
    # 统计信息
    total_questions = Column(Integer, default=0)
    total_size_mb = Column(Float, default=0.0)
    has_images = Column(Boolean, default=False)
    has_audio = Column(Boolean, default=False)
    has_video = Column(Boolean, default=False)
    last_sync_at = Column(DateTime)  # 最后同步时间（与文件系统）
    
    # 权限与共享
    creator_id = Column(Integer, nullable=False)
    is_public = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)  # 是否发布
    allow_download = Column(Boolean, default=True)  # 允许下载
    allow_fork = Column(Boolean, default=True)     # 允许复制
    
    # 元数据
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    questions = relationship("QuestionV2", back_populates="bank", cascade="all, delete-orphan")
    resources = relationship("QuestionBankResource", back_populates="bank", cascade="all, delete-orphan")


class QuestionV2(BaseQBank):
    """题目表 - 增强版"""
    __tablename__ = "questions_v2"
    
    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)
    question_number = Column(Integer)  # 题号
    question_code = Column(String(50))  # 题目编码（用于去重）
    
    # 题目内容
    stem = Column(Text, nullable=False)  # 题干
    stem_format = Column(String(20), default="text")  # text, markdown, latex, html
    stem_rich = Column(JSON)  # 富文本内容 {"html": "", "images": [], "formulas": []}
    
    # 题目属性
    type = Column(Enum(QuestionType), nullable=False, index=True)
    difficulty = Column(String(20), default="medium", index=True)  # easy, medium, hard, expert
    score = Column(Float, default=1.0)  # 分值
    estimated_time = Column(Integer)  # 预计答题时间（秒）
    
    # 分类与标签
    category = Column(String(50))
    sub_category = Column(String(50))
    tags = Column(JSON)  # ["三角函数", "求值"]
    knowledge_points = Column(JSON)  # 知识点
    
    # 内容增强
    explanation = Column(Text)  # 解析
    explanation_format = Column(String(20), default="text")
    explanation_rich = Column(JSON)  # 富文本解析
    
    hint = Column(Text)  # 提示
    note = Column(Text)  # 备注
    source = Column(String(100))  # 来源（如"2024高考真题"）
    
    # 资源标记
    has_images = Column(Boolean, default=False)
    has_audio = Column(Boolean, default=False)
    has_video = Column(Boolean, default=False)
    has_formula = Column(Boolean, default=False)
    
    # 统计信息
    usage_count = Column(Integer, default=0)  # 使用次数
    error_count = Column(Integer, default=0)  # 错误次数
    avg_score = Column(Float)  # 平均得分率
    avg_time = Column(Float)   # 平均答题时间
    
    # 元数据（包含答案等）
    meta_data = Column(JSON)
    """
    meta_data 结构示例：
    {
        # 判断题
        "answer": true/false,
        
        # 填空题
        "blanks": [
            {"position": 0, "answer": "答案", "alternatives": ["备选1", "备选2"]},
            {"position": 1, "answer": "答案2", "alternatives": []}
        ],
        
        # 问答题
        "reference_answer": "参考答案",
        "keywords": ["关键词1", "关键词2"],
        "scoring_rules": {...},
        
        # 复合题
        "sub_questions": [...]
    }
    """
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    bank = relationship("QuestionBankV2", back_populates="questions")
    options = relationship("QuestionOptionV2", back_populates="question", cascade="all, delete-orphan")
    resources = relationship("QuestionResourceV2", back_populates="question", cascade="all, delete-orphan")


class QuestionOptionV2(BaseQBank):
    """选项表 - 增强版"""
    __tablename__ = "question_options_v2"
    
    id = Column(String(36), primary_key=True, index=True)
    question_id = Column(String(36), ForeignKey("questions_v2.id"), nullable=False, index=True)
    
    option_label = Column(String(10), nullable=False)  # A, B, C, D
    option_content = Column(Text, nullable=False)
    option_format = Column(String(20), default="text")
    option_rich = Column(JSON)  # 富文本内容
    
    is_correct = Column(Boolean, default=False, nullable=False)
    explanation = Column(Text)  # 选项解析
    sort_order = Column(Integer, default=0)
    
    # 资源标记
    has_image = Column(Boolean, default=False)
    image_path = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    question = relationship("QuestionV2", back_populates="options")


class QuestionResourceV2(BaseQBank):
    """题目资源表"""
    __tablename__ = "question_resources_v2"
    
    id = Column(String(36), primary_key=True, index=True)
    question_id = Column(String(36), ForeignKey("questions_v2.id"), nullable=False, index=True)
    
    resource_type = Column(Enum(ResourceType), nullable=False)
    resource_path = Column(String(255), nullable=False)  # 相对路径
    resource_url = Column(String(500))  # CDN URL
    
    file_name = Column(String(255))
    file_size = Column(Integer)  # 字节
    mime_type = Column(String(50))
    
    position = Column(String(50))  # stem, option_a, explanation, etc
    alt_text = Column(String(255))  # 替代文本
    caption = Column(String(255))   # 图片说明
    
    width = Column(Integer)   # 图片/视频宽度
    height = Column(Integer)  # 图片/视频高度
    duration = Column(Integer)  # 音频/视频时长（秒）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    question = relationship("QuestionV2", back_populates="resources")


class QuestionBankResource(BaseQBank):
    """题库级别的共享资源"""
    __tablename__ = "question_bank_resources"
    
    id = Column(String(36), primary_key=True, index=True)
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)
    
    resource_type = Column(Enum(ResourceType), nullable=False)
    resource_path = Column(String(255), nullable=False)
    resource_url = Column(String(500))
    
    file_name = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(50))
    
    title = Column(String(255))
    description = Column(Text)
    tags = Column(JSON)
    
    usage_count = Column(Integer, default=0)  # 使用次数
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    bank = relationship("QuestionBankV2", back_populates="resources")


class QuestionBankExport(BaseQBank):
    """题库导出记录"""
    __tablename__ = "question_bank_exports"
    
    id = Column(String(36), primary_key=True, index=True)
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)
    
    export_type = Column(String(20))  # json, csv, pdf, zip
    export_path = Column(String(255))
    file_size = Column(Integer)
    
    include_images = Column(Boolean, default=True)
    include_audio = Column(Boolean, default=True)
    include_answers = Column(Boolean, default=True)
    include_explanations = Column(Boolean, default=True)
    
    exported_by = Column(Integer)  # User ID
    exported_at = Column(DateTime, default=datetime.utcnow)
    download_count = Column(Integer, default=0)
    expire_at = Column(DateTime)  # 过期时间