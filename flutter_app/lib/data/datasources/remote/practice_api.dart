import 'package:dio/dio.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/utils/logger.dart';
import '../../models/practice_session_model.dart';
import '../../models/answer_record_model.dart';

/// Practice API
/// 答题练习相关API接口
class PracticeApi {
  final DioClient _dioClient;

  PracticeApi(this._dioClient);

  /// Create a new practice session
  /// 创建新的答题会话
  ///
  /// [request] - Create practice session request
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [ValidationException]
  Future<CreatePracticeSessionResponse> createSession(
    CreatePracticeSessionRequest request,
  ) async {
    try {
      AppLogger.info('PracticeApi.createSession: bankId=${request.bankId}, mode=${request.mode}');

      final response = await _dioClient.post(
        ApiConstants.practiceSessions,
        data: request.toJson(),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        AppLogger.debug('Create session successful');
        // Backend returns PracticeSessionResponse, adapt to CreatePracticeSessionResponse
        final sessionData = response.data as Map<String, dynamic>;
        return CreatePracticeSessionResponse(
          success: true,
          sessionId: sessionData['id'] as String,
          totalQuestions: sessionData['total_questions'] as int,
          mode: sessionData['mode'] as String,
          message: '会话创建成功',
        );
      } else {
        throw ServerException(
          message: 'Failed to create session',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Create session error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get practice session by ID
  /// 根据ID获取答题会话
  ///
  /// [sessionId] - Practice session ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<PracticeSessionModel> getSession(String sessionId) async {
    try {
      AppLogger.info('PracticeApi.getSession: $sessionId');

      final response = await _dioClient.get(
        ApiConstants.practiceSessionById(sessionId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get session successful');
        return PracticeSessionModel.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get session',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get session error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get user's practice sessions
  /// 获取用户的答题会话列表
  ///
  /// [page] - Page number (starts from 1)
  /// [pageSize] - Items per page
  /// [bankId] - Filter by question bank ID
  /// [status] - Filter by session status
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<List<PracticeSessionModel>> getMySessions({
    int page = 1,
    int pageSize = 20,
    String? bankId,
    String? status,
  }) async {
    try {
      AppLogger.info('PracticeApi.getMySessions: page=$page');

      final queryParams = <String, dynamic>{
        'skip': (page - 1) * pageSize,
        'limit': pageSize,
      };

      if (bankId != null && bankId.isNotEmpty) {
        queryParams['bank_id'] = bankId;
      }
      if (status != null && status.isNotEmpty) {
        queryParams['status'] = status;
      }

      final response = await _dioClient.get(
        ApiConstants.practiceSessions,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get my sessions successful');
        final List<dynamic> data = response.data;
        return data.map((json) => PracticeSessionModel.fromJson(json)).toList();
      } else {
        throw ServerException(
          message: 'Failed to get sessions',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get my sessions error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Submit answer for a question
  /// 提交题目答案
  ///
  /// [sessionId] - Practice session ID
  /// [request] - Submit answer request
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [ValidationException]
  Future<SubmitAnswerResponse> submitAnswer(
    String sessionId,
    SubmitAnswerRequest request,
  ) async {
    try {
      AppLogger.info('PracticeApi.submitAnswer: sessionId=$sessionId, questionId=${request.questionId}');

      final response = await _dioClient.post(
        ApiConstants.practiceSessionSubmit(sessionId),
        data: request.toJson(),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Submit answer successful');
        return SubmitAnswerResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to submit answer',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Submit answer error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Complete a practice session
  /// 完成答题会话
  ///
  /// [sessionId] - Practice session ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<Map<String, dynamic>> completeSession(String sessionId) async {
    try {
      AppLogger.info('PracticeApi.completeSession: $sessionId');

      final response = await _dioClient.post(
        ApiConstants.practiceSessionComplete(sessionId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Complete session successful');
        return response.data;
      } else {
        throw ServerException(
          message: 'Failed to complete session',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Complete session error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get answer history for a session
  /// 获取会话的答题记录
  ///
  /// [sessionId] - Practice session ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<AnswerHistoryResponse> getAnswerHistory(String sessionId) async {
    try {
      AppLogger.info('PracticeApi.getAnswerHistory: $sessionId');

      final response = await _dioClient.get(
        ApiConstants.practiceSessionHistory(sessionId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get answer history successful');
        return AnswerHistoryResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get answer history',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get answer history error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Pause a practice session
  /// 暂停答题会话
  ///
  /// [sessionId] - Practice session ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<Map<String, dynamic>> pauseSession(String sessionId) async {
    try {
      AppLogger.info('PracticeApi.pauseSession: $sessionId');

      final response = await _dioClient.post(
        ApiConstants.practiceSessionPause(sessionId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Pause session successful');
        return response.data;
      } else {
        throw ServerException(
          message: 'Failed to pause session',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Pause session error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Resume a practice session
  /// 恢复答题会话
  ///
  /// [sessionId] - Practice session ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<Map<String, dynamic>> resumeSession(String sessionId) async {
    try {
      AppLogger.info('PracticeApi.resumeSession: $sessionId');

      final response = await _dioClient.post(
        ApiConstants.practiceSessionResume(sessionId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Resume session successful');
        return response.data;
      } else {
        throw ServerException(
          message: 'Failed to resume session',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Resume session error: ${e.message}');
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
