import 'package:dio/dio.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/utils/logger.dart';
import '../../models/user_model.dart';

/// Authentication API
/// 认证相关API接口
class AuthApi {
  final DioClient _dioClient;

  AuthApi(this._dioClient);

  /// Login
  /// 用户登录
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [ValidationException]
  Future<LoginResponse> login(LoginRequest request) async {
    try {
      AppLogger.info('AuthApi.login: ${request.username}');

      final response = await _dioClient.post(
        ApiConstants.login,
        data: request.toJson(),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Login successful');
        return LoginResponse.fromJson(response.data);
      } else {
        AppLogger.error('Login failed: ${response.statusCode}');
        throw ServerException(
          message: 'Login failed',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Login error: ${e.message}');
      throw _handleDioException(e);
    } catch (e) {
      AppLogger.error('Unexpected login error: $e');
      throw UnknownException(message: 'Unexpected error during login: $e');
    }
  }

  /// Register
  /// 用户注册
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [ValidationException]
  Future<LoginResponse> register(RegisterRequest request) async {
    try {
      AppLogger.info('AuthApi.register: ${request.username}');

      final response = await _dioClient.post(
        ApiConstants.register,
        data: request.toJson(),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        AppLogger.debug('Registration successful');
        return LoginResponse.fromJson(response.data);
      } else {
        AppLogger.error('Registration failed: ${response.statusCode}');
        throw ServerException(
          message: 'Registration failed',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Registration error: ${e.message}');
      throw _handleDioException(e);
    } catch (e) {
      AppLogger.error('Unexpected registration error: $e');
      throw UnknownException(message: 'Unexpected error during registration: $e');
    }
  }

  /// Get current user info
  /// 获取当前用户信息
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<UserModel> getCurrentUser() async {
    try {
      AppLogger.info('AuthApi.getCurrentUser');

      final response = await _dioClient.get(ApiConstants.userMe);

      if (response.statusCode == 200) {
        AppLogger.debug('Get current user successful');
        return UserModel.fromJson(response.data);
      } else {
        AppLogger.error('Get current user failed: ${response.statusCode}');
        throw ServerException(
          message: 'Failed to get user info',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get current user error: ${e.message}');
      throw _handleDioException(e);
    } catch (e) {
      AppLogger.error('Unexpected get user error: $e');
      throw UnknownException(message: 'Unexpected error getting user: $e');
    }
  }

  /// Logout
  /// 用户登出
  ///
  /// This is a client-side operation that clears the token
  Future<void> logout() async {
    try {
      AppLogger.info('AuthApi.logout');
      // Clear token from DioClient
      _dioClient.clearToken();
      AppLogger.debug('Logout successful');
    } catch (e) {
      AppLogger.error('Logout error: $e');
      throw UnknownException(message: 'Unexpected error during logout: $e');
    }
  }

  /// Handle Dio exceptions and convert to app exceptions
  Exception _handleDioException(DioException e) {
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
          return ValidationException(
            message: message,
            statusCode: statusCode,
          );
        case 401:
          return AuthenticationException(
            message: message,
            statusCode: statusCode,
          );
        case 403:
          return AuthorizationException(
            message: message,
            statusCode: statusCode,
          );
        case 404:
          return NotFoundException(
            message: message,
            statusCode: statusCode,
          );
        case 422:
          // Extract validation errors from response
          final errors = e.response?.data?['errors'];
          return ValidationException(
            message: errors != null ? errors.toString() : message,
            statusCode: statusCode,
          );
        default:
          if (statusCode >= 500) {
            return ServerException(
              message: message,
              statusCode: statusCode,
            );
          }
      }
    }

    return UnknownException(message: message);
  }
}
