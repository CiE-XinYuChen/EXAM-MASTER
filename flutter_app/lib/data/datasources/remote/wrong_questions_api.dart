import 'package:dio/dio.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/utils/logger.dart';
import '../../models/wrong_question_model.dart';

/// Wrong Questions API
/// 错题相关API接口
class WrongQuestionsApi {
  final DioClient _dioClient;

  WrongQuestionsApi(this._dioClient);

  /// Get user's wrong questions
  /// 获取用户的错题列表
  ///
  /// [page] - Page number (starts from 1)
  /// [pageSize] - Items per page
  /// [bankId] - Filter by question bank ID
  /// [corrected] - Filter by corrected status
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<WrongQuestionListResponse> getWrongQuestions({
    int page = 1,
    int pageSize = 20,
    String? bankId,
    bool? corrected,
  }) async {
    try {
      AppLogger.info('WrongQuestionsApi.getWrongQuestions: page=$page');

      final queryParams = <String, dynamic>{
        'skip': (page - 1) * pageSize,
        'limit': pageSize,
      };

      if (bankId != null && bankId.isNotEmpty) {
        queryParams['bank_id'] = bankId;
      }
      if (corrected != null) {
        queryParams['corrected'] = corrected;
      }

      final response = await _dioClient.get(
        ApiConstants.wrongQuestions,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get wrong questions successful');
        return WrongQuestionListResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get wrong questions',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get wrong questions error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Mark a wrong question as corrected or uncorrected
  /// 标记错题为已订正/未订正
  ///
  /// [wrongQuestionId] - Wrong question ID
  /// [corrected] - True to mark as corrected, false to mark as uncorrected
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<bool> markCorrected(String wrongQuestionId, bool corrected) async {
    try {
      AppLogger.info('WrongQuestionsApi.markCorrected: $wrongQuestionId, corrected=$corrected');

      final response = await _dioClient.put(
        ApiConstants.wrongQuestionCorrect(wrongQuestionId),
        data: {'corrected': corrected},
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Mark corrected successful');
        return true;
      } else {
        throw ServerException(
          message: 'Failed to mark corrected',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Mark corrected error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get wrong question analysis
  /// 获取错题分析
  ///
  /// [bankId] - Optional question bank ID filter
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<WrongQuestionAnalysisModel> getAnalysis({String? bankId}) async {
    try {
      AppLogger.info('WrongQuestionsApi.getAnalysis');

      final queryParams = <String, dynamic>{};
      if (bankId != null && bankId.isNotEmpty) {
        queryParams['bank_id'] = bankId;
      }

      final response = await _dioClient.get(
        ApiConstants.wrongQuestionsAnalysis,
        queryParameters: queryParams.isEmpty ? null : queryParams,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get wrong question analysis successful');
        return WrongQuestionAnalysisModel.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get analysis',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get analysis error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Delete a wrong question record
  /// 删除错题记录
  ///
  /// [wrongQuestionId] - Wrong question ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<void> deleteWrongQuestion(String wrongQuestionId) async {
    try {
      AppLogger.info('WrongQuestionsApi.deleteWrongQuestion: $wrongQuestionId');

      final response = await _dioClient.delete(
        ApiConstants.wrongQuestionById(wrongQuestionId),
      );

      if (response.statusCode == 200 || response.statusCode == 204) {
        AppLogger.debug('Delete wrong question successful');
      } else {
        throw ServerException(
          message: 'Failed to delete wrong question',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Delete wrong question error: ${e.message}');
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
