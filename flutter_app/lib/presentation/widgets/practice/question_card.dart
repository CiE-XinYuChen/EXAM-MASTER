import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../data/models/question_model.dart';
import '../../../data/models/answer_record_model.dart';
import '../../providers/practice_provider.dart';
import '../common/rich_content_viewer.dart';

/// Question Card Widget
/// 题目卡片组件 - 支持多种题型
class QuestionCard extends StatefulWidget {
  final QuestionModel question;
  final int questionNumber;
  final int totalQuestions;

  const QuestionCard({
    super.key,
    required this.question,
    required this.questionNumber,
    required this.totalQuestions,
  });

  @override
  State<QuestionCard> createState() => _QuestionCardState();
}

class _QuestionCardState extends State<QuestionCard> {
  // Track if answer is submitted
  bool _isAnswerSubmitted = false;

  // For single choice
  String? _selectedOption;

  // For multiple choice
  Set<String> _selectedOptions = {};

  // For judge
  bool? _judgeAnswer;

  // For fill-in-the-blank
  List<TextEditingController> _fillControllers = [];

  // For essay
  final TextEditingController _essayController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _initAnswer();
  }

  @override
  void didUpdateWidget(QuestionCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.question.id != widget.question.id) {
      _initAnswer();
    }
  }

  @override
  void dispose() {
    for (var controller in _fillControllers) {
      controller.dispose();
    }
    _essayController.dispose();
    super.dispose();
  }

  void _initAnswer() {
    final provider = context.read<PracticeProvider>();
    final savedAnswer = provider.getAnswer(widget.question.id);

    setState(() {
      // If there's a saved answer, mark as submitted
      _isAnswerSubmitted = savedAnswer != null;

      switch (widget.question.type) {
        case QuestionType.single:
          _selectedOption = savedAnswer as String?;
          break;
        case QuestionType.multiple:
          if (savedAnswer is List) {
            _selectedOptions = Set.from(savedAnswer);
          } else {
            _selectedOptions = {};
          }
          break;
        case QuestionType.judge:
          if (savedAnswer is bool) {
            _judgeAnswer = savedAnswer;
          } else if (savedAnswer is String) {
            _judgeAnswer = savedAnswer == 'true';
          } else {
            _judgeAnswer = null;
          }
          break;
        case QuestionType.fill:
          if (savedAnswer is List) {
            _fillControllers = List.generate(
              savedAnswer.length,
              (index) => TextEditingController(text: savedAnswer[index] as String? ?? ''),
            );
          } else {
            // Determine number of blanks (you might need to parse stem)
            _fillControllers = List.generate(1, (_) => TextEditingController());
          }
          break;
        case QuestionType.essay:
          _essayController.text = savedAnswer as String? ?? '';
          break;
      }
    });
  }

  void _saveAnswer(dynamic answer) {
    // Just save the answer locally, don't submit yet
    final provider = context.read<PracticeProvider>();
    provider.setAnswer(widget.question.id, answer);
  }

  Future<void> _submitAnswer() async {
    // Submit answer to server
    final provider = context.read<PracticeProvider>();
    final currentAnswer = provider.getAnswer(widget.question.id);

    if (currentAnswer == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请先选择答案')),
      );
      return;
    }

    final success = await provider.submitAnswer(
      questionId: widget.question.id,
      userAnswer: currentAnswer,
    );

    if (success && mounted) {
      setState(() {
        _isAnswerSubmitted = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Card(
        clipBehavior: Clip.antiAlias,
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Question header
              _buildQuestionHeader(),

              const SizedBox(height: 20),

              // Question stem
              _buildQuestionStem(),

              const SizedBox(height: 24),

              // Answer area based on question type
              _buildAnswerArea(),

              // Submit button (only show if not submitted)
              if (!_isAnswerSubmitted) ...[
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: FilledButton.icon(
                    onPressed: _submitAnswer,
                    icon: const Icon(Icons.send),
                    label: const Text('提交答案', style: TextStyle(fontSize: 16)),
                  ),
                ),
              ],

              // Correct answer (if submitted)
              if (_isAnswerSubmitted && widget.question.correctAnswer != null) ...[
                const SizedBox(height: 24),
                _buildCorrectAnswer(),
              ],

              // Explanation (if submitted and available)
              if (_isAnswerSubmitted && widget.question.explanation != null) ...[
                const SizedBox(height: 16),
                _buildExplanation(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuestionHeader() {
    return Row(
      children: [
        // Question number
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            '第 ${widget.questionNumber} 题',
            style: TextStyle(
              color: Theme.of(context).colorScheme.onPrimaryContainer,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),

        const SizedBox(width: 8),

        // Question type
        _buildTypeChip(),

        // Difficulty
        if (widget.question.difficulty != null) ...[
          const SizedBox(width: 8),
          _buildDifficultyChip(),
        ],

        const Spacer(),

        // Favorite button
        _buildFavoriteButton(),
      ],
    );
  }

  Widget _buildTypeChip() {
    String typeText;
    Color color;

    switch (widget.question.type) {
      case QuestionType.single:
        typeText = '单选';
        color = Colors.blue;
        break;
      case QuestionType.multiple:
        typeText = '多选';
        color = Colors.purple;
        break;
      case QuestionType.judge:
        typeText = '判断';
        color = Colors.green;
        break;
      case QuestionType.fill:
        typeText = '填空';
        color = Colors.orange;
        break;
      case QuestionType.essay:
        typeText = '问答';
        color = Colors.red;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        typeText,
        style: TextStyle(
          fontSize: 12,
          color: color,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildDifficultyChip() {
    String difficultyText;
    Color color;

    switch (widget.question.difficulty!) {
      case QuestionDifficulty.easy:
        difficultyText = '简单';
        color = Colors.green;
        break;
      case QuestionDifficulty.medium:
        difficultyText = '中等';
        color = Colors.orange;
        break;
      case QuestionDifficulty.hard:
        difficultyText = '困难';
        color = Colors.red;
        break;
      case QuestionDifficulty.expert:
        difficultyText = '专家';
        color = Colors.purple;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        difficultyText,
        style: TextStyle(
          fontSize: 12,
          color: color,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildFavoriteButton() {
    final isFavorite = widget.question.isFavorite ?? false;

    return IconButton(
      icon: Icon(
        isFavorite ? Icons.star : Icons.star_border,
        color: isFavorite ? Colors.amber : Colors.grey,
      ),
      onPressed: () {
        // TODO: Toggle favorite
      },
    );
  }

  Widget _buildQuestionStem() {
    return RichContentViewer(
      content: widget.question.stem,
      textStyle: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w500,
        height: 1.5,
      ),
    );
  }

  Widget _buildMediaAttachments() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        if (widget.question.hasImage == true)
          Chip(
            avatar: const Icon(Icons.image, size: 16),
            label: const Text('图片'),
            backgroundColor: Colors.blue.shade50,
          ),
        if (widget.question.hasVideo == true)
          Chip(
            avatar: const Icon(Icons.video_library, size: 16),
            label: const Text('视频'),
            backgroundColor: Colors.red.shade50,
          ),
        if (widget.question.hasAudio == true)
          Chip(
            avatar: const Icon(Icons.audio_file, size: 16),
            label: const Text('音频'),
            backgroundColor: Colors.green.shade50,
          ),
      ],
    );
  }

  Widget _buildAnswerArea() {
    switch (widget.question.type) {
      case QuestionType.single:
        return _buildSingleChoice();
      case QuestionType.multiple:
        return _buildMultipleChoice();
      case QuestionType.judge:
        return _buildJudge();
      case QuestionType.fill:
        return _buildFillInTheBlank();
      case QuestionType.essay:
        return _buildEssay();
    }
  }

  Widget _buildSingleChoice() {
    if (widget.question.options == null) return const SizedBox();

    return Column(
      children: widget.question.options!.map((option) {
        final isSelected = _selectedOption == option.label;

        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: InkWell(
            onTap: _isAnswerSubmitted ? null : () {
              setState(() {
                _selectedOption = option.label;
              });
              _saveAnswer(option.label);
            },
            borderRadius: BorderRadius.circular(12),
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isSelected
                    ? Theme.of(context).colorScheme.primaryContainer
                    : Colors.grey.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isSelected
                      ? Theme.of(context).colorScheme.primary
                      : Colors.grey.shade300,
                  width: isSelected ? 2 : 1,
                ),
              ),
              child: Row(
                children: [
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isSelected
                          ? Theme.of(context).colorScheme.primary
                          : Colors.white,
                      border: Border.all(
                        color: isSelected
                            ? Theme.of(context).colorScheme.primary
                            : Colors.grey.shade400,
                        width: 2,
                      ),
                    ),
                    child: isSelected
                        ? const Icon(Icons.check, size: 16, color: Colors.white)
                        : null,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${option.label}. ',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: isSelected ? Theme.of(context).colorScheme.onPrimaryContainer : Colors.black87,
                          ),
                        ),
                        Expanded(
                          child: RichContentViewer(
                            content: option.content,
                            textStyle: TextStyle(
                              fontSize: 16,
                              color: isSelected ? Theme.of(context).colorScheme.onPrimaryContainer : Colors.black87,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildMultipleChoice() {
    if (widget.question.options == null) return const SizedBox();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          '请选择所有正确答案',
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey.shade600,
            fontStyle: FontStyle.italic,
          ),
        ),
        const SizedBox(height: 12),
        ...widget.question.options!.map((option) {
          final isSelected = _selectedOptions.contains(option.label);

          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: InkWell(
              onTap: _isAnswerSubmitted ? null : () {
                setState(() {
                  if (isSelected) {
                    _selectedOptions.remove(option.label);
                  } else {
                    _selectedOptions.add(option.label);
                  }
                });
                _saveAnswer(_selectedOptions.toList());
              },
              borderRadius: BorderRadius.circular(12),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isSelected
                      ? Theme.of(context).colorScheme.primaryContainer
                      : Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isSelected
                        ? Theme.of(context).colorScheme.primary
                        : Colors.grey.shade300,
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 24,
                      height: 24,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(4),
                        color: isSelected
                            ? Theme.of(context).colorScheme.primary
                            : Colors.white,
                        border: Border.all(
                          color: isSelected
                              ? Theme.of(context).colorScheme.primary
                              : Colors.grey.shade400,
                          width: 2,
                        ),
                      ),
                      child: isSelected
                          ? const Icon(Icons.check, size: 16, color: Colors.white)
                          : null,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${option.label}. ',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: isSelected ? Theme.of(context).colorScheme.onPrimaryContainer : Colors.black87,
                            ),
                          ),
                          Expanded(
                            child: RichContentViewer(
                              content: option.content,
                              textStyle: TextStyle(
                                fontSize: 16,
                                color: isSelected ? Theme.of(context).colorScheme.onPrimaryContainer : Colors.black87,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ],
    );
  }

  Widget _buildJudge() {
    return Row(
      children: [
        Expanded(
          child: InkWell(
            onTap: _isAnswerSubmitted ? null : () {
              setState(() {
                _judgeAnswer = true;
              });
              _saveAnswer('true');
            },
            borderRadius: BorderRadius.circular(12),
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: _judgeAnswer == true
                    ? Colors.green.shade100
                    : Colors.grey.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _judgeAnswer == true
                      ? Colors.green
                      : Colors.grey.shade300,
                  width: _judgeAnswer == true ? 2 : 1,
                ),
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.check_circle,
                    size: 48,
                    color: _judgeAnswer == true ? Colors.green : Colors.grey.shade400,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '正确',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: _judgeAnswer == true ? Colors.green : Colors.grey.shade700,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: InkWell(
            onTap: _isAnswerSubmitted ? null : () {
              setState(() {
                _judgeAnswer = false;
              });
              _saveAnswer('false');
            },
            borderRadius: BorderRadius.circular(12),
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: _judgeAnswer == false
                    ? Colors.red.shade100
                    : Colors.grey.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _judgeAnswer == false
                      ? Colors.red
                      : Colors.grey.shade300,
                  width: _judgeAnswer == false ? 2 : 1,
                ),
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.cancel,
                    size: 48,
                    color: _judgeAnswer == false ? Colors.red : Colors.grey.shade400,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '错误',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: _judgeAnswer == false ? Colors.red : Colors.grey.shade700,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildFillInTheBlank() {
    if (_fillControllers.isEmpty) {
      _fillControllers = List.generate(1, (_) => TextEditingController());
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ...List.generate(_fillControllers.length, (index) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: TextField(
              controller: _fillControllers[index],
              enabled: !_isAnswerSubmitted,
              decoration: InputDecoration(
                labelText: '答案 ${index + 1}',
                hintText: '请输入答案',
                border: const OutlineInputBorder(),
              ),
              onChanged: (value) {
                final answers = _fillControllers.map((c) => c.text).toList();
                _saveAnswer(answers);
              },
            ),
          );
        }),
      ],
    );
  }

  Widget _buildEssay() {
    return TextField(
      controller: _essayController,
      enabled: !_isAnswerSubmitted,
      maxLines: 8,
      decoration: const InputDecoration(
        labelText: '请作答',
        hintText: '请输入您的答案...',
        border: OutlineInputBorder(),
      ),
      onChanged: (value) {
        _saveAnswer(value);
      },
    );
  }

  Widget _buildCorrectAnswer() {
    final provider = context.read<PracticeProvider>();
    final answerResult = provider.getAnswerResult(widget.question.id);

    // If we have the enhanced answer result with options, use it
    if (answerResult != null && answerResult.options != null && answerResult.options!.isNotEmpty) {
      return _buildEnhancedAnswerDisplay(answerResult);
    }

    // Fallback to original display
    final correctAnswerText = widget.question.getCorrectAnswerText();
    if (correctAnswerText == null) return const SizedBox();

    final userAnswer = provider.getAnswer(widget.question.id);
    final isCorrect = widget.question.checkAnswer(userAnswer);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isCorrect ? Colors.green.shade50 : Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isCorrect ? Colors.green.shade200 : Colors.orange.shade200,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isCorrect ? Icons.check_circle : Icons.info_outline,
                color: isCorrect ? Colors.green.shade700 : Colors.orange.shade700,
              ),
              const SizedBox(width: 8),
              Text(
                isCorrect ? '回答正确' : '正确答案',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: isCorrect ? Colors.green.shade700 : Colors.orange.shade700,
                ),
              ),
            ],
          ),
          if (!isCorrect) ...[
            const SizedBox(height: 8),
            Text(
              correctAnswerText,
              style: const TextStyle(
                fontSize: 15,
                height: 1.5,
              ),
            ),
          ],
        ],
      ),
    );
  }

  /// Build enhanced answer display with all options and visual indicators
  Widget _buildEnhancedAnswerDisplay(SubmitAnswerResponse answerResult) {
    final isCorrect = answerResult.isCorrect;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isCorrect ? Colors.green.shade50 : Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isCorrect ? Colors.green.shade200 : Colors.orange.shade200,
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Result header
          Row(
            children: [
              Icon(
                isCorrect ? Icons.check_circle : Icons.cancel,
                color: isCorrect ? Colors.green.shade700 : Colors.red.shade700,
                size: 28,
              ),
              const SizedBox(width: 8),
              Text(
                isCorrect ? '回答正确！' : '回答错误',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: isCorrect ? Colors.green.shade700 : Colors.red.shade700,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),
          const Divider(),
          const SizedBox(height: 12),

          // Title for options display
          Text(
            '答案详情',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade800,
            ),
          ),
          const SizedBox(height: 12),

          // Display all options with indicators
          ...answerResult.options!.map((option) {
            final isCorrectOption = option.isCorrect;

            // Get user's answer to check if this option was selected
            final userAnswerData = answerResult.userAnswer;
            bool isUserSelected = false;

            if (userAnswerData['answer'] != null) {
              // Single choice
              isUserSelected = userAnswerData['answer'] == option.label;
            } else if (userAnswerData['answers'] != null) {
              // Multiple choice
              final selectedAnswers = List<String>.from(userAnswerData['answers'] as List);
              isUserSelected = selectedAnswers.contains(option.label);
            }

            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isCorrectOption
                      ? Colors.green.shade50
                      : (isUserSelected && !isCorrectOption)
                          ? Colors.red.shade50
                          : Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: isCorrectOption
                        ? Colors.green.shade400
                        : (isUserSelected && !isCorrectOption)
                            ? Colors.red.shade400
                            : Colors.grey.shade300,
                    width: isCorrectOption || isUserSelected ? 2 : 1,
                  ),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Indicator icon
                    if (isCorrectOption)
                      Icon(
                        Icons.check_circle,
                        color: Colors.green.shade700,
                        size: 20,
                      )
                    else if (isUserSelected)
                      Icon(
                        Icons.cancel,
                        color: Colors.red.shade700,
                        size: 20,
                      )
                    else
                      Icon(
                        Icons.radio_button_unchecked,
                        color: Colors.grey.shade400,
                        size: 20,
                      ),

                    const SizedBox(width: 8),

                    // Option content
                    Expanded(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${option.label}. ',
                            style: TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.bold,
                              color: isCorrectOption
                                  ? Colors.green.shade900
                                  : (isUserSelected && !isCorrectOption)
                                      ? Colors.red.shade900
                                      : Colors.black87,
                            ),
                          ),
                          Expanded(
                            child: Text(
                              option.content,
                              style: TextStyle(
                                fontSize: 15,
                                color: isCorrectOption
                                    ? Colors.green.shade900
                                    : (isUserSelected && !isCorrectOption)
                                        ? Colors.red.shade900
                                        : Colors.black87,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Label tag
                    if (isCorrectOption) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.green.shade700,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Text(
                          '正确答案',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ] else if (isUserSelected) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.red.shade700,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Text(
                          '你的选择',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildExplanation() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb_outline, color: Colors.blue.shade700),
              const SizedBox(width: 8),
              Text(
                '解析',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue.shade700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            widget.question.explanation!,
            style: const TextStyle(
              fontSize: 15,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}
