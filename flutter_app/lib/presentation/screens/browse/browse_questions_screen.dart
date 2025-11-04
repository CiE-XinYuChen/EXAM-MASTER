import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:card_swiper/card_swiper.dart';
import '../../providers/question_bank_provider.dart';
import '../../../data/models/question_model.dart';
import '../../widgets/practice/question_card.dart';

/// Browse Questions Screen
/// 浏览题目页面 - 直接查看答案，无需作答
class BrowseQuestionsScreen extends StatefulWidget {
  final String bankId;

  const BrowseQuestionsScreen({
    super.key,
    required this.bankId,
  });

  @override
  State<BrowseQuestionsScreen> createState() => _BrowseQuestionsScreenState();
}

class _BrowseQuestionsScreenState extends State<BrowseQuestionsScreen> {
  final SwiperController _swiperController = SwiperController();
  int _currentIndex = 0;
  List<QuestionModel> _questions = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadQuestions();
    });
  }

  @override
  void dispose() {
    _swiperController.dispose();
    super.dispose();
  }

  Future<void> _loadQuestions() async {
    setState(() {
      _isLoading = true;
    });

    final provider = context.read<QuestionBankProvider>();
    await provider.getQuestions(
      bankId: widget.bankId,
      page: 1,
      pageSize: 10000,
    );

    setState(() {
      _questions = provider.questions;
      _isLoading = false;
    });
  }

  void _onIndexChanged(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('浏览题目'),
        actions: [
          // Question list button
          IconButton(
            icon: const Icon(Icons.format_list_numbered),
            onPressed: () {
              _showQuestionListDialog();
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : _questions.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.quiz_outlined,
                        size: 64,
                        color: Colors.grey.shade400,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        '暂无题目',
                        style: TextStyle(
                          fontSize: 20,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                )
              : Column(
                  children: [
                    // Progress bar
                    _buildProgressBar(),

                    // Question cards
                    Expanded(
                      child: Swiper(
                        controller: _swiperController,
                        itemCount: _questions.length,
                        onIndexChanged: _onIndexChanged,
                        index: _currentIndex,
                        loop: false,
                        itemBuilder: (context, index) {
                          final question = _questions[index];
                          return _BrowseQuestionCard(
                            question: question,
                            questionNumber: index + 1,
                            totalQuestions: _questions.length,
                          );
                        },
                      ),
                    ),

                    // Navigation buttons
                    _buildNavigationButtons(),
                  ],
                ),
    );
  }

  Widget _buildProgressBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              Icon(
                Icons.visibility_outlined,
                size: 20,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(
                '浏览模式',
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const Spacer(),
              Text(
                '${_currentIndex + 1}/${_questions.length}',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: _questions.isEmpty
                ? 0
                : (_currentIndex + 1) / _questions.length,
            backgroundColor: Colors.grey.shade200,
            minHeight: 6,
            borderRadius: BorderRadius.circular(3),
          ),
        ],
      ),
    );
  }

  Widget _buildNavigationButtons() {
    final hasPrevious = _currentIndex > 0;
    final hasNext = _currentIndex < _questions.length - 1;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Previous button
          Expanded(
            child: OutlinedButton.icon(
              onPressed: hasPrevious
                  ? () {
                      _swiperController.previous();
                    }
                  : null,
              icon: const Icon(Icons.arrow_back),
              label: const Text('上一题'),
            ),
          ),
          const SizedBox(width: 16),

          // Next button
          Expanded(
            flex: 2,
            child: FilledButton.icon(
              onPressed: hasNext
                  ? () {
                      _swiperController.next();
                    }
                  : null,
              icon: const Icon(Icons.arrow_forward),
              label: const Text('下一题'),
            ),
          ),
        ],
      ),
    );
  }

  void _showQuestionListDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          child: Container(
            height: MediaQuery.of(context).size.height * 0.7,
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '题目列表',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: GridView.builder(
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 5,
                      mainAxisSpacing: 8,
                      crossAxisSpacing: 8,
                      childAspectRatio: 1,
                    ),
                    itemCount: _questions.length,
                    itemBuilder: (context, index) {
                      final isCurrent = index == _currentIndex;
                      return InkWell(
                        onTap: () {
                          _swiperController.move(index);
                          Navigator.pop(context);
                        },
                        child: Container(
                          decoration: BoxDecoration(
                            color: isCurrent
                                ? Theme.of(context).colorScheme.primary
                                : Colors.grey.shade200,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Center(
                            child: Text(
                              '${index + 1}',
                              style: TextStyle(
                                color: isCurrent ? Colors.white : Colors.grey.shade700,
                                fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                              ),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// Browse Question Card
/// 显示题目和答案的卡片
class _BrowseQuestionCard extends StatelessWidget {
  final QuestionModel question;
  final int questionNumber;
  final int totalQuestions;

  const _BrowseQuestionCard({
    required this.question,
    required this.questionNumber,
    required this.totalQuestions,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Question header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '第 $questionNumber 题',
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Theme.of(context).colorScheme.onPrimaryContainer,
                          ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Chip(
                    label: Text(_getQuestionTypeLabel(question.type)),
                    backgroundColor: Colors.blue.shade100,
                    labelStyle: Theme.of(context).textTheme.labelSmall,
                    visualDensity: VisualDensity.compact,
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Question stem
              Text(
                question.stem,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      height: 1.6,
                    ),
              ),

              const SizedBox(height: 24),

              // Options (if any)
              if (question.options != null && question.options!.isNotEmpty)
                ...question.options!.asMap().entries.map((entry) {
                  final option = entry.value;
                  final isCorrect = option.isCorrect ?? false;

                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isCorrect
                          ? Colors.green.shade50
                          : Colors.grey.shade50,
                      border: Border.all(
                        color: isCorrect ? Colors.green : Colors.grey.shade300,
                        width: isCorrect ? 2 : 1,
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 32,
                          height: 32,
                          decoration: BoxDecoration(
                            color: isCorrect ? Colors.green : Colors.grey.shade300,
                            shape: BoxShape.circle,
                          ),
                          child: Center(
                            child: Text(
                              option.label,
                              style: TextStyle(
                                color: isCorrect ? Colors.white : Colors.grey.shade700,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            option.content,
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ),
                        if (isCorrect)
                          const Icon(
                            Icons.check_circle,
                            color: Colors.green,
                          ),
                      ],
                    ),
                  );
                }),

              const SizedBox(height: 24),
              const Divider(),
              const SizedBox(height: 16),

              // Explanation section
              Row(
                children: [
                  Icon(
                    Icons.lightbulb_outline,
                    color: Colors.orange.shade700,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '题目解析',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.orange.shade700,
                        ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              if (question.explanation != null && question.explanation!.isNotEmpty)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.orange.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    question.explanation!,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          height: 1.6,
                        ),
                  ),
                )
              else
                Text(
                  '暂无解析',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey.shade600,
                      ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  String _getQuestionTypeLabel(dynamic type) {
    final typeStr = type.toString();
    switch (typeStr) {
      case 'single':
      case 'QuestionType.single':
        return '单选题';
      case 'multiple':
      case 'QuestionType.multiple':
        return '多选题';
      case 'judge':
      case 'QuestionType.judge':
        return '判断题';
      case 'fill':
      case 'QuestionType.fill':
        return '填空题';
      case 'essay':
      case 'QuestionType.essay':
        return '问答题';
      default:
        return typeStr;
    }
  }
}
