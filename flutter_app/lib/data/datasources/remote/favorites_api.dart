import 'package:dio/dio.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/utils/logger.dart';
import '../../models/favorite_model.dart';

/// Favorites API
/// 收藏相关API接口
class FavoritesApi {
  final DioClient _dioClient;

  FavoritesApi(this._dioClient);

  /// Get user's favorites
  /// 获取用户的收藏列表
  ///
  /// [page] - Page number (starts from 1)
  /// [pageSize] - Items per page
  /// [bankId] - Filter by question bank ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<FavoriteListResponse> getFavorites({
    int page = 1,
    int pageSize = 20,
    String? bankId,
  }) async {
    try {
      AppLogger.info('FavoritesApi.getFavorites: page=$page');

      final queryParams = <String, dynamic>{
        'skip': (page - 1) * pageSize,
        'limit': pageSize,
      };

      if (bankId != null && bankId.isNotEmpty) {
        queryParams['bank_id'] = bankId;
      }

      final response = await _dioClient.get(
        ApiConstants.favorites,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get favorites successful');
        return FavoriteListResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get favorites',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get favorites error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Add a question to favorites
  /// 添加题目到收藏
  ///
  /// [request] - Add favorite request
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [ValidationException]
  Future<AddFavoriteResponse> addFavorite(AddFavoriteRequest request) async {
    try {
      AppLogger.info('FavoritesApi.addFavorite: questionId=${request.questionId}');

      final response = await _dioClient.post(
        ApiConstants.favorites,
        data: request.toJson(),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        AppLogger.debug('Add favorite successful');
        return AddFavoriteResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to add favorite',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Add favorite error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Remove a favorite
  /// 移除收藏
  ///
  /// [favoriteId] - Favorite ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<void> removeFavorite(String favoriteId) async {
    try {
      AppLogger.info('FavoritesApi.removeFavorite: $favoriteId');

      final response = await _dioClient.delete(
        ApiConstants.favoriteById(favoriteId),
      );

      if (response.statusCode == 200 || response.statusCode == 204) {
        AppLogger.debug('Remove favorite successful');
      } else {
        throw ServerException(
          message: 'Failed to remove favorite',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Remove favorite error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Update favorite note
  /// 更新收藏备注
  ///
  /// [favoriteId] - Favorite ID
  /// [request] - Update note request
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<void> updateNote(
    String favoriteId,
    UpdateFavoriteNoteRequest request,
  ) async {
    try {
      AppLogger.info('FavoritesApi.updateNote: $favoriteId');

      final response = await _dioClient.patch(
        ApiConstants.favoriteById(favoriteId),
        data: request.toJson(),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Update note successful');
      } else {
        throw ServerException(
          message: 'Failed to update note',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Update note error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Check if a question is favorited
  /// 检查题目是否已收藏
  ///
  /// [questionId] - Question ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<bool> isFavorited(String questionId) async {
    try {
      AppLogger.info('FavoritesApi.isFavorited: $questionId');

      final response = await _dioClient.get(
        ApiConstants.favoriteCheck(questionId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Check favorited successful');
        return response.data['is_favorited'] ?? false;
      } else {
        throw ServerException(
          message: 'Failed to check favorite status',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Check favorited error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Handle exceptions
  Exception _handleException(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return TimeoutException(message: 'Request timeout');
    }

    if (e.type == DioExceptionType.connectionError) {
      return NetworkException(message: 'Network connection error');
    }

    final statusCode = e.response?.statusCode;
    final message = e.response?.data?['message'] ?? e.message ?? 'Unknown error';

    if (statusCode != null) {
      switch (statusCode) {
        case 400:
          return ValidationException(message: message, statusCode: statusCode);
        case 401:
          return AuthenticationException(message: message, statusCode: statusCode);
        case 403:
          return AuthorizationException(message: message, statusCode: statusCode);
        case 404:
          return NotFoundException(message: message, statusCode: statusCode);
        case 422:
          final errors = e.response?.data?['errors'];
          return ValidationException(
            message: errors != null ? errors.toString() : message,
            statusCode: statusCode,
          );
        default:
          if (statusCode >= 500) {
            return ServerException(message: message, statusCode: statusCode);
          }
      }
    }

    return UnknownException(message: message);
  }
}
