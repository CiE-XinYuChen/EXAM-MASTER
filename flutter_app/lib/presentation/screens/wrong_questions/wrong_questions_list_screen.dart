import 'package:flutter/material.dart';
import '../../../data/models/practice_session_model.dart';

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
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadWrongQuestions();
    });
  }

  Future<void> _loadWrongQuestions() async {
    // TODO: Implement wrong questions loading
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('错题本'),
        actions: [
          // Practice wrong questions
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            tooltip: '开始练习',
            onPressed: () {
              Navigator.pushNamed(
                context,
                '/practice',
                arguments: {
                  'bankId': widget.bankId,
                  'mode': PracticeMode.wrongOnly,
                },
              );
            },
          ),
        ],
      ),
      body: Column(
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
    // TODO: Get actual count from provider
    final wrongQuestionsCount = 0;
    final correctedCount = 0;

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
              selected: const {'all'},
              onSelectionChanged: (Set<String> newSelection) {
                // TODO: Filter wrong questions
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWrongQuestionsList() {
    // TODO: Implement actual list from provider
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 0, // Placeholder
      itemBuilder: (context, index) {
        return Dismissible(
          key: Key('wrong_question_$index'),
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
            // TODO: Remove from wrong questions
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('已从错题本删除')),
            );
          },
          child: _WrongQuestionCard(
            questionNumber: index + 1,
            questionStem: '题目 ${index + 1}',
            questionType: '单选题',
            difficulty: '简单',
            errorCount: 2,
            isCorrected: index % 2 == 0,
            lastErrorDate: '2025-11-03',
            onTap: () {
              // TODO: Navigate to question detail or practice
            },
          ),
        );
      },
    );
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
