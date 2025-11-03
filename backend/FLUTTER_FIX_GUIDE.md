# Flutter前端修复指南 / Flutter Fix Guide

## 修复时间 / Fix Date
2025-11-03

---

## 🎯 需要修复的问题 / Issues to Fix

### 1. AudioPlayer 内存泄漏 / AudioPlayer Memory Leak

**错误信息 / Error Message:**
```
setState() called after dispose(): _AudioPlayerWidgetState
```

**原因 / Cause:**
音频播放器组件在被销毁后仍然尝试更新状态，导致内存泄漏。

**修复方法 / Solution:**

找到AudioPlayer组件（通常在 `lib/widgets/audio_player_widget.dart` 或类似路径），在 `dispose()` 方法中正确清理资源：

```dart
class _AudioPlayerWidgetState extends State<AudioPlayerWidget> {
  AudioPlayer? _audioPlayer;
  StreamSubscription? _positionSubscription;
  StreamSubscription? _durationSubscription;
  StreamSubscription? _stateSubscription;
  Timer? _progressTimer;

  @override
  void initState() {
    super.initState();
    _audioPlayer = AudioPlayer();
    _setupListeners();
  }

  void _setupListeners() {
    // 设置监听器
    _positionSubscription = _audioPlayer?.onPositionChanged.listen((position) {
      if (mounted) {  // ✅ 关键：检查mounted
        setState(() {
          // 更新位置
        });
      }
    });

    _durationSubscription = _audioPlayer?.onDurationChanged.listen((duration) {
      if (mounted) {  // ✅ 关键：检查mounted
        setState(() {
          // 更新时长
        });
      }
    });

    _stateSubscription = _audioPlayer?.onPlayerStateChanged.listen((state) {
      if (mounted) {  // ✅ 关键：检查mounted
        setState(() {
          // 更新状态
        });
      }
    });
  }

  @override
  void dispose() {
    // ✅ 重要：按正确顺序清理资源
    _progressTimer?.cancel();
    _progressTimer = null;

    // 取消所有订阅
    _positionSubscription?.cancel();
    _durationSubscription?.cancel();
    _stateSubscription?.cancel();

    // 停止并释放播放器
    _audioPlayer?.stop();
    _audioPlayer?.dispose();
    _audioPlayer = null;

    super.dispose();
  }

  // 在所有setState调用中添加mounted检查
  void _updateState() {
    if (mounted) {  // ✅ 添加检查
      setState(() {
        // 状态更新
      });
    }
  }
}
```

**关键要点 / Key Points:**
1. ✅ 所有`setState()`调用前检查`mounted`
2. ✅ 在`dispose()`中取消所有StreamSubscription
3. ✅ 在`dispose()`中取消所有Timer
4. ✅ 在`dispose()`中释放AudioPlayer
5. ✅ 按正确顺序清理（Timer → Subscriptions → Player → super.dispose()）

---

### 2. 答题流程逻辑 / Practice Flow Logic

**当前问题 / Current Issue:**
前端答题流程需要优化为：选择选项 → 提交 → 查看答案和解析 → 下一题

**后端已完成 / Backend Completed:**
✅ 答案返回现在包含完整信息：
- `correct_answer`: 正确答案
- `explanation`: 解析内容
- `options`: 所有选项（包含is_correct标记）
- `question_type`: 题目类型
- `question_stem`: 题干
- `is_correct`: 用户是否答对

**前端需要实现 / Frontend Implementation:**

```dart
// 1. 答题页面状态
class PracticeScreenState extends State<PracticeScreen> {
  String? selectedAnswer;  // 用户选择的答案
  AnswerResult? answerResult;  // 提交后的结果
  bool isAnswered = false;  // 是否已答题

  // 提交答案
  Future<void> submitAnswer() async {
    if (selectedAnswer == null) return;

    setState(() {
      isSubmitting = true;
    });

    try {
      // 调用API提交答案
      final result = await practiceRepository.submitAnswer(
        sessionId: sessionId,
        questionId: currentQuestion.id,
        userAnswer: {'answer': selectedAnswer},
        timeSpent: _calculateTimeSpent(),
      );

      setState(() {
        answerResult = result;
        isAnswered = true;
        isSubmitting = false;
      });

      // 显示答案解析
      _showAnswerResult(result);

    } catch (e) {
      // 错误处理
      setState(() {
        isSubmitting = false;
      });
    }
  }

  // 显示答案和解析
  void _showAnswerResult(AnswerResult result) {
    // 方案1: 在当前页面显示（推荐）
    // UI会自动根据isAnswered状态显示答案

    // 方案2: 使用Dialog或BottomSheet
    showModalBottomSheet(
      context: context,
      builder: (context) => AnswerResultSheet(
        result: result,
        onNext: _goToNextQuestion,
      ),
    );
  }

  // 下一题
  void _goToNextQuestion() {
    setState(() {
      selectedAnswer = null;
      answerResult = null;
      isAnswered = false;
      currentIndex++;
    });

    // 更新session进度
    _updateSessionProgress();

    // 加载下一题
    _loadNextQuestion();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // 题目显示
          QuestionWidget(question: currentQuestion),

          // 选项列表
          if (!isAnswered)
            OptionsWidget(
              options: currentQuestion.options,
              selectedAnswer: selectedAnswer,
              onSelect: (answer) {
                setState(() {
                  selectedAnswer = answer;
                });
              },
            )
          else
            // 显示答案和解析
            AnswerResultWidget(
              result: answerResult!,
              userAnswer: selectedAnswer,
            ),

          // 底部按钮
          if (!isAnswered)
            ElevatedButton(
              onPressed: selectedAnswer != null ? submitAnswer : null,
              child: Text('提交'),
            )
          else
            ElevatedButton(
              onPressed: _goToNextQuestion,
              child: Text('下一题'),
            ),
        ],
      ),
    );
  }
}

// 答案结果显示组件
class AnswerResultWidget extends StatelessWidget {
  final AnswerResult result;
  final String? userAnswer;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // 正确/错误提示
        Container(
          color: result.isCorrect ? Colors.green : Colors.red,
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(
                result.isCorrect ? Icons.check_circle : Icons.cancel,
                color: Colors.white,
              ),
              SizedBox(width: 8),
              Text(
                result.isCorrect ? '回答正确！' : '回答错误',
                style: TextStyle(color: Colors.white, fontSize: 18),
              ),
            ],
          ),
        ),

        // 选项列表（显示正确答案）
        if (result.options != null)
          ListView.builder(
            shrinkWrap: true,
            physics: NeverScrollableScrollPhysics(),
            itemCount: result.options!.length,
            itemBuilder: (context, index) {
              final option = result.options![index];
              final isUserAnswer = option['label'] == userAnswer;
              final isCorrect = option['is_correct'] == true;

              return Container(
                margin: EdgeInsets.symmetric(vertical: 4),
                decoration: BoxDecoration(
                  border: Border.all(
                    color: isCorrect
                        ? Colors.green
                        : isUserAnswer
                            ? Colors.red
                            : Colors.grey,
                    width: 2,
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ListTile(
                  leading: Text(
                    option['label'],
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: isCorrect ? Colors.green : null,
                    ),
                  ),
                  title: Text(option['content']),
                  trailing: isCorrect
                      ? Icon(Icons.check, color: Colors.green)
                      : isUserAnswer
                          ? Icon(Icons.close, color: Colors.red)
                          : null,
                ),
              );
            },
          ),

        // 解析
        if (result.explanation != null && result.explanation!.isNotEmpty)
          Container(
            margin: EdgeInsets.all(16),
            padding: EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.lightbulb, color: Colors.blue),
                    SizedBox(width: 8),
                    Text(
                      '解析',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(result.explanation!),
              ],
            ),
          ),
      ],
    );
  }
}
```

---

### 3. 进度保存功能 / Progress Saving

**实现方案 / Implementation:**

```dart
// 在答题过程中自动保存进度
class PracticeScreenState extends State<PracticeScreen> {
  Timer? _progressSaveTimer;

  @override
  void initState() {
    super.initState();
    // 每30秒自动保存一次进度
    _progressSaveTimer = Timer.periodic(
      Duration(seconds: 30),
      (_) => _saveProgress(),
    );
  }

  @override
  void dispose() {
    _progressSaveTimer?.cancel();
    // 最后保存一次进度
    _saveProgress();
    super.dispose();
  }

  Future<void> _saveProgress() async {
    try {
      await practiceRepository.updateSession(
        sessionId: sessionId,
        currentIndex: currentIndex,
        status: isCompleted ? 'completed' : 'in_progress',
      );
    } catch (e) {
      print('保存进度失败: $e');
    }
  }

  // 在提交答案后也保存进度
  Future<void> submitAnswer() async {
    // ... 提交答案逻辑 ...

    // 更新进度
    await _saveProgress();
  }
}
```

---

## 📝 API 数据结构 / API Data Structure

### 提交答案响应 / Submit Answer Response

```json
{
  "record_id": "uuid",
  "question_id": "uuid",
  "is_correct": true,
  "correct_answer": {
    "answer": "C"
  },
  "user_answer": {
    "answer": "C"
  },
  "explanation": "解析内容...",
  "time_spent": 30,
  "created_at": "2025-11-03T16:42:00",
  "options": [
    {
      "label": "A",
      "content": "选项A内容",
      "is_correct": false
    },
    {
      "label": "B",
      "content": "选项B内容",
      "is_correct": false
    },
    {
      "label": "C",
      "content": "选项C内容",
      "is_correct": true
    }
  ],
  "question_type": "single",
  "question_stem": "题干内容..."
}
```

---

## 🎯 实施步骤 / Implementation Steps

### 步骤 1: 修复AudioPlayer内存泄漏
1. 找到AudioPlayer组件文件
2. 在所有`setState()`前添加`mounted`检查
3. 正确实现`dispose()`方法
4. 测试多次进入/退出答题页面，确认不再报错

### 步骤 2: 更新答题流程
1. 修改答题页面状态管理
2. 添加答案结果显示组件
3. 实现提交按钮和下一题按钮的切换逻辑
4. 测试完整答题流程

### 步骤 3: 实现进度保存
1. 添加定时器自动保存
2. 在关键节点手动保存
3. 在页面退出时保存最终进度
4. 测试进度保存和恢复

### 步骤 4: 支持未练习模式
后端已支持，前端只需传递 `mode: "unpracticed"` 即可

---

## ✅ 测试清单 / Testing Checklist

- [ ] AudioPlayer不再报setState错误
- [ ] 答题流程：选择 → 提交 → 查看答案 → 下一题
- [ ] 答案显示正确（标记正确选项和用户选择）
- [ ] 解析正常显示
- [ ] 进度正确保存和恢复
- [ ] 未练习模式正常工作
- [ ] 收藏功能正常
- [ ] 错题本功能正常

---

## 🔗 相关文件 / Related Files

### 后端文件
- `app/api/v1/practice.py` - 练习API
- `app/api/v1/favorites.py` - 收藏API
- `app/schemas/practice_schemas.py` - 数据模型

### 前端需要修改的文件
- `lib/screens/practice/practice_screen.dart` - 答题页面
- `lib/widgets/audio_player_widget.dart` - 音频播放器
- `lib/repositories/practice_repository.dart` - 练习仓库
- `lib/models/answer_result.dart` - 答案结果模型

---

## 📞 需要帮助？ / Need Help?

如果在实施过程中遇到问题：
1. 检查后端日志确认API返回的数据结构
2. 使用Flutter DevTools检查widget树和内存泄漏
3. 确保所有异步操作都有正确的错误处理
