import 'package:flutter/material.dart';
import '../../../data/models/practice_session_model.dart';
import '../../../data/models/favorite_model.dart';
import '../../../data/datasources/remote/favorites_api.dart';
import '../../../data/repositories/favorites_repository.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/utils/logger.dart';
import 'favorite_question_detail_screen.dart';

/// Favorites List Screen
/// 收藏列表页面
class FavoritesListScreen extends StatefulWidget {
  final String bankId;

  const FavoritesListScreen({
    super.key,
    required this.bankId,
  });

  @override
  State<FavoritesListScreen> createState() => _FavoritesListScreenState();
}

class _FavoritesListScreenState extends State<FavoritesListScreen> {
  final FavoritesRepository _repository = FavoritesRepository(
    api: FavoritesApi(DioClient()),
  );

  List<FavoriteModel> _favorites = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadFavorites();
    });
  }

  Future<void> _loadFavorites() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final result = await _repository.getFavorites(
        page: 1,
        pageSize: 1000,
        bankId: widget.bankId,
      );

      result.fold(
        (failure) {
          setState(() {
            _error = failure.message;
            _isLoading = false;
          });
          AppLogger.error('Failed to load favorites: ${failure.message}');
        },
        (response) {
          setState(() {
            _favorites = response.favorites;
            _isLoading = false;
          });
          AppLogger.info('Loaded ${_favorites.length} favorites');
        },
      );
    } catch (e) {
      setState(() {
        _error = '加载失败: $e';
        _isLoading = false;
      });
      AppLogger.error('Unexpected error loading favorites: $e');
    }
  }

  Future<void> _deleteFavorite(String favoriteId, int index) async {
    final result = await _repository.removeFavorite(favoriteId);

    result.fold(
      (failure) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('删除失败: ${failure.message}')),
        );
      },
      (_) {
        setState(() {
          _favorites.removeAt(index);
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('已取消收藏')),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('收藏列表'),
        actions: [
          // Practice favorites (both browsing and doing)
          if (_favorites.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.edit_outlined),
              tooltip: '开始练习',
              onPressed: () {
                Navigator.pushNamed(
                  context,
                  '/practice',
                  arguments: {
                    'bankId': widget.bankId,
                    'mode': PracticeMode.favoriteOnly,
                  },
                );
              },
            ),
        ],
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
                        onPressed: _loadFavorites,
                        child: const Text('重试'),
                      ),
                    ],
                  ),
                )
              : Column(
                  children: [
                    // Summary Card
                    _buildSummaryCard(),

                    // Favorites List
                    Expanded(
                      child: _buildFavoritesList(),
                    ),
                  ],
                ),
    );
  }

  Widget _buildSummaryCard() {
    final favoritesCount = _favorites.length;

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.amber.shade100,
            Colors.amber.shade50,
          ],
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.amber,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.star,
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
                  '收藏题目',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  '共 $favoritesCount 道题目',
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

  Widget _buildFavoritesList() {
    if (_favorites.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.star_outline, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text('还没有收藏题目',
                style: TextStyle(fontSize: 18, color: Colors.grey.shade600)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: _favorites.length,
      itemBuilder: (context, index) {
        final favorite = _favorites[index];
        return Dismissible(
          key: Key(favorite.id),
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
            _deleteFavorite(favorite.id, index);
          },
          child: _FavoriteQuestionCard(
            questionNumber: favorite.questionNumber ?? (index + 1),
            questionStem: favorite.questionStem,
            questionType: _getQuestionTypeLabel(favorite.questionType),
            difficulty: favorite.questionDifficulty ?? '未知',
            onTap: () async {
              // Navigate to favorite question detail screen
              final result = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => FavoriteQuestionDetailScreen(
                    favorite: favorite,
                  ),
                ),
              );

              // Refresh list if note was updated
              if (result == true) {
                _loadFavorites();
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

/// Favorite Question Card
class _FavoriteQuestionCard extends StatelessWidget {
  final int questionNumber;
  final String questionStem;
  final String questionType;
  final String difficulty;
  final VoidCallback onTap;

  const _FavoriteQuestionCard({
    required this.questionNumber,
    required this.questionStem,
    required this.questionType,
    required this.difficulty,
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
                  const Icon(
                    Icons.star,
                    color: Colors.amber,
                    size: 20,
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
            ],
          ),
        ),
      ),
    );
  }
}
