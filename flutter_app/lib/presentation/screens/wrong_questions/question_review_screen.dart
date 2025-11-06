import 'package:flutter/material.dart';
import '../../../data/models/wrong_question_model.dart';
import '../../../data/repositories/wrong_questions_repository.dart';
import '../../../data/datasources/remote/wrong_questions_api.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/utils/logger.dart';

/// Question Review Screen
/// 题目复习/订正页面
class QuestionReviewScreen extends StatefulWidget {
  final WrongQuestionModel wrongQuestion;

  const QuestionReviewScreen({
    super.key,
    required this.wrongQuestion,
  });

  @override
  State<QuestionReviewScreen> createState() => _QuestionReviewScreenState();
}

class _QuestionReviewScreenState extends State<QuestionReviewScreen> {
  final WrongQuestionsRepository _repository = WrongQuestionsRepository(
    api: WrongQuestionsApi(DioClient()),
  );

  late bool _isCorrected;
  bool _isUpdating = false;

  @override
  void initState() {
    super.initState();
    _isCorrected = widget.wrongQuestion.corrected;
  }

  Future<void> _toggleCorrectedStatus() async {
    setState(() {
      _isUpdating = true;
    });

    final result = await _repository.markAsCorrected(
      widget.wrongQuestion.id,
      !_isCorrected,
    );

    result.fold(
      (failure) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('更新失败: ${failure.message}')),
        );
        setState(() {
          _isUpdating = false;
        });
      },
      (_) {
        setState(() {
          _isCorrected = !_isCorrected;
          _isUpdating = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(_isCorrected ? '已标记为已订正' : '已标记为未订正')),
        );
        AppLogger.info('Updated corrected status: $_isCorrected');
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('第 ${(widget.wrongQuestion.questionNumber != null && widget.wrongQuestion.questionNumber! > 0) ? widget.wrongQuestion.questionNumber : '?'} 题'),
        actions: [
          // Toggle corrected status button
          IconButton(
            icon: Icon(
              _isCorrected ? Icons.check_circle : Icons.check_circle_outline,
              color: _isCorrected ? Colors.green : null,
            ),
            tooltip: _isCorrected ? '标记为未订正' : '标记为已订正',
            onPressed: _isUpdating ? null : _toggleCorrectedStatus,
          ),
        ],
      ),
      body: _isUpdating
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Error info card
                  _buildErrorInfoCard(),
                  const SizedBox(height: 16),

                  // Question stem
                  _buildSectionTitle('题目'),
                  const SizedBox(height: 8),
                  _buildQuestionStem(),
                  const SizedBox(height: 16),

                  // Question options (if available)
                  if (widget.wrongQuestion.questionOptions != null &&
                      widget.wrongQuestion.questionOptions!.isNotEmpty) ...[
                    _buildQuestionOptions(),
                    const SizedBox(height: 24),
                  ],

                  // Last error answer (if available)
                  if (widget.wrongQuestion.lastErrorAnswer != null) ...[
                    _buildSectionTitle('你的错误答案'),
                    const SizedBox(height: 8),
                    _buildLastErrorAnswer(),
                    const SizedBox(height: 24),
                  ],

                  // Correct answer
                  if (widget.wrongQuestion.correctAnswer != null) ...[
                    _buildSectionTitle('正确答案'),
                    const SizedBox(height: 8),
                    _buildCorrectAnswer(),
                    const SizedBox(height: 24),
                  ],

                  // Tags (if available)
                  if (widget.wrongQuestion.questionTags != null &&
                      widget.wrongQuestion.questionTags!.isNotEmpty) ...[
                    _buildSectionTitle('相关知识点'),
                    const SizedBox(height: 8),
                    _buildTags(),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildErrorInfoCard() {
    return Card(
      color: _isCorrected ? Colors.green.shade50 : Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              _isCorrected ? Icons.check_circle : Icons.error,
              color: _isCorrected ? Colors.green : Colors.red,
              size: 32,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _isCorrected ? '已订正' : '未订正',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: _isCorrected ? Colors.green.shade700 : Colors.red.shade700,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '错误 ${widget.wrongQuestion.errorCount} 次 · 最后错误: ${widget.wrongQuestion.lastErrorAt.substring(0, 10)}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
    );
  }

  Widget _buildQuestionStem() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Question type and difficulty badges
            Row(
              children: [
                Chip(
                  label: Text(_getQuestionTypeLabel(widget.wrongQuestion.questionType)),
                  backgroundColor: Colors.blue.shade100,
                  labelStyle: Theme.of(context).textTheme.labelSmall,
                  padding: EdgeInsets.zero,
                  visualDensity: VisualDensity.compact,
                ),
                const SizedBox(width: 8),
                if (widget.wrongQuestion.questionDifficulty != null)
                  Chip(
                    label: Text(widget.wrongQuestion.questionDifficulty!),
                    backgroundColor: Colors.orange.shade100,
                    labelStyle: Theme.of(context).textTheme.labelSmall,
                    padding: EdgeInsets.zero,
                    visualDensity: VisualDensity.compact,
                  ),
              ],
            ),
            const SizedBox(height: 12),
            // Question text
            Text(
              widget.wrongQuestion.questionStem,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuestionOptions() {
    return Column(
      children: widget.wrongQuestion.questionOptions!.asMap().entries.map((entry) {
        final option = entry.value;
        final label = option['label'] ?? '';
        final content = option['content'] ?? '';
        final isCorrect = option['is_correct'] == true;

        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          color: isCorrect ? Colors.green.shade50 : null,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Option label (A, B, C, D)
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: isCorrect ? Colors.green : Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Center(
                    child: Text(
                      label,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: isCorrect ? Colors.white : Colors.grey.shade700,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                // Option content
                Expanded(
                  child: Text(
                    content,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: isCorrect ? Colors.green.shade900 : null,
                          fontWeight: isCorrect ? FontWeight.w600 : null,
                        ),
                  ),
                ),
                // Checkmark for correct answer
                if (isCorrect)
                  Icon(
                    Icons.check_circle,
                    color: Colors.green.shade700,
                    size: 20,
                  ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildLastErrorAnswer() {
    final lastError = widget.wrongQuestion.lastErrorAnswer!;
    String answerText;

    // Format answer based on question type
    if (lastError.containsKey('answer')) {
      answerText = lastError['answer'].toString();
    } else if (lastError.containsKey('answers')) {
      answerText = (lastError['answers'] as List).join(', ');
    } else {
      answerText = lastError.toString();
    }

    return Card(
      color: Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.close, color: Colors.red.shade700),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                answerText,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.red.shade900,
                    ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCorrectAnswer() {
    final correctAnswer = widget.wrongQuestion.correctAnswer!;
    String answerText;

    // Format answer based on question type
    if (correctAnswer.containsKey('answer')) {
      answerText = correctAnswer['answer'].toString();
    } else if (correctAnswer.containsKey('answers')) {
      answerText = (correctAnswer['answers'] as List).join(', ');
    } else {
      answerText = correctAnswer.toString();
    }

    return Card(
      color: Colors.green.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.check, color: Colors.green.shade700),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                answerText,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.green.shade900,
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTags() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: widget.wrongQuestion.questionTags!
          .map((tag) => Chip(
                label: Text(tag),
                backgroundColor: Colors.blue.shade100,
                labelStyle: Theme.of(context).textTheme.bodySmall,
              ))
          .toList(),
    );
  }

  String _getQuestionTypeLabel(String type) {
    switch (type) {
      case 'single':
        return '单选题';
      case 'multiple':
        return '多选题';
      case 'judge':
        return '判断题';
      case 'fill':
        return '填空题';
      case 'essay':
        return '问答题';
      default:
        return type;
    }
  }
}
