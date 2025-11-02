import 'package:dio/dio.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/utils/logger.dart';
import '../../models/ai_chat_model.dart';

/// AI Chat API
/// AI对话相关API接口
class AIChatApi {
  final DioClient _dioClient;

  AIChatApi(this._dioClient);

  /// Create a new chat session
  /// 创建新的聊天会话
  ///
  /// [request] - Create chat session request
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [ValidationException]
  Future<CreateChatSessionResponse> createSession(
    CreateChatSessionRequest request,
  ) async {
    try {
      AppLogger.info('AIChatApi.createSession: title=${request.title}');

      final response = await _dioClient.post(
        ApiConstants.chatSessions,
        data: request.toJson(),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        AppLogger.debug('Create chat session successful');
        return CreateChatSessionResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to create chat session',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Create chat session error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get user's chat sessions
  /// 获取用户的聊天会话列表
  ///
  /// [page] - Page number (starts from 1)
  /// [pageSize] - Items per page
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<ChatSessionListResponse> getSessions({
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      AppLogger.info('AIChatApi.getSessions: page=$page');

      final queryParams = <String, dynamic>{
        'skip': (page - 1) * pageSize,
        'limit': pageSize,
      };

      final response = await _dioClient.get(
        ApiConstants.chatSessions,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get chat sessions successful');
        return ChatSessionListResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get chat sessions',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get chat sessions error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get chat session by ID
  /// 根据ID获取聊天会话
  ///
  /// [sessionId] - Chat session ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<ChatSessionModel> getSession(String sessionId) async {
    try {
      AppLogger.info('AIChatApi.getSession: $sessionId');

      final response = await _dioClient.get(
        ApiConstants.chatSessionById(sessionId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get chat session successful');
        return ChatSessionModel.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get chat session',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get chat session error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Send a message in a chat session
  /// 在聊天会话中发送消息
  ///
  /// [sessionId] - Chat session ID
  /// [request] - Send message request
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [ValidationException]
  Future<SendMessageResponse> sendMessage(
    String sessionId,
    SendMessageRequest request,
  ) async {
    try {
      AppLogger.info('AIChatApi.sendMessage: sessionId=$sessionId');

      final response = await _dioClient.post(
        ApiConstants.chatSendMessage(sessionId),
        data: request.toJson(),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Send message successful');
        return SendMessageResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to send message',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Send message error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get messages from a chat session
  /// 获取聊天会话的消息列表
  ///
  /// [sessionId] - Chat session ID
  /// [page] - Page number (starts from 1)
  /// [pageSize] - Items per page
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<ChatMessageListResponse> getMessages({
    required String sessionId,
    int page = 1,
    int pageSize = 50,
  }) async {
    try {
      AppLogger.info('AIChatApi.getMessages: sessionId=$sessionId, page=$page');

      final queryParams = <String, dynamic>{
        'skip': (page - 1) * pageSize,
        'limit': pageSize,
      };

      final response = await _dioClient.get(
        ApiConstants.chatMessages(sessionId),
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get messages successful');
        return ChatMessageListResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get messages',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get messages error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Delete a chat session
  /// 删除聊天会话
  ///
  /// [sessionId] - Chat session ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<void> deleteSession(String sessionId) async {
    try {
      AppLogger.info('AIChatApi.deleteSession: $sessionId');

      final response = await _dioClient.delete(
        ApiConstants.chatSessionById(sessionId),
      );

      if (response.statusCode == 200 || response.statusCode == 204) {
        AppLogger.debug('Delete chat session successful');
      } else {
        throw ServerException(
          message: 'Failed to delete chat session',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Delete chat session error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Update chat session title
  /// 更新聊天会话标题
  ///
  /// [sessionId] - Chat session ID
  /// [title] - New title
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<void> updateSessionTitle(String sessionId, String title) async {
    try {
      AppLogger.info('AIChatApi.updateSessionTitle: $sessionId');

      final response = await _dioClient.patch(
        ApiConstants.chatSessionById(sessionId),
        data: {'title': title},
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Update session title successful');
      } else {
        throw ServerException(
          message: 'Failed to update session title',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Update session title error: ${e.message}');
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
