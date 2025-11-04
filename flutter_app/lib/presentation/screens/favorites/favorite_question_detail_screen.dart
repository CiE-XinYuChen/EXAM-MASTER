import 'package:flutter/material.dart';
import '../../../data/models/favorite_model.dart';
import '../../../data/repositories/favorites_repository.dart';
import '../../../data/datasources/remote/favorites_api.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/utils/logger.dart';

/// Favorite Question Detail Screen
/// 收藏题目详情页面
class FavoriteQuestionDetailScreen extends StatefulWidget {
  final FavoriteModel favorite;

  const FavoriteQuestionDetailScreen({
    super.key,
    required this.favorite,
  });

  @override
  State<FavoriteQuestionDetailScreen> createState() =>
      _FavoriteQuestionDetailScreenState();
}

class _FavoriteQuestionDetailScreenState
    extends State<FavoriteQuestionDetailScreen> {
  final FavoritesRepository _repository = FavoritesRepository(
    api: FavoritesApi(DioClient()),
  );

  final TextEditingController _noteController = TextEditingController();
  bool _isUpdating = false;

  @override
  void initState() {
    super.initState();
    _noteController.text = widget.favorite.note ?? '';
  }

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _updateNote() async {
    if (_noteController.text == widget.favorite.note) {
      Navigator.pop(context);
      return;
    }

    setState(() {
      _isUpdating = true;
    });

    final result = await _repository.updateFavoriteNote(
      widget.favorite.id,
      _noteController.text,
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
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('备注已更新')),
        );
        AppLogger.info('Updated favorite note');
        Navigator.pop(context, true); // Return true to indicate changes
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('第 ${widget.favorite.questionNumber ?? '?'} 题'),
      ),
      body: _isUpdating
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Favorite info card
                  _buildFavoriteInfoCard(),
                  const SizedBox(height: 16),

                  // Question stem
                  _buildSectionTitle('题目'),
                  const SizedBox(height: 8),
                  _buildQuestionStem(),
                  const SizedBox(height: 24),

                  // Options (if available)
                  if (widget.favorite.questionOptions != null &&
                      widget.favorite.questionOptions!.isNotEmpty) ...[
                    _buildSectionTitle('选项'),
                    const SizedBox(height: 8),
                    _buildOptions(),
                    const SizedBox(height: 24),
                  ],

                  // Explanation (if available)
                  if (widget.favorite.questionExplanation != null &&
                      widget.favorite.questionExplanation!.isNotEmpty) ...[
                    _buildSectionTitle('题目解析'),
                    const SizedBox(height: 8),
                    _buildExplanation(),
                    const SizedBox(height: 24),
                  ],

                  // Note section
                  _buildSectionTitle('我的备注'),
                  const SizedBox(height: 8),
                  _buildNoteSection(),
                  const SizedBox(height: 24),

                  // Tags (if available)
                  if (widget.favorite.questionTags != null &&
                      widget.favorite.questionTags!.isNotEmpty) ...[
                    _buildSectionTitle('相关知识点'),
                    const SizedBox(height: 8),
                    _buildTags(),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildFavoriteInfoCard() {
    return Card(
      color: Colors.amber.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              Icons.star,
              color: Colors.amber.shade700,
              size: 32,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '收藏题目',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.amber.shade900,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '收藏时间: ${widget.favorite.createdAt.substring(0, 10)}',
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
                  label: Text(_getQuestionTypeLabel(widget.favorite.questionType)),
                  backgroundColor: Colors.blue.shade100,
                  labelStyle: Theme.of(context).textTheme.labelSmall,
                  padding: EdgeInsets.zero,
                  visualDensity: VisualDensity.compact,
                ),
                const SizedBox(width: 8),
                if (widget.favorite.questionDifficulty != null)
                  Chip(
                    label: Text(widget.favorite.questionDifficulty!),
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
              widget.favorite.questionStem,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoteSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: TextField(
          controller: _noteController,
          decoration: const InputDecoration(
            hintText: '添加备注...',
            border: InputBorder.none,
          ),
          maxLines: null,
          minLines: 3,
          onChanged: (value) {
            setState(() {}); // Rebuild to show/hide save button
          },
        ),
      ),
    );
  }

  Widget _buildTags() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: widget.favorite.questionTags!
          .map((tag) => Chip(
                label: Text(tag),
                backgroundColor: Colors.blue.shade100,
                labelStyle: Theme.of(context).textTheme.bodySmall,
              ))
          .toList(),
    );
  }

  Widget _buildOptions() {
    return Column(
      children: widget.favorite.questionOptions!.map((option) {
        final isCorrect = option.isCorrect ?? false;
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isCorrect ? Colors.green.shade50 : Colors.grey.shade50,
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
      }).toList(),
    );
  }

  Widget _buildExplanation() {
    return Card(
      color: Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  color: Colors.orange.shade700,
                ),
                const SizedBox(width: 8),
                Text(
                  '解析',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.orange.shade700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              widget.favorite.questionExplanation!,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    height: 1.6,
                  ),
            ),
          ],
        ),
      ),
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
