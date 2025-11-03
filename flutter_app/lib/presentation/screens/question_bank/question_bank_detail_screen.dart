import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/question_bank_provider.dart';
import '../../../data/models/question_bank_model.dart';
import '../../../data/models/practice_session_model.dart';
import '../../../data/models/statistics_model.dart';
import '../../../data/datasources/remote/statistics_api.dart';
import '../../../data/repositories/statistics_repository.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/utils/date_formatter.dart';
import '../../../core/utils/logger.dart';

/// Question Bank Detail Screen
/// 题库详情页面
class QuestionBankDetailScreen extends StatefulWidget {
  final String bankId;

  const QuestionBankDetailScreen({
    super.key,
    required this.bankId,
  });

  @override
  State<QuestionBankDetailScreen> createState() =>
      _QuestionBankDetailScreenState();
}

class _QuestionBankDetailScreenState extends State<QuestionBankDetailScreen> {
  final StatisticsRepository _statisticsRepository = StatisticsRepository(
    api: StatisticsApi(DioClient()),
  );

  BankStatisticsModel? _statistics;
  bool _loadingStatistics = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadQuestionBank();
      _loadStatistics();
    });
  }

  Future<void> _loadQuestionBank() async {
    final provider = context.read<QuestionBankProvider>();
    await provider.getQuestionBankById(widget.bankId);
  }

  Future<void> _loadStatistics() async {
    setState(() {
      _loadingStatistics = true;
    });

    try {
      final result = await _statisticsRepository.getBankStatistics(widget.bankId);

      result.fold(
        (failure) {
          AppLogger.error('Failed to load statistics: ${failure.message}');
          setState(() {
            _loadingStatistics = false;
          });
        },
        (statistics) {
          setState(() {
            _statistics = statistics;
            _loadingStatistics = false;
          });
          AppLogger.info('Statistics loaded: ${statistics.practicedQuestions}/${statistics.totalQuestions}');
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error loading statistics: $e');
      setState(() {
        _loadingStatistics = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('题库详情'),
        actions: [
          // Info icon to show statistics and details
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: () {
              final provider = context.read<QuestionBankProvider>();
              final bank = provider.currentQuestionBank;
              if (bank != null) {
                _showBankInfoDialog(context, bank);
              }
            },
          ),
        ],
      ),
      body: Consumer<QuestionBankProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (provider.errorMessage != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.error_outline,
                    size: 64,
                    color: Colors.red.shade300,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    provider.errorMessage!,
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.red.shade700,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: _loadQuestionBank,
                    icon: const Icon(Icons.refresh),
                    label: const Text('重试'),
                  ),
                ],
              ),
            );
          }

          final bank = provider.currentQuestionBank;
          if (bank == null) {
            return const Center(
              child: Text('题库不存在'),
            );
          }

          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header
                _buildHeader(bank, context),

                // Progress Bar
                _buildProgressBar(bank),

                // Practice Options
                _buildPracticeOptions(bank, context),

                // Wrong Questions Statistics (placeholder)
                _buildWrongQuestionStats(),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildHeader(QuestionBankModel bank, BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            theme.colorScheme.primaryContainer,
            theme.colorScheme.primaryContainer.withOpacity(0.7),
          ],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Category
          if (bank.category != null)
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 6,
              ),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                bank.category!,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.onPrimary,
                ),
              ),
            ),

          const SizedBox(height: 12),

          // Title
          Text(
            bank.name,
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.onPrimaryContainer,
            ),
          ),

          const SizedBox(height: 8),

          // Description
          if (bank.description != null)
            Text(
              bank.description!,
              style: theme.textTheme.bodyLarge?.copyWith(
                color: theme.colorScheme.onPrimaryContainer.withOpacity(0.8),
              ),
            ),

          const SizedBox(height: 16),

          // Tags
          if (bank.tags != null && bank.tags!.isNotEmpty)
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: bank.tags!.map((tag) {
                return Chip(
                  label: Text(tag),
                  backgroundColor: Colors.white.withOpacity(0.9),
                  labelStyle: theme.textTheme.labelSmall,
                );
              }).toList(),
            ),
        ],
      ),
    );
  }

  Widget _buildPracticeOptions(QuestionBankModel bank, BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            '开始练习',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),

          // Sequential Practice
          _PracticeOptionCard(
            icon: Icons.format_list_numbered,
            title: '顺序练习',
            subtitle: '按照题目顺序依次练习',
            color: Colors.blue,
            onTap: () {
              Navigator.pushNamed(
                context,
                '/practice',
                arguments: {
                  'bankId': bank.id,
                  'mode': PracticeMode.sequential,
                },
              );
            },
          ),

          const SizedBox(height: 12),

          // Random Practice
          _PracticeOptionCard(
            icon: Icons.shuffle,
            title: '随机练习',
            subtitle: '随机打乱题目顺序练习',
            color: Colors.orange,
            onTap: () {
              Navigator.pushNamed(
                context,
                '/practice',
                arguments: {
                  'bankId': bank.id,
                  'mode': PracticeMode.random,
                },
              );
            },
          ),

          const SizedBox(height: 12),

          // Unpracticed
          _PracticeOptionCard(
            icon: Icons.new_releases_outlined,
            title: '未练习题目',
            subtitle: '只练习从未做过的题目',
            color: Colors.pink,
            onTap: () {
              Navigator.pushNamed(
                context,
                '/practice',
                arguments: {
                  'bankId': bank.id,
                  'mode': PracticeMode.unpracticed,
                },
              );
            },
          ),

          const SizedBox(height: 12),

          // Wrong Questions
          _PracticeOptionCard(
            icon: Icons.error_outline,
            title: '错题本',
            subtitle: '查看和练习做错的题目',
            color: Colors.red,
            onTap: () {
              Navigator.pushNamed(
                context,
                '/wrong-questions',
                arguments: {
                  'bankId': bank.id,
                },
              );
            },
          ),

          const SizedBox(height: 12),

          // Favorites
          _PracticeOptionCard(
            icon: Icons.star_outline,
            title: '收藏列表',
            subtitle: '查看收藏的题目',
            color: Colors.amber,
            onTap: () {
              Navigator.pushNamed(
                context,
                '/favorites',
                arguments: {
                  'bankId': bank.id,
                },
              );
            },
          ),

          const SizedBox(height: 12),

          // Browse Mode
          _PracticeOptionCard(
            icon: Icons.visibility_outlined,
            title: '浏览题目',
            subtitle: '直接查看题目和答案，无需作答',
            color: Colors.purple,
            onTap: () {
              Navigator.pushNamed(
                context,
                '/browse-questions',
                arguments: {
                  'bankId': bank.id,
                },
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildProgressBar(QuestionBankModel bank) {
    final totalQuestions = _statistics?.totalQuestions ?? bank.totalQuestions ?? 0;
    final practicedQuestions = _statistics?.practicedQuestions ?? 0;
    final progress = totalQuestions > 0 ? practicedQuestions / totalQuestions : 0.0;

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '学习进度',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              Text(
                '$practicedQuestions/$totalQuestions',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey.shade600,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: progress,
            minHeight: 8,
            backgroundColor: Colors.grey.shade200,
            borderRadius: BorderRadius.circular(4),
          ),
          const SizedBox(height: 4),
          Text(
            '${(progress * 100).toStringAsFixed(0)}% 已完成',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey.shade600,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildWrongQuestionStats() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            '错题统计',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              '功能开发中...',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade600,
                  ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  void _showBankInfoDialog(BuildContext context, QuestionBankModel bank) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Title
                Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '题库信息',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Total Questions
                _StatCard(
                  icon: Icons.quiz_outlined,
                  label: '总题数',
                  value: '${bank.totalQuestions ?? 0}',
                  color: Colors.blue,
                ),

                const SizedBox(height: 24),
                const Divider(),
                const SizedBox(height: 24),

                // Details Section
                Text(
                  '详细信息',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 16),
                _DetailRow(
                  label: '题库ID',
                  value: bank.id,
                ),
                _DetailRow(
                  label: '可见性',
                  value: bank.isPublic == true ? '公开' : '私有',
                ),
                if (bank.createdAt != null)
                  _DetailRow(
                    label: '创建时间',
                    value: DateFormatter.formatDateTime(
                      DateTime.parse(bank.createdAt!),
                    ),
                  ),
                if (bank.updatedAt != null)
                  _DetailRow(
                    label: '更新时间',
                    value: DateFormatter.formatDateTime(
                      DateTime.parse(bank.updatedAt!),
                    ),
                  ),

                const SizedBox(height: 24),
                FilledButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('关闭'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Practice Option Card
class _PracticeOptionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _PracticeOptionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 32,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey.shade600,
                          ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: Colors.grey.shade400,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Stat Card
class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(
              icon,
              color: color,
              size: 32,
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey.shade600,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Detail Row
class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade600,
                  ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}
