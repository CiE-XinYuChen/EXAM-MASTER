# 📚 题库管理新架构设计

## 🎯 设计目标
1. **文件夹与数据库结合**：每个题库对应一个文件夹，存储相关资源
2. **支持富媒体**：轻松管理图片、音频、视频等资源
3. **便于备份**：整个题库（包括资源）可以打包导出
4. **版本管理**：支持题库版本控制
5. **分布式存储**：支持云存储和本地存储

## 📂 文件夹结构

```
storage/
├── question_banks/
│   ├── {bank_id}/                    # 每个题库一个文件夹
│   │   ├── metadata.json             # 题库元数据
│   │   ├── questions.json            # 题目数据
│   │   ├── images/                   # 图片资源
│   │   │   ├── q_{question_id}/      # 每个题目的图片
│   │   │   │   ├── stem.png          # 题干图片
│   │   │   │   ├── option_a.png      # 选项图片
│   │   │   │   └── explanation.png   # 解析图片
│   │   │   └── shared/               # 共享图片
│   │   ├── audio/                    # 音频资源
│   │   ├── video/                    # 视频资源
│   │   └── exports/                  # 导出历史
│   │       ├── 2025-08-08_export.zip
│   │       └── 2025-08-08_export.json
│   └── _templates/                   # 题库模板
│       └── default/
├── resources/                         # 全局共享资源
│   ├── formulas/                     # 公式图片
│   ├── diagrams/                     # 图表
│   └── references/                   # 参考资料
└── uploads/                          # 临时上传目录
    └── temp/
```

## 🗄️ 数据库设计优化

### 1. QuestionBank 表增强
```python
class QuestionBank(BaseQBank):
    __tablename__ = "question_banks"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(String(20), default="1.0.0")
    category = Column(String(50))
    
    # 文件系统关联
    folder_path = Column(String(255))  # 相对路径: question_banks/{bank_id}
    storage_type = Column(String(20), default="local")  # local, s3, oss
    
    # 统计信息
    total_questions = Column(Integer, default=0)
    total_size_mb = Column(Float, default=0.0)  # 包含所有资源的大小
    has_images = Column(Boolean, default=False)
    has_audio = Column(Boolean, default=False)
    has_video = Column(Boolean, default=False)
    
    # 元数据
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

### 2. Question 表增强
```python
class Question(BaseQBank):
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True)
    bank_id = Column(String(36), ForeignKey("question_banks.id"))
    question_number = Column(Integer)
    
    # 内容
    stem = Column(Text, nullable=False)
    stem_format = Column(String(20), default="text")  # text, markdown, latex, html
    stem_image = Column(String(255))  # 题干图片路径
    
    # 资源关联
    has_images = Column(Boolean, default=False)
    has_audio = Column(Boolean, default=False)
    image_paths = Column(JSON)  # {"stem": "path", "options": {...}, "explanation": "path"}
    audio_paths = Column(JSON)
    
    # 其他字段...
```

### 3. QuestionResource 表（新增）
```python
class QuestionResource(BaseQBank):
    __tablename__ = "question_resources"
    
    id = Column(String(36), primary_key=True)
    question_id = Column(String(36), ForeignKey("questions.id"))
    resource_type = Column(String(20))  # image, audio, video, document
    resource_path = Column(String(255))  # 相对路径
    resource_url = Column(String(500))   # CDN URL（如果有）
    file_size = Column(Integer)          # 字节
    mime_type = Column(String(50))
    alt_text = Column(String(255))       # 替代文本（用于无障碍）
    position = Column(String(20))        # stem, option_a, explanation, etc
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 🔧 核心功能实现

### 1. 创建题库时创建文件夹
```python
def create_question_bank(bank_data: dict) -> QuestionBank:
    """创建题库及其文件夹结构"""
    bank_id = str(uuid.uuid4())
    bank_folder = f"storage/question_banks/{bank_id}"
    
    # 创建文件夹结构
    os.makedirs(f"{bank_folder}/images/shared", exist_ok=True)
    os.makedirs(f"{bank_folder}/audio", exist_ok=True)
    os.makedirs(f"{bank_folder}/video", exist_ok=True)
    os.makedirs(f"{bank_folder}/exports", exist_ok=True)
    
    # 创建元数据文件
    metadata = {
        "id": bank_id,
        "name": bank_data["name"],
        "description": bank_data.get("description", ""),
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "question_count": 0
    }
    
    with open(f"{bank_folder}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 创建数据库记录
    bank = QuestionBank(
        id=bank_id,
        name=bank_data["name"],
        description=bank_data.get("description", ""),
        folder_path=f"question_banks/{bank_id}",
        **bank_data
    )
    
    return bank
```

### 2. 上传图片到题目
```python
async def upload_question_image(
    question_id: str, 
    file: UploadFile,
    position: str = "stem"  # stem, option_a, explanation, etc
) -> str:
    """上传题目图片"""
    question = get_question(question_id)
    bank_folder = f"storage/question_banks/{question.bank_id}"
    
    # 创建题目图片文件夹
    image_folder = f"{bank_folder}/images/q_{question_id}"
    os.makedirs(image_folder, exist_ok=True)
    
    # 生成文件名
    ext = file.filename.split(".")[-1]
    filename = f"{position}_{int(time.time())}.{ext}"
    file_path = f"{image_folder}/{filename}"
    
    # 保存文件
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    # 更新数据库
    resource = QuestionResource(
        id=str(uuid.uuid4()),
        question_id=question_id,
        resource_type="image",
        resource_path=file_path.replace("storage/", ""),
        file_size=len(content),
        mime_type=file.content_type,
        position=position
    )
    
    return file_path
```

### 3. 导出题库（包含所有资源）
```python
def export_question_bank(bank_id: str) -> str:
    """导出题库为ZIP包"""
    bank = get_question_bank(bank_id)
    bank_folder = f"storage/question_banks/{bank_id}"
    
    # 导出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_filename = f"{bank.name}_{timestamp}.zip"
    export_path = f"{bank_folder}/exports/{export_filename}"
    
    # 创建ZIP包
    with zipfile.ZipFile(export_path, 'w') as zipf:
        # 添加元数据
        zipf.write(f"{bank_folder}/metadata.json", "metadata.json")
        
        # 添加题目数据
        questions = get_all_questions(bank_id)
        questions_data = [q.to_dict() for q in questions]
        zipf.writestr("questions.json", json.dumps(questions_data, ensure_ascii=False))
        
        # 添加所有图片
        for root, dirs, files in os.walk(f"{bank_folder}/images"):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = file_path.replace(bank_folder + "/", "")
                zipf.write(file_path, arc_path)
    
    return export_path
```

### 4. 导入题库（恢复完整题库）
```python
def import_question_bank(zip_file: UploadFile) -> QuestionBank:
    """从ZIP包导入题库"""
    # 解压到临时目录
    temp_dir = f"storage/uploads/temp/{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_file.file, 'r') as zipf:
        zipf.extractall(temp_dir)
    
    # 读取元数据
    with open(f"{temp_dir}/metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    # 创建新题库
    new_bank = create_question_bank(metadata)
    
    # 复制资源文件
    if os.path.exists(f"{temp_dir}/images"):
        shutil.copytree(f"{temp_dir}/images", f"storage/question_banks/{new_bank.id}/images")
    
    # 导入题目
    with open(f"{temp_dir}/questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
        for q_data in questions:
            import_question(new_bank.id, q_data)
    
    # 清理临时文件
    shutil.rmtree(temp_dir)
    
    return new_bank
```

## 🎨 前端界面增强

### 1. 题目编辑器支持图片
- 题干支持插入图片
- 每个选项支持配图
- 解析支持图文混排
- 支持拖拽上传
- 支持粘贴截图

### 2. 题库管理界面
- 显示题库占用空间
- 显示资源统计（图片数、音频数等）
- 支持题库打包下载
- 支持题库在线预览

### 3. 资源管理器
- 浏览题库所有资源
- 批量上传资源
- 资源去重
- 压缩优化

## 🚀 优势

1. **独立性**：每个题库独立管理，互不干扰
2. **可移植**：整个题库文件夹可以直接复制迁移
3. **易备份**：文件夹级别的备份和恢复
4. **支持CDN**：图片等资源可以上传到CDN
5. **离线使用**：导出的题库包可以离线使用
6. **版本控制**：可以使用Git管理题库版本

## 📝 迁移计划

1. **第一阶段**：实现文件夹创建和基础资源管理
2. **第二阶段**：添加图片上传和显示功能
3. **第三阶段**：实现导出/导入功能
4. **第四阶段**：添加CDN支持和优化

这个架构怎么样？需要我开始实现吗？