import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/question_bank_provider.dart';
import '../../../data/models/question_bank_model.dart';
import '../../../core/utils/date_formatter.dart';

/// Home Tab
/// 首页标签 - 显示题库列表
class HomeTab extends StatefulWidget {
  const HomeTab({super.key});

  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  final TextEditingController _searchController = TextEditingController();
  String? _searchQuery;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadQuestionBanks();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadQuestionBanks() async {
    final provider = context.read<QuestionBankProvider>();
    await provider.getQuestionBanks(search: _searchQuery);
  }

  Future<void> _showActivationDialog() async {
    final controller = TextEditingController();

    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('激活题库'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('请输入激活码以访问题库'),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: '激活码',
                hintText: '请输入激活码',
                border: OutlineInputBorder(),
              ),
              autofocus: true,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          FilledButton(
            onPressed: () async {
              if (controller.text.trim().isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('请输入激活码')),
                );
                return;
              }

              Navigator.pop(context, true);

              final provider = context.read<QuestionBankProvider>();
              final success = await provider.activateCode(controller.text.trim());

              if (mounted) {
                if (success) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('激活成功！')),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(provider.errorMessage ?? '激活失败'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            child: const Text('激活'),
          ),
        ],
      ),
    );
  }

  void _performSearch(String query) {
    setState(() {
      _searchQuery = query.isEmpty ? null : query;
    });
    _loadQuestionBanks();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('题库'),
        actions: [
          IconButton(
            icon: const Icon(Icons.vpn_key_outlined),
            onPressed: _showActivationDialog,
            tooltip: '激活题库',
          ),
        ],
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: '搜索题库...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _performSearch('');
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: Colors.grey.shade100,
              ),
              onSubmitted: _performSearch,
            ),
          ),

          // Question Banks List
          Expanded(
            child: Consumer<QuestionBankProvider>(
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
                          onPressed: _loadQuestionBanks,
                          icon: const Icon(Icons.refresh),
                          label: const Text('重试'),
                        ),
                      ],
                    ),
                  );
                }

                if (provider.questionBanks.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.library_books_outlined,
                          size: 80,
                          color: Colors.grey.shade400,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          '暂无题库',
                          style: TextStyle(
                            fontSize: 20,
                            color: Colors.grey.shade600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '使用激活码解锁题库',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade400,
                          ),
                        ),
                        const SizedBox(height: 24),
                        FilledButton.icon(
                          onPressed: _showActivationDialog,
                          icon: const Icon(Icons.vpn_key_outlined),
                          label: const Text('激活题库'),
                        ),
                      ],
                    ),
                  );
                }

                return RefreshIndicator(
                  onRefresh: _loadQuestionBanks,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: provider.questionBanks.length,
                    itemBuilder: (context, index) {
                      final bank = provider.questionBanks[index];
                      return _QuestionBankCard(
                        bank: bank,
                        onTap: () {
                          Navigator.pushNamed(
                            context,
                            '/question-bank-detail',
                            arguments: bank.id,
                          );
                        },
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

/// Question Bank Card Widget
class _QuestionBankCard extends StatelessWidget {
  final QuestionBankModel bank;
  final VoidCallback onTap;

  const _QuestionBankCard({
    required this.bank,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

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
              // Title and category
              Row(
                children: [
                  Expanded(
                    child: Text(
                      bank.name,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (bank.category != null)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.primaryContainer,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        bank.category!,
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.onPrimaryContainer,
                        ),
                      ),
                    ),
                ],
              ),

              // Description
              if (bank.description != null) ...[
                const SizedBox(height: 8),
                Text(
                  bank.description!,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade700,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],

              // Tags
              if (bank.tags != null && bank.tags!.isNotEmpty) ...[
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: bank.tags!.take(3).map((tag) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade200,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        tag,
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: Colors.grey.shade700,
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],

              // Stats
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    Icons.quiz_outlined,
                    size: 16,
                    color: Colors.grey.shade600,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${bank.totalQuestions ?? 0} 题',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(width: 16),
                  if (bank.updatedAt != null) ...[
                    Icon(
                      Icons.update,
                      size: 16,
                      color: Colors.grey.shade600,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '更新于 ${DateFormatter.formatRelativeTime(DateTime.parse(bank.updatedAt!))}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
