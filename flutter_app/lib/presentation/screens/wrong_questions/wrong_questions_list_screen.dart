import 'package:flutter/material.dart';
import '../../../data/models/wrong_question_model.dart';
import '../../../data/datasources/remote/wrong_questions_api.dart';
import '../../../data/repositories/wrong_questions_repository.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/utils/logger.dart';
import 'question_review_screen.dart';

/// Wrong Questions List Screen
/// 错题本列表页面
class WrongQuestionsListScreen extends StatefulWidget {
  final String bankId;

  const WrongQuestionsListScreen({
    super.key,
    required this.bankId,
  });

  @override
  State<WrongQuestionsListScreen> createState() =>
      _WrongQuestionsListScreenState();
}

class _WrongQuestionsListScreenState extends State<WrongQuestionsListScreen> {
  final WrongQuestionsRepository _repository = WrongQuestionsRepository(
    api: WrongQuestionsApi(DioClient()),
  );

  List<WrongQuestionModel> _wrongQuestions = [];
  bool _isLoading = true;
  String? _error;
  String _selectedFilter = 'all';
  int _uncorrectedCount = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadWrongQuestions();
    });
  }

  Future<void> _loadWrongQuestions() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      bool? correctedFilter;
      if (_selectedFilter == 'uncorrected') {
        correctedFilter = false;
      } else if (_selectedFilter == 'corrected') {
        correctedFilter = true;
      }

      final result = await _repository.getWrongQuestions(
        page: 1,
        pageSize: 1000,
        bankId: widget.bankId,
        corrected: correctedFilter,
      );

      result.fold(
        (failure) {
          setState(() {
            _error = failure.message;
            _isLoading = false;
          });
          AppLogger.error('Failed to load wrong questions: ${failure.message}');
        },
        (response) {
          setState(() {
            _wrongQuestions = response.wrongQuestions;
            _uncorrectedCount = response.uncorrectedCount;
            _isLoading = false;
          });
          AppLogger.info('Loaded ${_wrongQuestions.length} wrong questions');
        },
      );
    } catch (e) {
      setState(() {
        _error = '加载失败: $e';
        _isLoading = false;
      });
      AppLogger.error('Unexpected error loading wrong questions: $e');
    }
  }

  Future<void> _deleteWrongQuestion(String wrongQuestionId, int index) async {
    final result = await _repository.deleteWrongQuestion(wrongQuestionId);

    result.fold(
      (failure) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('删除失败: ${failure.message}')),
        );
      },
      (_) {
        setState(() {
          _wrongQuestions.removeAt(index);
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('已从错题本删除')),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('错题本'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error_outline,
                          size: 64, color: Colors.grey.shade400),
                      const SizedBox(height: 16),
                      Text(_error!,
                          style: TextStyle(color: Colors.grey.shade600)),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadWrongQuestions,
                        child: const Text('重试'),
                      ),
                    ],
                  ),
                )
              : Column(
                  children: [
                    // Summary Card
                    _buildSummaryCard(),

                    // Filter Tabs
                    _buildFilterTabs(),

                    // Wrong Questions List
                    Expanded(
                      child: _buildWrongQuestionsList(),
                    ),
                  ],
                ),
    );
  }

  Widget _buildSummaryCard() {
    final wrongQuestionsCount = _wrongQuestions.length;
    final correctedCount = _wrongQuestions.where((wq) => wq.corrected).length;

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.red.shade100,
            Colors.red.shade50,
          ],
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.red,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.error_outline,
              color: Colors.white,
              size: 32,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '错题本',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  '共 $wrongQuestionsCount 道错题 · 已订正 $correctedCount 道',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey.shade700,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterTabs() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Expanded(
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                  value: 'all',
                  label: Text('全部'),
                  icon: Icon(Icons.list),
                ),
                ButtonSegment(
                  value: 'uncorrected',
                  label: Text('未订正'),
                  icon: Icon(Icons.error),
                ),
                ButtonSegment(
                  value: 'corrected',
                  label: Text('已订正'),
                  icon: Icon(Icons.check_circle),
                ),
              ],
              selected: {_selectedFilter},
              onSelectionChanged: (Set<String> newSelection) {
                setState(() {
                  _selectedFilter = newSelection.first;
                });
                _loadWrongQuestions();
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWrongQuestionsList() {
    if (_wrongQuestions.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle_outline,
                size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text('还没有错题',
                style: TextStyle(fontSize: 18, color: Colors.grey.shade600)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _wrongQuestions.length,
      itemBuilder: (context, index) {
        final wrongQuestion = _wrongQuestions[index];
        return Dismissible(
          key: Key(wrongQuestion.id),
          direction: DismissDirection.endToStart,
          background: Container(
            alignment: Alignment.centerRight,
            padding: const EdgeInsets.only(right: 16),
            decoration: BoxDecoration(
              color: Colors.red,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.delete,
              color: Colors.white,
            ),
          ),
          onDismissed: (direction) {
            _deleteWrongQuestion(wrongQuestion.id, index);
          },
          child: _WrongQuestionCard(
            questionNumber: (wrongQuestion.questionNumber != null && wrongQuestion.questionNumber! > 0)
                ? wrongQuestion.questionNumber!
                : (index + 1),
            questionStem: wrongQuestion.questionStem,
            questionType: _getQuestionTypeLabel(wrongQuestion.questionType),
            difficulty: wrongQuestion.questionDifficulty ?? '未知',
            errorCount: wrongQuestion.errorCount,
            isCorrected: wrongQuestion.corrected,
            lastErrorDate: wrongQuestion.lastErrorAt.substring(0, 10),
            onTap: () async {
              // Navigate to question review screen
              final result = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => QuestionReviewScreen(
                    wrongQuestion: wrongQuestion,
                  ),
                ),
              );

              // Refresh list if status changed
              if (result == true) {
                _loadWrongQuestions();
              }
            },
          ),
        );
      },
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

/// Wrong Question Card
class _WrongQuestionCard extends StatelessWidget {
  final int questionNumber;
  final String questionStem;
  final String questionType;
  final String difficulty;
  final int errorCount;
  final bool isCorrected;
  final String lastErrorDate;
  final VoidCallback onTap;

  const _WrongQuestionCard({
    required this.questionNumber,
    required this.questionStem,
    required this.questionType,
    required this.difficulty,
    required this.errorCount,
    required this.isCorrected,
    required this.lastErrorDate,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Question number and tags
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade100,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '第 $questionNumber 题',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            color: Colors.blue.shade700,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Chip(
                    label: Text(questionType),
                    backgroundColor: Colors.green.shade100,
                    labelStyle: Theme.of(context).textTheme.labelSmall,
                    padding: EdgeInsets.zero,
                    visualDensity: VisualDensity.compact,
                  ),
                  const SizedBox(width: 8),
                  Chip(
                    label: Text(difficulty),
                    backgroundColor: Colors.orange.shade100,
                    labelStyle: Theme.of(context).textTheme.labelSmall,
                    padding: EdgeInsets.zero,
                    visualDensity: VisualDensity.compact,
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: isCorrected
                          ? Colors.green.shade100
                          : Colors.red.shade100,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          isCorrected ? Icons.check_circle : Icons.error,
                          size: 14,
                          color: isCorrected
                              ? Colors.green.shade700
                              : Colors.red.shade700,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          isCorrected ? '已订正' : '未订正',
                          style:
                              Theme.of(context).textTheme.labelSmall?.copyWith(
                                    color: isCorrected
                                        ? Colors.green.shade700
                                        : Colors.red.shade700,
                                  ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Question stem (truncated)
              Text(
                questionStem,
                style: Theme.of(context).textTheme.bodyMedium,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),

              const SizedBox(height: 12),

              // Error info
              Row(
                children: [
                  Icon(
                    Icons.error_outline,
                    size: 16,
                    color: Colors.grey.shade600,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '错误 $errorCount 次',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey.shade600,
                        ),
                  ),
                  const SizedBox(width: 16),
                  Icon(
                    Icons.access_time,
                    size: 16,
                    color: Colors.grey.shade600,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '最后错误: $lastErrorDate',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey.shade600,
                        ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
