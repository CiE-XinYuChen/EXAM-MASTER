import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:card_swiper/card_swiper.dart';
import '../../providers/practice_provider.dart';
import '../../../data/models/practice_session_model.dart';
import '../../../data/models/question_model.dart';
import '../../widgets/practice/question_card.dart';

/// Practice Screen
/// 答题练习页面
class PracticeScreen extends StatefulWidget {
  final String bankId;
  final PracticeMode mode;

  const PracticeScreen({
    super.key,
    required this.bankId,
    required this.mode,
  });

  @override
  State<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends State<PracticeScreen> {
  final SwiperController _swiperController = SwiperController();
  bool _isInitialized = false;
  Timer? _progressSaveTimer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initSession();
    });
    // Auto-save progress every 30 seconds
    _progressSaveTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _saveProgress(),
    );
  }

  @override
  void dispose() {
    _progressSaveTimer?.cancel();
    _saveProgress(); // Save one last time before disposing
    _swiperController.dispose();
    super.dispose();
  }

  Future<void> _initSession() async {
    final provider = context.read<PracticeProvider>();
    final success = await provider.createSession(
      bankId: widget.bankId,
      mode: widget.mode,
    );

    if (success) {
      setState(() {
        _isInitialized = true;
      });
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(provider.errorMessage ?? '创建答题会话失败'),
          backgroundColor: Colors.red,
        ),
      );
      Navigator.pop(context);
    }
  }

  void _onIndexChanged(int index) {
    final provider = context.read<PracticeProvider>();
    provider.goToQuestion(index);
  }

  /// Auto-save progress periodically
  Future<void> _saveProgress() async {
    if (!mounted || !_isInitialized) return;

    try {
      final provider = context.read<PracticeProvider>();
      if (provider.currentSession != null) {
        // Progress is automatically saved through answer submissions
        // The current index and answered questions are tracked in the session
        // This method ensures the session state is persisted periodically
        await provider.pauseSession();
        // Immediately resume to keep the session active
        await provider.resumeSession();
      }
    } catch (e) {
      // Silently fail - auto-save should not interrupt user experience
      // The data is still safe as answers are saved on submission
    }
  }

  Future<void> _showExitDialog() async {
    // 直接保存并退出，不显示对话框
    final provider = context.read<PracticeProvider>();
    await provider.pauseSession();
    if (mounted) {
      Navigator.pop(context);
    }
  }

  Future<void> _completeSession() async {
    final provider = context.read<PracticeProvider>();

    // Check if all questions are answered
    if (provider.answeredCount < provider.totalQuestions) {
      final result = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('提示'),
          content: Text('还有 ${provider.totalQuestions - provider.answeredCount} 道题未作答，确定要提交吗？'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('继续答题'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('确定提交'),
            ),
          ],
        ),
      );

      if (result != true) return;
    }

    final success = await provider.completeSession();

    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('答题完成！')),
        );
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(provider.errorMessage ?? '提交失败'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async {
        await _showExitDialog();
        return false;
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(_getModeTitle()),
          leading: IconButton(
            icon: const Icon(Icons.close),
            onPressed: _showExitDialog,
          ),
          actions: [
            // Question list button
            IconButton(
              icon: const Icon(Icons.list_alt),
              onPressed: () {
                _showQuestionList();
              },
            ),
          ],
        ),
        body: Consumer<PracticeProvider>(
          builder: (context, provider, child) {
            if (!_isInitialized || provider.isLoading) {
              return const Center(
                child: CircularProgressIndicator(),
              );
            }

            if (provider.questions.isEmpty) {
              return Center(
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
              );
            }

            return Column(
              children: [
                // Progress bar
                _buildProgressBar(provider),

                // Question cards
                Expanded(
                  child: Swiper(
                    controller: _swiperController,
                    itemCount: provider.questions.length,
                    onIndexChanged: _onIndexChanged,
                    index: provider.currentQuestionIndex,
                    loop: false,
                    itemBuilder: (context, index) {
                      final question = provider.questions[index];
                      return QuestionCard(
                        question: question,
                        questionNumber: index + 1,
                        totalQuestions: provider.totalQuestions,
                      );
                    },
                  ),
                ),

                // Navigation buttons
                _buildNavigationButtons(provider),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildProgressBar(PracticeProvider provider) {
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
              Text(
                '进度: ${provider.currentQuestionIndex + 1}/${provider.totalQuestions}',
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const Spacer(),
              Text(
                '已答: ${provider.answeredCount}/${provider.totalQuestions}',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: provider.totalQuestions > 0
                ? (provider.currentQuestionIndex + 1) / provider.totalQuestions
                : 0.0,
            backgroundColor: Colors.grey.shade200,
            minHeight: 6,
            borderRadius: BorderRadius.circular(3),
          ),
        ],
      ),
    );
  }

  Widget _buildNavigationButtons(PracticeProvider provider) {
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
              onPressed: provider.hasPreviousQuestion
                  ? () {
                      _swiperController.previous();
                    }
                  : null,
              icon: const Icon(Icons.arrow_back),
              label: const Text('上一题'),
            ),
          ),
          const SizedBox(width: 16),

          // Next or Submit button
          Expanded(
            flex: 2,
            child: provider.isLastQuestion
                ? FilledButton.icon(
                    onPressed: _completeSession,
                    icon: const Icon(Icons.check),
                    label: const Text('完成答题'),
                  )
                : FilledButton.icon(
                    onPressed: provider.hasNextQuestion
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

  void _showQuestionList() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) {
          return Consumer<PracticeProvider>(
            builder: (context, provider, child) {
              return Column(
                children: [
                  // Header
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      border: Border(
                        bottom: BorderSide(
                          color: Colors.grey.shade200,
                        ),
                      ),
                    ),
                    child: Row(
                      children: [
                        const Text(
                          '题目列表',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const Spacer(),
                        IconButton(
                          icon: const Icon(Icons.close),
                          onPressed: () => Navigator.pop(context),
                        ),
                      ],
                    ),
                  ),

                  // Question grid
                  Expanded(
                    child: GridView.builder(
                      controller: scrollController,
                      padding: const EdgeInsets.all(16),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 5,
                        mainAxisSpacing: 12,
                        crossAxisSpacing: 12,
                        childAspectRatio: 1,
                      ),
                      itemCount: provider.totalQuestions,
                      itemBuilder: (context, index) {
                        final question = provider.questions[index];
                        final isAnswered = provider.getAnswer(question.id) != null;
                        final isCurrent = index == provider.currentQuestionIndex;

                        return InkWell(
                          onTap: () {
                            _swiperController.move(index);
                            Navigator.pop(context);
                          },
                          child: Container(
                            decoration: BoxDecoration(
                              color: isCurrent
                                  ? Theme.of(context).colorScheme.primary
                                  : isAnswered
                                      ? Colors.green.shade100
                                      : Colors.grey.shade200,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: isCurrent
                                    ? Theme.of(context).colorScheme.primary
                                    : isAnswered
                                        ? Colors.green
                                        : Colors.grey.shade300,
                                width: isCurrent ? 2 : 1,
                              ),
                            ),
                            child: Center(
                              child: Text(
                                '${index + 1}',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: isCurrent
                                      ? Colors.white
                                      : isAnswered
                                          ? Colors.green.shade700
                                          : Colors.grey.shade700,
                                ),
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              );
            },
          );
        },
      ),
    );
  }

  String _getModeTitle() {
    switch (widget.mode) {
      case PracticeMode.sequential:
        return '顺序练习';
      case PracticeMode.random:
        return '随机练习';
      case PracticeMode.wrongOnly:
        return '错题练习';
      case PracticeMode.favoriteOnly:
        return '收藏练习';
      case PracticeMode.unpracticed:
        return '未练习题目';
    }
  }
}
