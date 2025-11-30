"""
Question Bank Service - 题库服务层
处理题库的创建、管理、文件系统操作等
"""

import os
import json
import uuid
import shutil
import zipfile
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from app.models.question_models_v2 import (
    QuestionBankV2, QuestionV2, QuestionOptionV2,
    QuestionResourceV2, QuestionBankResource,
    StorageType, ResourceType, QuestionType
)
from app.models.activation import ActivationCode, UserBankAccess


class QuestionBankService:
    """题库服务"""
    
    BASE_STORAGE_PATH = "storage/question_banks"
    
    def __init__(self, db: Session):
        self.db = db
        self._ensure_storage_structure()
    
    def _ensure_storage_structure(self):
        """确保存储目录结构存在"""
        paths = [
            self.BASE_STORAGE_PATH,
            "storage/resources",
            "storage/uploads/temp"
        ]
        for path in paths:
            Path(path).mkdir(parents=True, exist_ok=True)
    
    def create_question_bank(
        self, 
        name: str,
        description: str = "",
        category: str = "",
        creator_id: int = 1,
        **kwargs
    ) -> QuestionBankV2:
        """
        创建题库及其文件夹结构
        """
        # 生成唯一ID
        bank_id = str(uuid.uuid4())
        bank_folder = f"{self.BASE_STORAGE_PATH}/{bank_id}"
        
        # 创建文件夹结构
        folders = [
            f"{bank_folder}/images/shared",
            f"{bank_folder}/images/questions",
            f"{bank_folder}/audio",
            f"{bank_folder}/video",
            f"{bank_folder}/documents",
            f"{bank_folder}/exports",
            f"{bank_folder}/backups"
        ]
        
        for folder in folders:
            Path(folder).mkdir(parents=True, exist_ok=True)
        
        # 创建元数据文件
        metadata = {
            "id": bank_id,
            "name": name,
            "description": description,
            "category": category,
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "creator_id": creator_id,
            "structure_version": "2.0",  # 文件结构版本
            "question_count": 0,
            "resource_count": 0
        }
        
        metadata_path = f"{bank_folder}/metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 创建题目数据文件（初始为空）
        questions_path = f"{bank_folder}/questions.json"
        with open(questions_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        # 创建README文件
        readme_path = f"{bank_folder}/README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(f"# {name}\n\n")
            f.write(f"{description}\n\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Bank ID: {bank_id}\n")
        
        # 创建数据库记录
        bank = QuestionBankV2(
            id=bank_id,
            name=name,
            description=description,
            category=category,
            creator_id=creator_id,
            folder_path=f"question_banks/{bank_id}",
            storage_type=StorageType.local,
            **kwargs
        )
        
        self.db.add(bank)
        self.db.commit()
        self.db.refresh(bank)
        
        return bank
    
    def get_question_bank(self, bank_id: str) -> Optional[QuestionBankV2]:
        """获取题库"""
        return self.db.query(QuestionBankV2).filter(
            QuestionBankV2.id == bank_id
        ).first()
    
    def update_question_bank(
        self, 
        bank_id: str, 
        **update_data
    ) -> QuestionBankV2:
        """更新题库信息"""
        bank = self.get_question_bank(bank_id)
        if not bank:
            raise HTTPException(status_code=404, detail="题库不存在")
        
        # 更新数据库
        for key, value in update_data.items():
            if hasattr(bank, key):
                setattr(bank, key, value)
        
        bank.updated_at = datetime.utcnow()
        self.db.commit()
        
        # 更新元数据文件
        self._update_metadata_file(bank)
        
        return bank
    
    def delete_question_bank(self, bank_id: str) -> bool:
        """删除题库（包括文件夹）"""
        bank = self.get_question_bank(bank_id)
        if not bank:
            raise HTTPException(status_code=404, detail="题库不存在")

        # 备份到回收站（可选）
        self._backup_before_delete(bank)

        # 删除文件夹
        bank_folder = f"{self.BASE_STORAGE_PATH}/{bank_id}"
        if os.path.exists(bank_folder):
            shutil.rmtree(bank_folder)

        # 先删除关联的用户访问记录
        self.db.query(UserBankAccess).filter(UserBankAccess.bank_id == bank_id).delete()

        # 再删除关联的激活码
        self.db.query(ActivationCode).filter(ActivationCode.bank_id == bank_id).delete()

        # 删除数据库记录
        self.db.delete(bank)
        self.db.commit()

        return True
    
    def add_question(
        self,
        bank_id: str,
        stem: str,
        type: QuestionType,
        options: List[Dict] = None,
        meta_data: Dict = None,
        **kwargs
    ) -> QuestionV2:
        """添加题目到题库"""
        bank = self.get_question_bank(bank_id)
        if not bank:
            raise HTTPException(status_code=404, detail="题库不存在")
        
        # 生成题目ID
        question_id = str(uuid.uuid4())
        
        # 创建题目
        question = QuestionV2(
            id=question_id,
            bank_id=bank_id,
            stem=stem,
            type=type,
            meta_data=meta_data or {},
            **kwargs
        )
        
        self.db.add(question)
        
        # 添加选项（如果有）
        if options and type in [QuestionType.single, QuestionType.multiple]:
            for i, opt_data in enumerate(options):
                option = QuestionOptionV2(
                    id=str(uuid.uuid4()),
                    question_id=question_id,
                    option_label=opt_data.get("label", chr(65 + i)),
                    option_content=opt_data["content"],
                    is_correct=opt_data.get("is_correct", False),
                    sort_order=i
                )
                self.db.add(option)
        
        # 更新题库统计
        bank.total_questions += 1
        bank.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # 同步到文件系统
        self._sync_questions_to_file(bank_id)
        
        return question
    
    async def upload_question_image(
        self,
        question_id: str,
        file: UploadFile,
        position: str = "stem"
    ) -> QuestionResourceV2:
        """上传题目图片"""
        question = self.db.query(QuestionV2).filter(
            QuestionV2.id == question_id
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="题目不存在")
        
        # 创建题目图片文件夹
        image_folder = f"{self.BASE_STORAGE_PATH}/{question.bank_id}/images/questions/{question_id}"
        Path(image_folder).mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = file.filename.split(".")[-1].lower()
        filename = f"{position}_{timestamp}.{ext}"
        file_path = f"{image_folder}/{filename}"
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 创建资源记录
        resource = QuestionResourceV2(
            id=str(uuid.uuid4()),
            question_id=question_id,
            resource_type=ResourceType.image,
            resource_path=file_path.replace("storage/", ""),
            file_name=file.filename,
            file_size=len(content),
            mime_type=file.content_type,
            position=position
        )
        
        # 更新题目标记
        question.has_images = True
        
        # 更新题库统计
        bank = question.bank
        bank.has_images = True
        bank.total_size_mb += len(content) / (1024 * 1024)
        
        self.db.add(resource)
        self.db.commit()
        
        return resource
    
    def export_question_bank(
        self,
        bank_id: str,
        include_images: bool = True,
        include_audio: bool = True,
        format: str = "zip"
    ) -> str:
        """导出题库"""
        bank = self.get_question_bank(bank_id)
        if not bank:
            raise HTTPException(status_code=404, detail="题库不存在")
        
        bank_folder = f"{self.BASE_STORAGE_PATH}/{bank_id}"
        
        # 生成导出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in bank.name if c.isalnum() or c in "._- ")
        export_filename = f"{safe_name}_{timestamp}.{format}"
        export_path = f"{bank_folder}/exports/{export_filename}"
        
        if format == "zip":
            # 创建ZIP包
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加元数据
                zipf.write(f"{bank_folder}/metadata.json", "metadata.json")
                
                # 获取并导出所有题目
                questions = self.db.query(QuestionV2).filter(
                    QuestionV2.bank_id == bank_id
                ).all()
                
                questions_data = []
                for q in questions:
                    q_dict = {
                        "id": q.id,
                        "number": q.question_number,
                        "stem": q.stem,
                        "type": q.type.value,
                        "difficulty": q.difficulty,
                        "category": q.category,
                        "explanation": q.explanation,
                        "meta_data": q.meta_data
                    }
                    
                    # 添加选项
                    if q.options:
                        q_dict["options"] = [
                            {
                                "label": opt.option_label,
                                "content": opt.option_content,
                                "is_correct": opt.is_correct
                            }
                            for opt in q.options
                        ]
                    
                    questions_data.append(q_dict)
                
                # 写入题目数据
                zipf.writestr(
                    "questions.json",
                    json.dumps(questions_data, ensure_ascii=False, indent=2)
                )
                
                # 添加图片资源
                if include_images and os.path.exists(f"{bank_folder}/images"):
                    for root, dirs, files in os.walk(f"{bank_folder}/images"):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = file_path.replace(bank_folder + "/", "")
                            zipf.write(file_path, arc_path)
                
                # 添加音频资源
                if include_audio and os.path.exists(f"{bank_folder}/audio"):
                    for root, dirs, files in os.walk(f"{bank_folder}/audio"):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = file_path.replace(bank_folder + "/", "")
                            zipf.write(file_path, arc_path)
        
        elif format == "json":
            # 纯JSON导出
            questions = self.db.query(QuestionV2).filter(
                QuestionV2.bank_id == bank_id
            ).all()
            
            export_data = {
                "bank_info": {
                    "id": bank.id,
                    "name": bank.name,
                    "description": bank.description,
                    "category": bank.category,
                    "version": bank.version,
                    "exported_at": datetime.now().isoformat()
                },
                "questions": []
            }
            
            for q in questions:
                q_dict = {
                    "number": q.question_number,
                    "stem": q.stem,
                    "type": q.type.value,
                    "difficulty": q.difficulty,
                    "category": q.category,
                    "explanation": q.explanation,
                    "meta_data": q.meta_data
                }
                
                if q.options:
                    q_dict["options"] = [
                        {
                            "label": opt.option_label,
                            "content": opt.option_content,
                            "is_correct": opt.is_correct
                        }
                        for opt in q.options
                    ]
                else:
                    q_dict["options"] = []
                
                export_data["questions"].append(q_dict)
            
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return export_path
    
    def import_question_bank(
        self,
        file_path: str,
        creator_id: int = 1
    ) -> QuestionBankV2:
        """导入题库（从ZIP或JSON）"""
        if file_path.endswith('.zip'):
            return self._import_from_zip(file_path, creator_id)
        elif file_path.endswith('.json'):
            return self._import_from_json(file_path, creator_id)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    def _import_from_zip(self, zip_path: str, creator_id: int) -> QuestionBankV2:
        """从ZIP导入"""
        # 解压到临时目录
        temp_dir = f"storage/uploads/temp/{uuid.uuid4()}"
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # 读取元数据
            with open(f"{temp_dir}/metadata.json", "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # 创建新题库
            new_bank = self.create_question_bank(
                name=metadata["name"] + " (导入)",
                description=metadata.get("description", ""),
                category=metadata.get("category", ""),
                creator_id=creator_id
            )
            
            # 复制资源文件
            if os.path.exists(f"{temp_dir}/images"):
                shutil.copytree(
                    f"{temp_dir}/images",
                    f"{self.BASE_STORAGE_PATH}/{new_bank.id}/images",
                    dirs_exist_ok=True
                )
            
            # 导入题目
            with open(f"{temp_dir}/questions.json", "r", encoding="utf-8") as f:
                questions = json.load(f)
                
                for q_data in questions:
                    self.add_question(
                        bank_id=new_bank.id,
                        stem=q_data["stem"],
                        type=QuestionType(q_data["type"]),
                        options=q_data.get("options"),
                        meta_data=q_data.get("meta_data"),
                        difficulty=q_data.get("difficulty", "medium"),
                        category=q_data.get("category"),
                        explanation=q_data.get("explanation"),
                        question_number=q_data.get("number")
                    )
            
            return new_bank
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def _import_from_json(self, json_path: str, creator_id: int) -> QuestionBankV2:
        """从JSON导入"""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 创建新题库
        bank_info = data.get("bank_info", {})
        new_bank = self.create_question_bank(
            name=bank_info.get("name", "导入题库"),
            description=bank_info.get("description", ""),
            category=bank_info.get("category", ""),
            creator_id=creator_id
        )

        # 导入题目
        for q_data in data.get("questions", []):
            # 构建 meta_data，合并 correct_answer 信息
            meta_data = q_data.get("meta_data") or {}
            correct_answer = q_data.get("correct_answer")

            if correct_answer:
                # 根据题型将 correct_answer 合并到 meta_data
                q_type = q_data.get("type", "single")
                if q_type == "fill" and "blanks" in correct_answer:
                    meta_data["blanks"] = correct_answer["blanks"]
                elif q_type == "judge" and "answer" in correct_answer:
                    meta_data["answer"] = correct_answer["answer"]
                elif q_type == "essay":
                    if "reference_answer" in correct_answer:
                        meta_data["reference_answer"] = correct_answer["reference_answer"]
                    if "keywords" in correct_answer:
                        meta_data["keywords"] = correct_answer["keywords"]

            self.add_question(
                bank_id=new_bank.id,
                stem=q_data["stem"],
                type=QuestionType(q_data["type"]),
                options=q_data.get("options"),
                meta_data=meta_data,
                difficulty=q_data.get("difficulty", "medium"),
                category=q_data.get("category"),
                explanation=q_data.get("explanation"),
                question_number=q_data.get("number")
            )

        return new_bank
    
    def _update_metadata_file(self, bank: QuestionBankV2):
        """更新元数据文件"""
        metadata_path = f"{self.BASE_STORAGE_PATH}/{bank.id}/metadata.json"
        
        metadata = {
            "id": bank.id,
            "name": bank.name,
            "description": bank.description,
            "category": bank.category,
            "version": bank.version,
            "updated_at": datetime.now().isoformat(),
            "total_questions": bank.total_questions,
            "has_images": bank.has_images,
            "has_audio": bank.has_audio,
            "has_video": bank.has_video
        }
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _sync_questions_to_file(self, bank_id: str):
        """同步题目数据到文件"""
        questions = self.db.query(QuestionV2).filter(
            QuestionV2.bank_id == bank_id
        ).all()
        
        questions_data = []
        for q in questions:
            q_dict = {
                "id": q.id,
                "number": q.question_number,
                "stem": q.stem,
                "type": q.type.value,
                "difficulty": q.difficulty,
                "category": q.category,
                "explanation": q.explanation,
                "meta_data": q.meta_data,
                "created_at": q.created_at.isoformat() if q.created_at else None
            }
            
            if q.options:
                q_dict["options"] = [
                    {
                        "label": opt.option_label,
                        "content": opt.option_content,
                        "is_correct": opt.is_correct
                    }
                    for opt in q.options
                ]
            
            questions_data.append(q_dict)
        
        questions_path = f"{self.BASE_STORAGE_PATH}/{bank_id}/questions.json"
        with open(questions_path, "w", encoding="utf-8") as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
    
    def renumber_questions(self, bank_id: str) -> int:
        """
        重新编号所有题目
        按创建时间排序，重新分配从1开始的序号
        """
        bank = self.get_question_bank(bank_id)
        if not bank:
            raise HTTPException(status_code=404, detail="题库不存在")
            
        # 获取该题库所有���目，按创建时间排序
        questions = self.db.query(QuestionV2).filter(
            QuestionV2.bank_id == bank_id
        ).order_by(QuestionV2.created_at).all()
        
        # 重新编号
        count = 0
        for index, question in enumerate(questions):
            new_number = index + 1
            if question.question_number != new_number:
                question.question_number = new_number
                count += 1
        
        if count > 0:
            self.db.commit()
            # 同步更新到文件
            self._sync_questions_to_file(bank_id)
            
        return count

    def _backup_before_delete(self, bank: QuestionBankV2):
        """删除前备份"""
        backup_dir = "storage/backups/deleted"
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{bank.name}_{bank.id}_{timestamp}"
        
        # 复制整个题库文件夹
        src = f"{self.BASE_STORAGE_PATH}/{bank.id}"
        dst = f"{backup_dir}/{backup_name}"
        
        if os.path.exists(src):
            shutil.copytree(src, dst)